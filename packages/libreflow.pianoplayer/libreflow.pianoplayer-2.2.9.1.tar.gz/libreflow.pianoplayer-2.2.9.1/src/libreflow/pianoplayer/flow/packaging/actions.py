import os
import shutil
import re
import glob
import smtplib
import ssl
from datetime import datetime
from email.message import EmailMessage
from kabaret import flow

from ...resources.icons import gui

from .package import PackageView


MAX_DELIVERY_COUNT = 1e3


class EmailSessionValue(flow.values.SessionValue):

    _action = flow.Parent()

    def revert_to_default(self):
        value = self.root().project().get_action_value_store().get_action_value(
            self._action.name(),
            self.name(),
        )
        self.set(value)


class EmailReceiverSessionValue(EmailSessionValue):

    DEFAULT_EDITOR = 'mapping'


class PackAction(flow.Action):

    ICON = ('icons.gui', 'package')

    package_name = flow.SessionParam('sources').ui(editable=False)
    content = flow.Child(PackageView).ui(expanded=True)

    _parent = flow.Parent()

    def get_buttons(self):
        return ['Create package', 'Cancel']

    def get_package_template(self):
        return self._parent.name()
    
    def get_start_oid(self):
        return self._parent.oid()
    
    def _ensure_package_folder(self, folder_name):
        if not self._parent.files.has_mapped_name(folder_name):
            add_action = self._parent.files.create_folder_action
            add_action.folder_name.set(folder_name)
            add_action.tracked.set(True)
            add_action.run('Create')
        
        return self._parent.files[folder_name]
    
    def run(self, button):
        if button == 'Cancel':
            return
        
        folder = self._ensure_package_folder(self.package_name.get())
        r = folder.create_working_copy()
        
        for f in self.content.mapped_items():
            if f.enabled.get():
                f.pack(r.get_path())


