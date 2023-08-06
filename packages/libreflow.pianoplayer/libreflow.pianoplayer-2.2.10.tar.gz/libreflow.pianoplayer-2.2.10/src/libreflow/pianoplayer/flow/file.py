import pathlib
import os
import re
import fileseq
from collections import defaultdict
from kabaret import flow

from libreflow.baseflow.file import (
    CreateFileAction       as BaseCreateFileAction,
    CreateFolderAction     as BaseCreateFolderAction,
    FileSystemMap          as BaseFileSystemMap,
    TrackedFile            as BaseTrackedFile,
    TrackedFolder          as BaseTrackedFolder,
    GenericRunAction       as BaseGenericRunAction,
)
from libreflow.utils.flow import get_contextual_dict


class RevisionsMultiChoiceValue(flow.values.MultiChoiceValue):

    _file = flow.Parent(2)

    def choices(self):
        if self._file is not None:
            return sorted(self._file.get_revision_names(sync_status='Available', published_only=True), reverse=True)
        else:
            return ''

    def revert_to_default(self):
        if self._file is None or self._file.is_empty():
            self.set('')
            return

        revision = self._file.get_head_revision(sync_status='Available')
        revision_name = ''
        
        if revision is None:
            choices = self.choices()
            if choices:
                revision_name = choices[0]
        else:
            revision_name = revision.name()
        
        self.set(revision_name)
    
    def _fill_ui(self, ui):
        super(RevisionsMultiChoiceValue, self)._fill_ui(ui)
        if self._file is None or self._file.is_empty(on_current_site=True):
            ui['hidden'] = True


class AnimaticRevisionsMultiChoiceValue(RevisionsMultiChoiceValue):

    _shot = flow.Parent(6)

    def __init__(self, parent, name):
        super(AnimaticRevisionsMultiChoiceValue, self).__init__(parent, name)
        self._file = None
        if self._shot.tasks['misc'].files.has_mapped_name('animatic_mp4'):
            self._file = self._shot.tasks['misc'].files['animatic_mp4']
    
    def revert_to_default(self):
        self.set([])


class CreateFileAction(BaseCreateFileAction):

    def run(self, button):
        if button == 'Cancel':
            return

        name, extension = self.file_name.get(), self.file_format.get()

        if self._files.has_file(name, extension):
            self._warn((
                f'File {name}.{extension} already exists. '
                'Please choose another name.'
            ))
            return self.get_result(close=False)
        
        # Create a file with the default path format this
        # project is supposed to provide
        self._files.add_file(
            name,
            extension=extension,
            base_name=name,
            display_name=f'{name}.{extension}',
            tracked=self.tracked.get(),
        )
        self._files.touch()


class CreateFolderAction(BaseCreateFolderAction):

    def run(self, button):
        if button == 'Cancel':
            return
        
        name = self.folder_name.get()

        if self._files.has_folder(name):
            self._warn((
                f'Folder {name} already exists. '
                'Please choose another name.'
            ))
            return self.get_result(close=False)
        
        # Create a folder with the default path format this
        # project is supposed to provide
        self._files.add_folder(
            name,
            base_name=name,
            display_name=name,
            tracked=self.tracked.get(),
        )
        self._files.touch()


class AbstractRVOption(BaseGenericRunAction):
    """
    Abstract run action which instantiate an RV runner,
    with its default version.
    """
    def runner_name_and_tags(self):
        return 'RV', []
    
    def get_version(self, button):
        return None


class CompareWithAnimaticAction(AbstractRVOption):

    ICON = ('icons.libreflow', 'compare-previews')

    _file = flow.Parent()
    _shot = flow.Parent(5)
    _animatic_path = flow.Computed(cached=True)

    @classmethod
    def supported_extensions(cls):
        return ["mp4","mov"]

    def allow_context(self, context):
        return (
            context 
            and self._file.format.get() in self.supported_extensions()
        )

    def needs_dialog(self):
        self._animatic_path.touch()

        return (
            self._animatic_path.get() is None
        )
    
    def get_buttons(self):
        if self._animatic_path.get() is None:
            self.message.set('<h2>This shot has no animatic.</h2>')
        
        return ['Close']

    def compute_child_value(self, child_value):
        if child_value is self._animatic_path:
            self._animatic_path.set(
                self._get_last_revision_path('misc', 'animatic.mp4')
            )
    
    def extra_argv(self):
        return [
            '-wipe', '-autoRetime', '0',
            self._file.get_head_revision().get_path(),
            '[', '-volume', '0', self._animatic_path.get(), ']'
        ]

    def run(self, button):
        if button == 'Close':
            return
        else:
            super(CompareWithAnimaticAction, self).run(button)

    def _get_last_revision_path(self, task_name, file_name):
        path = None

        if self._shot.tasks.has_mapped_name(task_name):
            task = self._shot.tasks[task_name]
            name, ext = file_name.rsplit('.', 1)

            if task.files.has_file(name, ext):
                f = task.files[f'{name}_{ext}']
                r = f.get_head_revision()

                if r is not None and r.get_sync_status() == "Available":
                    path = r.get_path()

        return path


