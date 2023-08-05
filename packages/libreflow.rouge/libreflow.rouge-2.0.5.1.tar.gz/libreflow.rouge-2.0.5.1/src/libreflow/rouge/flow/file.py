import os
import shutil
import pathlib

from kabaret import flow
from libreflow.baseflow.file import (
    TrackedFile            as BaseTrackedFile,
    TrackedFolder          as BaseTrackedFolder,
    Revision               as BaseRevision,
    TrackedFolderRevision  as BaseTrackedFolderRevision,
    FileSystemMap          as BaseFileSystemMap,
    PublishFileAction      as BasePublishFileAction,
)
from libreflow.utils.flow import get_contextual_dict


class Revision(BaseRevision):
    pass


class TrackedFolderRevision(BaseTrackedFolderRevision):
    pass


class KitsuTaskNames(flow.values.SessionValue):

    DEFAULT_EDITOR = 'choice'

    STRICT_CHOICES = False

    _task = flow.Parent(4)

    def choices(self):
        kitsu = self.root().project().kitsu_api()
        tm = self.root().project().get_task_manager()
        subtasks = tm.get_subtasks(self._task.name())

        return [
            kitsu.get_task_name(self._task.name(), st)
            for st in subtasks
        ]
    
    def revert_to_default(self):
        current = self._task.current_subtask.get()
        kitsu = self.root().project().kitsu_api()
        if current:
            kitsu_task = kitsu.get_task_name(self._task.name(), current)
            self.set(kitsu_task)
        else:
            names = self.choices()
            if names:
                self.set(names[0])


class PublishFileAction(BasePublishFileAction):

    submit_for_check = flow.SessionParam(False).ui(
        editor='bool',
        label='Submit for check',
    )
    kitsu_task = flow.SessionParam(value_type=KitsuTaskNames)
    status = flow.SessionParam('F To CHECK ')

    _task = flow.Parent(3)
    _shot = flow.Parent(5)

    def needs_dialog(self):
        self.submit_for_check.revert_to_default()
        # self.kitsu_task.revert_to_default()
        return True

    def run(self, button):
        super(PublishFileAction, self).run(button)
        
        if self.submit_for_check.get():
            user_name = self.root().project().get_user_name()

            self._shot.set_task_status(
                self.kitsu_task.get(),
                self.status.get(),
                comment=(
                    f"**{user_name}** has changed {self._shot.name()} "
                    f"status on '{self._task.name()}/{self._file.display_name.get()}' "
                    f"*{self._file.get_head_revision().name()}*.\n"
                    f"> {self.comment.get()}\n\n"
                    f"*{self._task.oid()}*"
                )
            )


class ToValidateKeyFrame(flow.Action):

    _file = flow.Parent()
    _map  = flow.Parent(2)
    _task = flow.Parent(3)
    _shot = flow.Parent(5)

    kitsu_target_task   = flow.SessionParam(value_type=KitsuTaskNames).watched()
    kitsu_source_status = flow.Param('H TO SEND').ui(hidden=True)
    kitsu_target_status = flow.Param('I Waiting For Approval').ui(hidden=True)
    task_files          = flow.DictParam({
        'L&S KEY FRAME': ('key_frame_to_validate.plas', 'fix'),
        'L&S ANIMATION': ('animation_to_validate.plas', 'ani'),
    }).ui(hidden=True)

    def allow_context(self, context):
        return (
            context
            and self._file.display_name.get() == 'lighting.plas'
            and self._file.get_head_revision() is not None
        )
    
    def needs_dialog(self):
        self.kitsu_target_task.revert_to_default()
        return True
    
    def get_buttons(self):
        return ['Confirm', 'Cancel']
    
    def run(self, button):
        if button == 'Cancel':
            return
        
        self._ensure_file_to_valid()
        self._update_kitsu_status()
    
    def child_value_changed(self, child_value):
        if child_value is self.kitsu_target_task:
            self._check_kitsu_status()

    def _ensure_file_to_valid(self):
        file_name, suffix = self.task_files.get()[self.kitsu_target_task.get()]
        name, ext = file_name.split('.')
        if not self._map.has_file(name, ext):
            f = self._map.add_file(
                name, ext,
                tracked=True,
                default_path_format='{sequence}_{shot}/{sequence}_{shot}_'+suffix+'_{revision}'
            )
        else:
            f = self._map[f'{name}_{ext}']
        
        r = self._file.get_head_revision()
        source_path = r.get_path()
        take_index = len(f.get_revisions().mapped_names()) + 1
        take = f.add_revision(
            name=f't{take_index:02}',
            comment=f'Created from lighting.plas {r.name()}'
        )
        self._map.touch()

        take_path = take.get_path()
        os.makedirs(os.path.dirname(take_path), exist_ok=True)
        shutil.copy2(source_path, take_path)
    
    def _check_kitsu_status(self):
        kitsu_task_name = self.kitsu_target_task.get()
        source_status = self.kitsu_source_status.get()

        if self._shot.get_task_status(kitsu_task_name) != source_status:
            self.message.set(
                f'Status is not {source_status}. Do you want to continue ?'
            )
        else:
            self.message.set('')
    
    def _update_kitsu_status(self):
        kitsu_task_name = self.kitsu_target_task.get()
        self._shot.set_task_status(
            kitsu_task_name,
            self.kitsu_target_status.get()
        )


class TrackedFile(BaseTrackedFile):
    
    to_validate = flow.Child(ToValidateKeyFrame)


class TrackedFolder(BaseTrackedFolder):
    pass


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