class CreateLayoutPackagesAction(flow.Action):
    '''
    This action allows to package folders into existing shots.

    It uses the following parameters in the current site:
      - `package_source_dir`: location of the folders to pack
      - `package_target_dir`: location where each folder will
      be moved after packing

    A folder is packed as a tracked folder. The target shot
    name is extracted performing a match between the folder
    name and the regular expression `shot_name_regex`. Thus,
    only folders with names matching this parameter will be
    available for packing.

    Each package is requested toward all sites whose names are
    provided in the `target_sites` param of the current site.

    {
        shotgrid_id,
        sequence,
        shot,
        sg_name,
        publish_comment,
        status,
        available,
        sources: [
            {
                path,
                sg_status
            }
        ]
    }
    '''

    ICON = ('icons.gui', 'package')

    shot_name_regex = flow.Param('^TS_(c\d{3})_(s\d{3})').ui(editable=False, hidden=True) # Used to validate ShotGrid shot names
    source_dir_name_pattern = flow.Param('^TS_{sequence_name}_{shot_name}.*').ui(editable=False, hidden=True) # Used to find shot source folders

    sg_task_filter    = flow.DictParam(dict(name='Pre-Comp', status='send'))
    target_sg_task    = flow.DictParam(dict(name='Pre-Comp', status='rs'))
    target_kitsu_task = flow.DictParam(dict(name='Compositing', status='INV'))

    email_receiver    = flow.SessionParam('', EmailReceiverSessionValue)
    email_subject     = flow.SessionParam('', EmailSessionValue)

    _film = flow.Parent()

    def __init__(self, parent, name):
        super(CreateLayoutPackagesAction, self).__init__(parent, name)
        self._shots_data = None
    
    def allow_context(self, context):
        return False
    
    def get_shots_data(self, refresh=False):
        if self._shots_data is None or refresh:
            self._shots_data = []
            site = self.root().project().get_current_site()
            sg_config = self.root().project().get_shotgrid_config()
            
            regex = self.shot_name_regex.get()
            layout_src_dir = site.package_layout_dir.get()

            task_filter = self.sg_task_filter.get()

            for sg_shot in sg_config.get_shots(task_filter['name'], task_filter['status']):
                sg_shot_name = sg_shot['name']
                m = re.search(regex, sg_shot_name, re.IGNORECASE)

                if m is not None:
                    sg_shot_id = sg_shot['id']
                    sequence_name = m.group(1).lower()
                    shot_name = m.group(2).lower()

                    layout_src_path = self.find_shot_source_dir(sequence_name, shot_name, layout_src_dir)
                    layout_src_size = self.get_dir_size(layout_src_path)
                    layout_status = sg_config.get_shot_task_status(sg_shot_id, 'Layout')

                    status = 'warning'
                    if layout_src_path is None: # layout files don't exist
                        status = 'error'
                    elif layout_status == 'apr': # layout is approved and files exist
                        status = 'valid'

                    self._shots_data.append({
                        'shotgrid_id': sg_shot_id,
                        'sequence': m.group(1).lower(),
                        'shot': m.group(2).lower(),
                        'sg_name': sg_shot_name,
                        'publish_comment': None,
                        'status': status,
                        'available': layout_status != 'na',
                        'layout_src_path': layout_src_path,
                        'layout_src_size': layout_src_size,
                        'layout_sg_status': layout_status,
                    })
        
        return self._shots_data
    
    def _ensure_package_revision(self, sequence_name, shot_name, dept_name, package_name):
        revision = None

        try:
            file_map = self.root().get_object(
                f'{self._film.oid()}/sequences/{sequence_name}/shots/{shot_name}/tasks/{dept_name}/files'
            )
        except:
            print(f'Packages :: TS_{sequence_name}_{shot_name} :: Shot does not exist in the project')
        else:
            if not file_map.has_folder(package_name):
                f = file_map.add_folder(package_name, tracked=True)
            else:
                f = file_map[package_name]
            
            revision = f.add_revision()
            f.ensure_last_revision_oid()
        
        return revision
    
    def _submit_upload(self, revision, do_upload=False):
        current_site = self.root().project().get_current_site()
        sites = self.root().project().get_working_sites()

        # Request revision for upload toward source site
        source_site = sites[revision.site.get()]
        
        if revision.get_sync_status(exchange=True) != 'Available':
            job = source_site.get_queue().submit_job(
                job_type='Upload',
                init_status='WAITING',
                emitter_oid=revision.oid(),
                user=self.root().project().get_user_name(),
                studio=source_site.name(),
            )

        # Request revision for download toward target sites
        for site_name in current_site.target_sites.get():
            try:
                site = sites[site_name]
            except flow.exceptions.MappedNameError:
                continue
            else:
                if revision.get_sync_status(site_name=site_name) != 'Available':
                    site.get_queue().submit_job(
                        job_type='Download',
                        init_status='WAITING',
                        emitter_oid=revision.oid(),
                        user=self.root().project().get_user_name(),
                        studio=site_name,
                    )
                    revision.set_sync_status('Requested', site_name=site_name)

        if do_upload and current_site.name() == source_site.name():
            self.root().project().get_sync_manager().process(job)
        
        return job.status.get()
    
    def find_shot_source_dir(self, sequence_name, shot_name, sources_dir):
        src_dir = None

        if os.path.exists(sources_dir):
            regex = self.source_dir_name_pattern.get().format(
                sequence_name=sequence_name,
                shot_name=shot_name
            )

            for dir_name in next(os.walk(sources_dir))[1]:
                if re.search(regex, dir_name, re.IGNORECASE) is not None:
                    src_dir = os.path.join(sources_dir, dir_name)
                    break
            
        return src_dir

    def get_dir_size(self, path):
        total = 0
        if path != None:
            for p in os.listdir(path):
                full_path = os.path.join(path, p)
                if os.path.isfile(full_path):
                    total += os.path.getsize(full_path)
                elif os.path.isdir(full_path):
                    total += self.get_dir_size(full_path)
        return total
    
    def _create_shot_package(self, shot_data, dept_name, package_name, source_paths, do_upload, dst_dir):
        sg_shot_name = shot_data['sg_name']
        sequence_name = shot_data['sequence']
        shot_name = shot_data['shot']

        # Create new revision for package
        r = self._ensure_package_revision(sequence_name, shot_name, dept_name, package_name)

        if r is not None:
            target_path = r.get_path()

            if os.path.exists(target_path):
                shutil.rmtree(target_path)
            
            # Copy the content of all source folders in target folder
            for source_path in source_paths:
                # Copy source files in package revision
                shutil.copytree(source_path, target_path, dirs_exist_ok=True)
            
            print(f'Packages :: {sg_shot_name}: Package created: {target_path}')
            
            # Submit revision upload
            upload = self._submit_upload(r, do_upload)
            print(f'Packages :: {sg_shot_name}: Package uploaded')

            # Copy sources to destination folder
            if dst_dir is not None:
                for source_path in source_paths:
                    dst_path = os.path.join(dst_dir, os.path.basename(source_path))

                    if not os.path.exists(dst_path):
                        shutil.copytree(source_path, dst_path)
                        print(f'Packages :: {sg_shot_name}: Source folder copied into {dst_path}')
                    else:
                        print(f'Packages :: {sg_shot_name}: Source folder already present in {dst_dir}')
            
            return [True, upload]
        else:
            return [False, None]

    def create_shot_packages(self, shot_data, do_upload, dst_dir):
        created = False
        layout_src_path = shot_data['layout_src_path']

        if layout_src_path is not None:
            created = self._create_shot_package(shot_data, 'misc', 'sources', [layout_src_path], do_upload, dst_dir)
        
        return created
    
    def update_statutes(self, shot_data):
        # Update SG status: ready to start
        sg_config = self.root().project().get_shotgrid_config()
        target_task = self.target_sg_task.get()
        sg_config.set_shot_task_status(shot_data['shotgrid_id'], target_task['name'], target_task['status'])

        # Update Kitsu status: inventory
        kitsu_config = self.root().project().kitsu_api()
        target_task = self.target_kitsu_task.get()
        kitsu_config.set_shot_task_status(shot_data['sequence'], shot_data['shot'], target_task['name'], target_task['status'])
    
    def create_packages(self, shots_data, do_upload=False):
        site = self.root().project().get_current_site()
        pkg_layout_dir = site.package_layout_dir.get()
        pkg_clean_dir = site.package_clean_dir.get()
        dst_dir = os.path.join(
            site.package_target_dir.get(),
            datetime.now().strftime('%y%m%d')
        )

        if os.path.exists(dst_dir):
            i = 2
            while os.path.exists(f'{dst_dir}-{i}') and i <= MAX_DELIVERY_COUNT:
                i += 1
            
            dst_dir = f'{dst_dir}-{i}'

        if pkg_layout_dir is None or pkg_clean_dir is None:
            print((
                'Packages :: Layout and clean package directories '
                'must be specified in the current site settings'
            ))
            return

        package_list = []

        for shot_data in shots_data:
            created = self.create_shot_packages(shot_data, do_upload, dst_dir)

            if created[0]:
                if created[1] != 'WAITING':
                    package_list.append({
                        'shot': shot_data['sg_name'],
                        'status': created[1],
                    })
                self.update_statutes(shot_data)
        
        if len(package_list) != 0:
            self.send_mail(package_list)
            print('Packages :: Mail sent!')

    def send_mail(self, package_list):
        delivered_count = 0
        error_count = 0

        email_sender = self.root().project().get_action_value_store().get_action_value(
            'create_packages',
            'email_sender',
        )
        email_password = self.root().project().get_action_value_store().get_action_value(
            'create_packages',
            'email_password',
        )
        self.email_receiver.revert_to_default()
        self.email_subject.revert_to_default()

        timestamp = datetime.now().strftime("%y%m%d")

        subject = self.email_subject.get().format(date=timestamp)
        body = '''
        <!DOCTYPE html>
        <html>
            <body>
                <p>Hello,<br>
                {user} have just made the following <b>{type}</b> delivery:</p>
                <table style="border-collapse: collapse;border-spacing: 0;">
        '''.format(user=self.root().project().get_user_name(), type='layout')

        # Add packages to <table>
        i = 0
        for package in package_list:
            i += 1
            if i % 2:
                tr = '''
                    <tr>
                        <td style="padding: 6px 12px;border: 1px solid #D9CED6;font-size: 18px;">{shot}</td>
                        <td style="padding: 6px 12px;border: 1px solid #D9CED6;font-size: 18px;">{status}</td>
                    </tr>
                '''.format(shot=package['shot'].upper(), status=package['status'])
                body = body + tr
            else:
                tr = '''
                    <tr>
                        <td style="padding: 6px 12px;border: 1px solid #D9CED6;background-color: #EEEEEE;font-size: 18px;">{shot}</td>
                        <td style="padding: 6px 12px;border: 1px solid #D9CED6;background-color: #EEEEEE;font-size: 18px;">{status}</td>
                    </tr>
                '''.format(shot=package['shot'].upper(), status=package['status'])
                body = body + tr
            
            if package['status'] == 'PROCESSED':
                delivered_count += 1
            elif package['status'] == 'ERROR':
                error_count += 1

        # Add the rest of the HTML content with total counts
        body = body + '''
                </table>
                <p>Total delivered: {delivered}/{total}</p>
                <p>Total errors: {error}</p>
            </body>
        </html>
        '''.format(delivered=delivered_count, total=len(package_list), error=error_count)

        em = EmailMessage()
        em['From'] = email_sender
        em['To'] = ", ".join(self.email_receiver.get())
        em['Subject'] = subject
        em.set_content(body, subtype='html')

        context = ssl.create_default_context()

        smtp_server = self.root().project().get_action_value_store().get_action_value(
            'create_packages',
            'smtp_server',
        )
        smtp_port = self.root().project().get_action_value_store().get_action_value(
            'create_packages',
            'smtp_port',
        )

        with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as smtp:
            smtp.login(email_sender, email_password)
            smtp.sendmail(email_sender, self.email_receiver.get(), em.as_string())
    
    def _fill_ui(self, ui):
        ui['custom_page'] = 'libreflow.pianoplayer.ui.packaging.CreateLayoutPackagesWidget'


