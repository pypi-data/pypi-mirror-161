import os
import shutil
import fileseq
import re
import sys
from fnmatch import fnmatch
from collections import defaultdict
from kabaret import flow


MAX_ITEM_COUNT = 1e3


class UnpackTargetFile(flow.Object):

    path_template = flow.Param()
    package_department = flow.Param()
    package_name = flow.Param()
    file_department = flow.Param() # None means unset
    file_name = flow.Param() # None means unset
    file_relpath = flow.Param() # Used by folder targets only
    file_basename = flow.Param()
    kitsu_target_statutes = flow.DictParam(dict)
    sg_target_statutes = flow.DictParam(dict)
    max_match_count = flow.IntParam(sys.maxsize)
    to_ignore = flow.BoolParam(False)


class AddTargetFile(flow.Action):

    ICON = ('icons.gui', 'plus-sign-in-a-black-circle')

    path_template = flow.SessionParam('')
    package_department = flow.SessionParam('')
    package_name = flow.SessionParam('')
    file_department = flow.SessionParam('')
    file_name = flow.SessionParam('')
    file_relpath = flow.SessionParam('')
    file_basename = flow.SessionParam('')
    max_match_count = flow.SessionParam(-1)
    to_ignore = flow.SessionParam(False).ui(editor='bool')

    _map = flow.Parent()

    def get_buttons(self):
        return ['Add', 'Cancel']
    
    def allow_context(self, context):
        return context and context.endswith('.inline')
    
    def run(self, button):
        if button == 'Cancel':
            return
        
        max_match_count = self.max_match_count.get()
        if max_match_count < 0:
            max_match_count = sys.maxsize
        
        self._map.add_target_file(
            self.path_template.get(),
            self.package_department.get(),
            self.package_name.get(),
            self.file_department.get() or None,
            self.file_name.get() or None,
            self.file_relpath.get() or None,
            self.file_basename.get() or None,
            max_match_count,
            self.to_ignore.get(),
        )


class UnpackTargetFiles(flow.Map):

    add_action = flow.Child(AddTargetFile).ui(label='Add target file')

    @classmethod
    def mapped_type(cls):
        return UnpackTargetFile
    
    def columns(self):
        return ['Package', 'Template', 'Target']
    
    def add_target_file(self, path_template, pkg_department, pkg_name, file_department, file_name, relpath, basename, max_match_count, to_ignore=False):
        i = len(self)
        mapped_names = self.mapped_names()

        while f'f{i:04}' in mapped_names and i < MAX_ITEM_COUNT:
            i += 1

        f = self.add(f'f{i:04}')
        f.path_template.set(path_template)
        f.package_department.set(pkg_department)
        f.package_name.set(pkg_name)
        f.file_department.set(file_department)
        f.file_name.set(file_name)
        f.max_match_count.set(max_match_count)
        f.to_ignore.set(to_ignore)
        f.file_relpath.set(relpath)
        f.file_basename.set(basename)

        self.touch()
    
    def to_dict(self):
        '''
        {
            (pkg_name, pkg_dept): [
                {
                    path_template,
                    file_name,
                    department,
                }
            ]
        }
        '''
        d = defaultdict(list)
        for item in self.mapped_items():
            key = (item.package_name.get(), item.package_department.get())
            d[key].append({
                'mapped_name': item.name(),
                'path_template': item.path_template.get(),
                'file_name': item.file_name.get() or None,
                'department': item.file_department.get() or None,
                'relpath': item.file_relpath.get(),
                'basename': item.file_basename.get(),
                'max_match_count': item.max_match_count.get(),
                'to_ignore': item.to_ignore.get(),
                'kitsu_target_statutes': item.kitsu_target_statutes.get(),
                'sg_target_statutes': item.sg_target_statutes.get(),
            })
        
        return dict(d)
    
    def _fill_row_cells(self, row, item):
        row['Package'] = f'{item.package_department.get()}/{item.package_name.get()}'
        row['Template'] = item.path_template.get()

        if item.to_ignore.get():
            row['Target'] = 'ignored'
        else:
            row['Target'] = f'{item.file_department.get()}/{item.file_name.get()}'


class SafeDict(dict):
    '''
    From https://stackoverflow.com/a/17215533
    '''
    def __missing__(self, key):
        return '{' + key + '}'


def union(lst0, lst1):
    print(lst0, lst1)
    result_list = list(
        set().union(lst0, lst1)
    )
    return result_list