class CompareInRVAction(AbstractRVOption):
    ICON = ('icons.libreflow', 'compare-previews')

    _file = flow.Parent()
    _shot = flow.Parent(5)
    revisions = flow.Param([], RevisionsMultiChoiceValue)
    antc_revisions = flow.Param([], AnimaticRevisionsMultiChoiceValue).ui(label="Animatic Revisions")
   
    @classmethod
    def supported_extensions(cls):
        return ["mp4","mov"]

    def allow_context(self, context):
        return (
            context 
            and self._file.format.get() in self.supported_extensions()
            and len(self._file.get_revision_names(sync_status='Available', published_only=True)) >= 2 
        )

    def needs_dialog(self):
        return True

    def extra_argv(self):
        return ['-autoRetime', '0', '-layout', 'column', '-view', 'defaultLayout'] + self._revisions
       
    def get_buttons(self):
        if self._file.is_empty() == True or len(self._file.get_revision_names(sync_status='Available', published_only=True)) == 0:
            self.message.set('<h3>This file has no revision</h3>')
            return ['Cancel']
        else:
            self.message.set('<h3>Choose revisions to compare</h3>')
            self.revisions.set([self.revisions.choices()[0], self.revisions.choices()[1]])
            self.antc_revisions.revert_to_default()
            return ['Open', 'Cancel']
  
    def run(self, button):
        if button == "Cancel":
            return

        self._revisions = []

        for revision in self.revisions.get():
            if self._revisions == []:
                self._revisions += [self._file.get_revision(revision).get_path()]
                continue
            self._revisions += ['[', '-volume', '0', self._file.get_revision(revision).get_path(), ']']
        
        if self._shot.tasks['misc'].files.has_mapped_name('animatic_mp4'):
            for antc_revision in self.antc_revisions.get():
                self._revisions += ['[', '-volume', '0', self._shot.tasks['misc'].files['animatic_mp4'].get_revision(antc_revision).get_path(), ']']

        result = super(CompareInRVAction, self).run(button)
        return self.get_result(close=True)


class OpenAnimationLayers(AbstractRVOption):
    """
    Opens the set of animation layers contained in a folder
    named `layers`, in the `clean` task.
    """
    ICON = ('icons.gui', 'anim-layers')

    _layers_paths = flow.Computed(cached=True)

    _folder = flow.Parent()
    _task   = flow.Parent(3)

    def needs_dialog(self):
        self._layers_paths.touch()
        return not bool(self._layers_paths.get())
    
    def allow_context(self, context):
        return (
            context
            and self._task.name() == 'clean'
            and self._folder.name() == 'layers'
        )
    
    def get_buttons(self):
        if not self._layers_paths.get():
            self.message.set(
                '<h2>This folder has no animation layers.</h2>'
            )
        
        return ['Close']

    def extra_argv(self):
        paths = []
        for col_path, line_path in self._layers_paths.get():
            if line_path is not None:
                paths.append(line_path)
            if col_path is not None:
                paths.append(col_path)
        
        return ['-bg', 'checker', '-over'] + paths

    def compute_child_value(self, child_value):
        if child_value is self._layers_paths:
            self._layers_paths.set(self._get_layers_paths())
    
    def run(self, button):
        if button == 'Close':
            return
        else:
            super(OpenAnimationLayers, self).run(button)
    
    def _get_layers_paths(self):
        paths = {}
        r = self._folder.get_head_revision()

        if r is not None:
            layers_folder = r.get_path()

            paths = defaultdict(lambda: [None, None])
            for dir_name in os.listdir(layers_folder):
                dir_path = os.path.join(layers_folder, dir_name)
                m = re.match('(.*)_(col|color)$', dir_name, re.IGNORECASE)
                index = 0
                if m is None:
                    m = re.match('(.*)_(line)$', dir_name, re.IGNORECASE)
                    index = 1
                    if m is None:
                        continue
                
                sequences = fileseq.findSequencesOnDisk(dir_path)
                if sequences:
                    seq_format = sequences[0].format(template='{basename}{padding}{extension}')
                    paths[m.group(1)][index] = os.path.join(dir_path, seq_format)

        return sorted(paths.values())


class TrackedFile(BaseTrackedFile):

    with flow.group('Advanced'):
        compare_rv = flow.Child(CompareInRVAction).ui(label="Compare in RV")
        compare_comp_antc = flow.Child(CompareWithAnimaticAction).ui(label='Compare with animatic')


class TrackedFolder(BaseTrackedFolder):
    
    with flow.group('Advanced'):
        open_anim_layers = flow.Child(OpenAnimationLayers).ui(label='Open animation layers')


class FileSystemMap(BaseFileSystemMap):
    
    def add_file(self, name, extension, display_name=None, base_name=None, tracked=False, default_path_format=None):
        if default_path_format is None:
            default_path_format = get_contextual_dict(self, 'settings').get(
                'path_format', None
            )
        return super(FileSystemMap, self).add_file(name, extension, display_name, base_name, tracked, default_path_format)

    def add_folder(self, name, display_name=None, base_name=None, tracked=False, default_path_format=None):
        if default_path_format is None:
            default_path_format = get_contextual_dict(self, 'settings').get(
                'path_format', None
            )
        return super(FileSystemMap, self).add_folder(name, display_name, base_name, tracked, default_path_format)