class _SafeDict(dict):
    '''
    From https://stackoverflow.com/a/17215533
    '''
    def __missing__(self, key):
        return '{' + key + '}'


class AddPresetAction(flow.Action):

    ICON = ('icons.gui', 'plus-sign-in-a-black-circle')

    preset_name   = flow.SessionParam('').ui(label='Name')
    path_template = flow.SessionParam('')
    relative_path = flow.SessionParam().ui(editor='bool')
    optional      = flow.SessionParam().ui(editor='bool')

    _map = flow.Parent()

    def get_buttons(self):
        return ('Add', 'Cancel')
    
    def run(self, button):
        if button == 'Cancel':
            return
        
        p = self._map.add(self.preset_name.get())
        p.path_template.set(self.path_template.get())
        p.relative_path.set(self.relative_path.get())
        p.optional.set(self.optional.get())
        self._map.touch()


class PackageSourcePreset(flow.Object):

    path_template = flow.Param() # e.g., "{sequence}_{shot}*/MOVIES/{sequence}_{shot}_v??.mp4"
    relative_path = flow.BoolParam()
    optional      = flow.BoolParam()

    def find_path(self, **path_keywords):
        path_template = self.path_template.get().format_map(_SafeDict(path_keywords))

        if self.relative_path.get():
            root_dir = self.root().project().get_current_site().package_clean_dir.get()
            path_template = os.path.join(root_dir, path_template)
        
        paths = sorted(glob.glob(path_template))
        path = None

        if paths:
            path = paths[-1]
        
        return path
    
    def get_size(self, path):
        if path is None or os.path.isfile(path):
            return None
        elif os.path.isdir(path):
            return self.get_dir_size(path)

    def get_dir_size(self, path):
        total = 0
        for p in os.listdir(path):
            full_path = os.path.join(path, p)
            if os.path.isfile(full_path):
                total += os.path.getsize(full_path)
            elif os.path.isdir(full_path):
                total += self.get_dir_size(full_path)
        return total