class UnpackSourcePackagesAction(flow.Action):

    target_files = flow.Child(UnpackTargetFiles)
    kitsu_shot_filter   = flow.DictParam({})

    target_kitsu_status = flow.DictParam({})
    target_sg_status    = flow.DictParam({})

    _film = flow.Parent()

    def __init__(self, parent, name):
        super(UnpackSourcePackagesAction, self).__init__(parent, name)
        self._shots_data = None
        self._targets_cache = None

    def get_package_infos(self):
        return self.target_files.to_dict()

    def shots_count(self, force_update=False):
        return len(list(self._shots_data.keys()))

    def shot_ids(self, force_update=False):
        if self._shots_data is None or force_update:
            self._shots_data = self._compute_shots_data()

        return list(self._shots_data.keys())

    def get_shot(self, id):
        self.shot_ids()
        return self._shots_data[id]

    def get_package(self, shot_id, id):
        shot = self.get_shot(shot_id)
        return shot['packages'][id]

    def get_match(self, shot_id, package_id, id):
        package = self.get_package(shot_id, package_id)
        return package['matches'][id]

    def get_targets(self, force_update=False):
        if self._targets_cache is None or force_update:
            self._targets_cache = []

            for target_file in self.target_files.mapped_items():
                if target_file.to_ignore.get() == False:
                    preset = target_file.file_department.get() + "/" + target_file.file_name.get()
                    if preset in self._targets_cache:
                        continue
                    self._targets_cache.append(preset)
        
        return self._targets_cache

    def update_target(self, shot_id, package_id, match_id, target_str, relpath):
        target = self.parse_target_str(target_str, relpath)
        m = self.get_match(shot_id, package_id, match_id)

        if target is not None:
            m['department'], m['name'], relpath = target
            m['undefined'] = False
            m['to_ignore'] = (target == (None, None, relpath))

            if m['name'] is not None and relpath is None and os.path.splitext(m['name'])[1] == '':
                # Relative path undefined and target is a folder: use
                # file's relative path in source package
                m['relpath'] = m['file_label']
            else:
                m['relpath'] = relpath
        else:
            m['undefined'] = True
            m['to_ignore'] = False
    
    def shot_is_valid(self, shot_id):
        shot_data = self.get_shot(shot_id)
        valid = True
        for pkg_id in shot_data['packages']:
            if not self.package_is_valid(shot_id, pkg_id):
                valid = False
                break
        
        return valid
    
    def package_is_valid(self, shot_id, package_id):
        pkg = self.get_package(shot_id, package_id)
        valid = True

        for match in pkg['matches']:
            if match['undefined']:
                valid = False
                break
        
        return valid and len(pkg['matches']) > 0

    @staticmethod
    def parse_target_str(target_str, relpath):
        '''
        Returns the target as a tuple (department, name, relative_path)
        corresponding to the string `target_str`, or None if the string
        couldn't be parsed.
        '''
        target = None

        if target_str == '-':
            target = (None, None, relpath)
        else:
            while target_str.startswith('/'): target_str = target_str[1:]
            while target_str.endswith('/'): target_str = target_str[:-1]
            target_fields = tuple(target_str.split('/', 2))
            target_len = len(target_fields)

            if target_len >= 2:
                target_dept = target_fields[0]
                target_name = target_fields[1]
                target_relpath = None

                if target_len >= 3:
                    target_relpath = target_fields[2]
                
                target = (target_dept, target_name, target_relpath)
        
        return target

    def _compute_shots_data(self):
        kitsu_api = self.root().project().kitsu_api()
        data = {}
        package_infos = self.get_package_infos()
        
        for sequence_name, shot_name in sorted(kitsu_api.get_shots(self.kitsu_shot_filter.get())):
            shot_data = {'sequence': sequence_name, 'shot': shot_name}
            packages_data = {}

            for (package_name, package_dept), target_files in package_infos.items():
                package = self._get_package_revision(sequence_name, shot_name, package_dept, package_name)

                if package is not None:
                    package_path = package.get_path()
                    package_data = {
                        'name': package_name,
                        'department': package_dept,
                        'revision': package.name(),
                        'path': package_path,
                    }
                    files_data = []
                    file_indices_per_target = defaultdict(list)
                    file_max_count_per_target = {}
                    i = 0
                    match_conflict_count = 0

                    # Save file count limits of targets
                    for target_file in target_files:
                        file_max_count_per_target[target_file['mapped_name']] = target_file['max_match_count']

                    for file_label, file_sequence in self._list_package_files(package_path):
                        file_data = dict.fromkeys(['name', 'department', 'relpath'])
                        file_data['undefined'] = True
                        file_data['to_ignore'] = False
                        file_data['kitsu_target_statutes'] = {}
                        file_data['sg_target_statutes'] = {}
                        file_data['warning'] = ''
                        file_data['conflict_group'] = 0

                        # Search for the first preset matching the found file/sequence/folder
                        for target_file in target_files:
                            if self._match(file_label, target_file['path_template'], sequence=sequence_name, shot=shot_name):
                                relpath = target_file['relpath']
                                basename = target_file['basename']

                                # If the matched file is not to be ignored and the target is a folder
                                if not target_file['to_ignore'] and '.' not in target_file['file_name']:
                                    parent_folder = os.path.basename(
                                        os.path.dirname(file_label)
                                    )
                                    parent_folder = parent_folder.lower()

                                    if relpath is None:
                                        relpath = os.path.dirname(file_label)
                                    else:
                                        relpath = self._format(
                                            relpath,
                                            film=self._film.name(),
                                            sequence=sequence_name,
                                            shot=shot_name,
                                            parent_folder=parent_folder,
                                        )
                                    if basename is None:
                                        basename = os.path.basename(file_label)
                                    else:
                                        basename = self._format(
                                            basename,
                                            film=self._film.name(),
                                            sequence=sequence_name,
                                            shot=shot_name,
                                            parent_folder=parent_folder,
                                        )
                                    
                                    file_count = len(file_sequence)
                                    if file_count > 1:
                                        relpath = self._conform_file_sequence_relpath(relpath, file_label, basename, file_count)
                                    else:
                                        relpath = os.path.join(relpath, basename).replace('\\', '/')
                                
                                file_data.update({
                                    'name': target_file['file_name'],
                                    'department': target_file['department'],
                                    'relpath': relpath,
                                    'undefined': False,
                                    'to_ignore': target_file['to_ignore'],
                                    'kitsu_target_statutes': target_file['kitsu_target_statutes'],
                                    'sg_target_statutes': target_file['sg_target_statutes'],
                                })

                                file_indices_per_target[target_file['mapped_name']].append(i)

                                break
                        
                        file_data['file_sequence'] = file_sequence
                        file_data['file_label'] = file_label
                        files_data.append(file_data)

                        i += 1
                    
                    # Make the file targets undefined if the number of matches exceeds the target's match limit
                    for target_file in target_files:
                        target_key = target_file['mapped_name']
                        limit = file_max_count_per_target[target_key]
                        file_indices = file_indices_per_target[target_key]

                        if len(file_indices) > limit:
                            match_conflict_count += 1
                            files_data[file_indices[0]]['conflict_group'] = match_conflict_count
                            files_data[file_indices[0]]['warning'] = 'Match conflict'
                            for i in file_indices[1:]:
                                if not files_data[i]['to_ignore']:
                                    files_data[i]['conflict_group'] = match_conflict_count
                                    files_data[i]['undefined'] = True
                                    files_data[i]['warning'] = 'Match conflict'
                                    files_data[i].update(
                                        dict.fromkeys(['name', 'department', 'relpath'])
                                    )
                
                    package_data['matches'] = files_data
                    package_data['target_files'] = target_files # Add list of available target files
                    packages_data[f'{package_dept}_{package_name}'] = package_data
                else:
                    # Package not created
                    self.root().session().log_warning('')
            
            shot_data['packages'] = packages_data
            data[f'{sequence_name}_{shot_name}'] = shot_data
        
        return data
    
    def _conform_file_sequence_relpath(self, relative_path, sequence_format, target_prefix, length):
        relative_path = relative_path.replace('\\', '/')
        dirname = os.path.basename(relative_path)
        split = sequence_format.split('.')
        target_prefix = split[0]
        ext = split[-1]
        
        # If the provided formatted name is invalid or the
        # basename isn't equal to the parent folder name
        if re.match(r'.*\.\d+-\d+(#+|@+)\..*', sequence_format) is None or (dirname and dirname != target_prefix):
            target_prefix = dirname
        relpath = f'{relative_path}/{target_prefix}.{1:04}-{length:04}#.{ext}'
        
        return relpath
    
    def unpack(self, shot_ids):
        target_kitsu_status = self.target_kitsu_status.get()
        target_sg_status = self.target_sg_status.get()
        
        for shot_id in shot_ids:
            if not self.shot_is_valid(shot_id):
                continue
            
            shot_data = self.get_shot(shot_id).copy()
            sequence_name = shot_data['sequence']
            shot_name = shot_data['shot']
            animatic_path = None
            kitsu_target_statutes = {}
            sg_target_statutes = {}

            for package_id, package_data in shot_data['packages'].items():
                print(f'Unpacking :: Unpack package {sequence_name}/{shot_name}/{package_data["department"]}/{package_data["name"]}/{package_data["revision"]}')
                matches = defaultdict(list)

                for match in package_data['matches']:
                    if match['to_ignore']:
                        continue

                    match_key = (match['department'], match['name'])
                    matches[match_key].append((match['file_sequence'], match['file_label'], match['relpath']))
                    kitsu_target_statutes.update(match['kitsu_target_statutes'])
                    sg_target_statutes.update(match['sg_target_statutes'])
                
                for match, file_sequences in matches.items():
                    department, target_name = match

                    if '.' not in target_name: # Target is a folder
                        dst_path = self._unpack_into_folder(package_data['path'], file_sequences, sequence_name, shot_name, department, target_name)
                    else:
                        # Unpack the first file of the first sequence
                        src_path = file_sequences[0][0][0]
                        dst_path = self._unpack_into_file(package_data['path'], src_path, sequence_name, shot_name, department, target_name)
                        
                        if target_name == 'animatic.mp4': # TODO: store animatic name in package data ?
                            animatic_path = dst_path
                
                self._save_json(sequence_name, shot_name, package_data['department'], [])
            
            if target_sg_status:
                self._update_shotgrid_status(sequence_name, shot_name, target_sg_status['task'], target_sg_status['status'])
            if target_kitsu_status:
                self._update_kitsu_status(
                    sequence_name,
                    shot_name,
                    target_kitsu_status['task'],
                    target_kitsu_status['status'],
                    animatic_path
                )
            
            for task, status in sg_target_statutes.items():
                self._update_shotgrid_status(sequence_name, shot_name, task, status)
            for task, status in kitsu_target_statutes.items():
                self._update_kitsu_status(sequence_name, shot_name, task, status, animatic_path)
            
            self._shots_data.pop(shot_id)
    
    def _get_package_revision(self, sequence_name, shot_name, dept_name, package_name):
        r = None
        film_oid = self._film.oid()
        try:
            package_folder = self.root().get_object(
                f'{film_oid}/sequences/{sequence_name}/shots/{shot_name}/tasks/{dept_name}/files/{package_name}'
            )
        except:
            pass
        else:
            r = package_folder.get_head_revision()
        
        return r
    
    def _list_package_files(self, package_path):
        def path_in_package(package_path, file_path):
            relpath = os.path.relpath(file_path, package_path)
            return relpath.replace('\\', '/')
        
        def get_paths(root):
            paths = []
            file_sequences = fileseq.findSequencesOnDisk(root)

            for file_sequence in file_sequences:
                file_count = len(file_sequence)

                if file_count > 0:
                    if file_count > 1:
                        file_label = path_in_package(
                            package_path,
                            os.path.join(file_sequence.dirname(), file_sequence.format())
                        )
                    else:
                        file_label = path_in_package(package_path, file_sequence.index(0))
                    
                    paths.append((
                        file_label,
                        [path_in_package(package_path, f) for f in file_sequence]
                    ))
            
            return paths
        
        paths = get_paths(package_path)

        for root, dirs, _ in os.walk(package_path):
            for d in dirs:
                paths.extend(
                    get_paths(os.path.join(root, d))
                )
        
        return paths
    
    def _format(self, string, **keywords):
        '''
        Does not evaluate formatting keywords in `string`
        not provided in `keywords`.
        '''
        return string.format_map(SafeDict(keywords))

    def _match(self, path, template, **keywords):
        '''
        ...
        '''
        template = self._format(template, **keywords)
        return fnmatch(path, template)
    
    def _unpack_into_file(self, package_path, source_file_path, sequence_name, shot_name, dept_name, file_name):
        film_oid = self._film.oid()
        revision_path = None

        try:
            file_map = self.root().get_object(
                f'{film_oid}/sequences/{sequence_name}/shots/{shot_name}/tasks/{dept_name}/files'
            )
        except:
            pass
        else:
            name, ext = file_name.rsplit('.', 1)

            if file_map.has_file(name, ext):
                f = file_map[f'{name}_{ext}']
            else:
                f = file_map.add_file(name, ext, tracked=True)
            
            r = self._create_revision(f)
            revision_path = r.get_path()
            revision_name = r.name()

            # Unpack
            print('Unpacking :: \t', source_file_path, f'-> {dept_name}/{file_name}/{revision_name}/{os.path.basename(revision_path)}')
            shutil.copy2(os.path.join(package_path, source_file_path), revision_path)
            # Upload
            self._upload_revision(r)
        
        return revision_path
    
    def _unpack_into_folder(self, package_path, file_sequences, sequence_name, shot_name, dept_name, folder_name):
        film_oid = self._film.oid()
        revision_path = None

        try:
            file_map = self.root().get_object(
                f'{film_oid}/sequences/{sequence_name}/shots/{shot_name}/tasks/{dept_name}/files'
            )
        except:
            pass
        else:
            if file_map.has_folder(folder_name):
                f = file_map[folder_name]
            else:
                f = file_map.add_folder(folder_name, tracked=True)
            
            r = self._create_revision(f)
            revision_path = r.get_path()
            revision_name = r.name()

            for file_paths, file_label, relpath in file_sequences:
                print('Unpacking :: \t', file_label, f'-> {dept_name}/{folder_name}/{revision_name}/{relpath}')
                sequence_dir = os.path.join(revision_path, os.path.dirname(relpath))

                if not os.path.exists(sequence_dir):
                    os.makedirs(sequence_dir)
                
                updated_paths = self._update_sequence_paths(file_paths, relpath)
                
                for i in range(len(file_paths)):
                    shutil.copy2(
                        os.path.join(package_path, file_paths[i]),
                        os.path.join(revision_path, updated_paths[i])
                    )

            self._upload_revision(r)

        return revision_path

    def _update_sequence_paths(self, file_sequence, relpath):
        if len(file_sequence) <= 1:
            return [relpath]
        
        s = fileseq.FileSequence(relpath)
        updated_paths = [
            s.frame(i) for i in range(1, len(file_sequence) + 1)
        ]

        return updated_paths
    
    def _save_json(self, sequence_name, shot_name, department, files_data):
        pass

    def _update_kitsu_status(self, sequence_name, shot_name, task_name, task_status, animatic_path=None):
        kitsu_api = self.root().project().kitsu_api()

        if animatic_path is not None:
            kitsu_api.upload_shot_preview(sequence_name, shot_name, task_name, task_status, animatic_path)
        else:
            kitsu_api.set_shot_task_status(sequence_name, shot_name, task_name, task_status)

    def _update_shotgrid_status(self, sequence_name, shot_name, step_name, status):
        shot = self.root().get_object(f'{self._film.oid()}/sequences/{sequence_name}/shots/{shot_name}')
        sg_config = self.root().project().get_shotgrid_config()
        sg_config.set_shot_task_status(shot.shotgrid_id.get(), step_name, status)

    def _create_revision(self, f):
        r = f.add_revision()
        revision_path = r.get_path()
        f.last_revision_oid.set(r.oid())
        os.makedirs(os.path.dirname(revision_path), exist_ok=True)

        return r

    def _upload_revision(self, revision):
        current_site = self.root().project().get_current_site()
        job = current_site.get_queue().submit_job(
            job_type='Upload',
            init_status='WAITING',
            emitter_oid=revision.oid(),
            user=self.root().project().get_user_name(),
            studio=current_site.name(),
        )

        self.root().project().get_sync_manager().process(job)

    def _fill_ui(self, ui):
        ui['custom_page'] = 'libreflow.pianoplayer.ui.unpacking.UnpackSourcePackagesWidget'


class UnpackLayoutPackagesAction(UnpackSourcePackagesAction):

    def allow_context(self, context):
        return False

    def _update_kitsu_status(self, sequence_name, shot_name, task_name, task_status, animatic_path=None):
        super(UnpackLayoutPackagesAction, self)._update_kitsu_status(sequence_name, shot_name, task_name, task_status, animatic_path)
        kitsu = self.root().project().kitsu_api()
        sg = self.root().project().get_shotgrid_config()

        if kitsu.get_shot_task_status_name(sequence_name, shot_name, 'Compositing') == 'Todo':
            shot = self._film.sequences[sequence_name].shots[shot_name]
            comment = sg.get_shot_comp_briefing(shot.shotgrid_id.get())
            
            if comment is not None:
                comment = comment.strip('"')
            
            kitsu.set_shot_task_status(sequence_name, shot_name, 'Compositing', 'Todo', comment or 'No comment')


class UnpackCleanPackagesAction(UnpackSourcePackagesAction):

    def allow_context(self, context):
        return False