class PackageSourcePresets(flow.Map):

    add_preset = flow.Child(AddPresetAction)

    @classmethod
    def mapped_type(cls):
        return PackageSourcePreset


class CreateCleanPackagesAction(flow.Action):
    """
    Creates clean-up packages
    """

    ICON = ('icons.gui', 'package')

    package_file_presets = flow.Child(PackageSourcePresets)

    sg_shot_name_regex   = flow.Param('^TS_(c\d{3})_(s\d{3})') # Used to validate ShotGrid shot names
    shot_filter          = flow.DictParam(dict(task='Pre-Comp', status='send'))
    shot_task            = flow.Param('Color Ink & Paint')

    package_name         = flow.Param('sources')
    package_department   = flow.Param('clean')
    target_kitsu_status  = flow.DictParam(dict(task='Reception', status='INV'))
    target_sg_status     = flow.DictParam(dict(task='Pre-Comp', status='rs'))

    delete_sources       = flow.BoolParam(False)

    _film                = flow.Parent()

    def __init__(self, parent, name):
        super(CreateCleanPackagesAction, self).__init__(parent, name)
        self._shots_data = None
    
    def allow_context(self, context):
        return False

    def package_file_names(self):
        """
        Returns the names of the package files
        """
        return self.package_file_presets.mapped_names()
    
    def shot_ids(self, force_update=False):
        return list(self.shots_data(force_update).keys())

    def shots_data(self, force_update=False):
        """
        Returns a dict describing the shots to create
        clean-up package for.

        The returned dict has the following layout:
        {
            <id>: {
                sg_id,
                sg_name,
                sequence_name,
                shot_name,
                sg_status,
                source_files: {
                    <name>: (path, size, optional)
                },
                status
            }
        }
        """
        if self._shots_data is None or force_update:
            self._shots_data = self._compute_shots_data()
        
        return self._shots_data
    
    def shot_data(self, id):
        return self.shots_data()[id]

    def create_shot_packages(self, shot_ids, do_upload=False):
        package_name = self.package_name.get()
        department = self.package_department.get()
        kitsu_status = self.target_kitsu_status.get()
        sg_status = self.target_sg_status.get()

        for shot_id in shot_ids:
            shot = self.shot_data(shot_id)
            created = self.create_shot_package(shot, department, package_name, do_upload)

            if created:
                self.update_statutes(shot, kitsu_status, sg_status)
                self.remove_shot(shot)

    def _compute_shots_data(self):
        shots_data = {}
        shot_filter = self.shot_filter.get()
        shot_task = self.shot_task.get()
        name_regex = self.sg_shot_name_regex.get()
        sg = self.root().project().get_shotgrid_config()

        sg_shots = sg.get_shots(shot_filter['task'], shot_filter['status'])

        for sg_shot in sg_shots:
            sg_shot_name = sg_shot['name']
            m = re.search(name_regex, sg_shot_name, re.IGNORECASE)

            if m is None:
                print("Clean-up packages :: Skip shot {}: invalid name".format(sg_shot_name))
                continue

            sequence_name = m.group(1).lower()
            shot_name     = m.group(2).lower()
            sg_shot_id    = sg_shot['id']

            # Get ShotGrid color status
            sg_status = sg.get_shot_task_status(sg_shot_id, shot_task)

            # Find package source files
            source_files = self.find_package_sources(sequence_name, shot_name)
            status = self.get_shot_status(sg_status, source_files)

            shots_data[sg_shot_id] = {
                'sg_id': sg_shot_id,
                'sg_name': sg_shot_name,
                'sequence_name': sequence_name,
                'shot_name': shot_name,
                'sg_status': sg_status,
                'source_files': source_files,
                'status': status
            }
        
        return shots_data

    def remove_shot(self, shot_data):
        if self._shots_data is not None:
            self._shots_data.pop(shot_data['sg_id'])
    
    def get_shot_status(self, sg_status, source_files):
        mandatory_files_exist = True
        all_files_exist = True
        status = 'valid'

        for path, size, optional in source_files.values():
            if path is None:
                all_files_exist = False
                
                if not optional:
                    mandatory_files_exist = False
                    break
        
        if not mandatory_files_exist:
            status = 'error'
        elif sg_status != 'apr' or not all_files_exist:
            status = 'warning'
        
        return status

    def find_package_sources(self, sequence_name, shot_name):
        sources = {}

        for preset in self.package_file_presets.mapped_items():
            path = preset.find_path(sequence=sequence_name, shot=shot_name)
            size = preset.get_size(path)
            sources[preset.name()] = (path, size, preset.optional.get())
        
        return sources

    def create_shot_package(self, shot_data, dept_name, package_name, do_upload):
        sg_shot_name = shot_data['sg_name']

        # Create new revision for package
        r = self._ensure_package_revision(shot_data['sequence_name'], shot_data['shot_name'], dept_name, package_name)

        if r is None:
            return False
        
        target_path = r.get_path()

        if os.path.exists(target_path):
            shutil.rmtree(target_path)
        
        # Copy source files in package
        for source_path, _, _ in shot_data['source_files'].values():
            if source_path is None:
                continue

            if os.path.isdir(source_path):
                shutil.copytree(source_path, target_path, dirs_exist_ok=True)
            else:
                shutil.copy2(source_path, target_path)
            
        print(f'Packages :: {sg_shot_name}: Package created: {target_path}')
        
        # Submit revision upload
        self._submit_upload(r, do_upload)
        print(f'Packages :: {sg_shot_name}: Package uploaded')

        if do_upload and self.delete_sources.get():
            print(f'Packages :: {sg_shot_name}: Remove package from current site')
            self._remove_revision(r)
            
        return True

    def update_statutes(self, shot_data, target_kitsu_status, target_sg_status):
        if target_sg_status:
            sg = self.root().project().get_shotgrid_config()
            sg.set_shot_task_status(shot_data['sg_id'], target_sg_status['task'], target_sg_status['status'])

        if target_kitsu_status:
            kitsu = self.root().project().kitsu_api()
            kitsu.set_shot_task_status(shot_data['sequence_name'], shot_data['shot_name'], target_kitsu_status['task'], target_kitsu_status['status'])

    def _ensure_package_revision(self, sequence_name, shot_name, dept_name, package_name):
        revision = None
        film_oid = self._film.oid()

        try:
            file_map = self.root().get_object(
                f'{film_oid}/sequences/{sequence_name}/shots/{shot_name}/tasks/{dept_name}/files'
            )
        except:
            print(f'Packages :: Shot {sequence_name} {shot_name} does not exist in the project')
        else:
            if not file_map.has_folder(package_name):
                f = file_map.add_folder(package_name, tracked=True)
            else:
                f = file_map[package_name]
            
            revision = f.add_revision()
            f.ensure_last_revision_oid()
        
        return revision
    
    def _submit_upload(self, revision, do_upload=False):
        current_site = self.root().project().get_current_site()
        sites = self.root().project().get_working_sites()

        # Request revision for upload toward source site
        source_site = sites[revision.site.get()]
        
        if revision.get_sync_status(exchange=True) != 'Available':
            job = source_site.get_queue().submit_job(
                job_type='Upload',
                init_status='WAITING',
                emitter_oid=revision.oid(),
                user=self.root().project().get_user_name(),
                studio=source_site.name(),
            )

        # Request revision for download toward target sites
        for site_name in current_site.target_sites.get():
            try:
                site = sites[site_name]
            except flow.exceptions.MappedNameError:
                continue
            else:
                if revision.get_sync_status(site_name=site_name) != 'Available':
                    site.get_queue().submit_job(
                        job_type='Download',
                        init_status='WAITING',
                        emitter_oid=revision.oid(),
                        user=self.root().project().get_user_name(),
                        studio=site_name,
                    )
                    revision.set_sync_status('Requested', site_name=site_name)

        if do_upload and current_site.name() == source_site.name():
            self.root().project().get_sync_manager().process(job)

    def _remove_revision(self, revision):
        path = revision.get_path()

        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
        
        revision.set_sync_status('NotAvailable')

    def _fill_ui(self, ui):
        ui['custom_page'] = 'libreflow.pianoplayer.ui.packaging.CreateCleanPackagesWidget'
