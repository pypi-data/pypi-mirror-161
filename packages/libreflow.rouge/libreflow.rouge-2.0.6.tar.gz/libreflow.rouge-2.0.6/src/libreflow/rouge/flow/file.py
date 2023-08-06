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
    CreateWorkingCopyAction as BaseCreateWorkingCopyAction,
    PublishFileAction      as BasePublishFileAction,
    RevisionsWorkingCopiesChoiceValue,
)
from libreflow.utils.flow import get_contextual_dict


class Revision(BaseRevision):
    pass


class TrackedFolderRevision(BaseTrackedFolderRevision):
    pass


class RevisionsWorkingCopies(RevisionsWorkingCopiesChoiceValue):

    _shot = flow.Parent(6)

    def _fill_ui(self, ui):
        ui['hidden'] = (
            self._shot.get_task_status('L&S ANIMATION') == 'K APPROVED'
        )


class CreateWorkingCopyAction(BaseCreateWorkingCopyAction):

    from_revision = flow.Param(None, RevisionsWorkingCopies).ui(
        label='Revision'
    )

    _shot = flow.Parent(5)

    def get_buttons(self):
        status = self._shot.get_task_status('L&S ANIMATION')
        if status == 'K APPROVED':
            self.message.set((
                '<h3>Create a working copy</h3>'
                '<font color=#D5000D>You can\'t create a working '
                'copy since the status of the <b>L&S ANIMATION</b> '
                'task is <b>APPROVED</b>.</font>'
            ))
            return ['Cancel']
        else:
            return super(CreateWorkingCopyAction, self).get_buttons()


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


class KitsuTargetStatus(flow.values.SessionValue):

    DEFAULT_EDITOR = 'choice'

    _statutes = {
        'WIP': 'E Work In Progress',
        'To check': 'F To CHECK ',
    }

    def choices(self):
        return ['WIP', 'To check']
    
    def get_kitsu_status(self):
        return self._statutes[self._value]


class PublishFileAction(BasePublishFileAction):

    keep_editing = flow.SessionParam(False).ui(
        editor='bool',
        hidden=True,
    )
    upload_after_publish = flow.SessionParam(False).ui(
        editor='bool',
        hidden=True,
    )
    status = flow.SessionParam('WIP', KitsuTargetStatus).ui(
        label='Kitsu status'
    )

    _file = flow.Parent()
    _task = flow.Parent(3)
    _shot = flow.Parent(5)

    def check_default_values(self):
        self.comment.apply_preset()
    
    def update_presets(self):
        self.comment.update_preset()

    def run(self, button):
        # Keep working copy when Kitsu status is set to WIP
        self.keep_editing.set(
            self.status.get() == 'WIP'
        )

        super(PublishFileAction, self).run(button)
        
        user_name = self.root().project().get_user_name()

        key_frame_status = self._shot.get_task_status('L&S KEY FRAME')
        target_task = 'L&S KEY FRAME'

        if key_frame_status == 'K APPROVED':
            target_task = 'L&S ANIMATION'

        self._shot.set_task_status(
            target_task,
            self.status.get_kitsu_status(),
            comment=(
                f"**{user_name}** has changed {self._shot.name()} "
                f"status on '{self._task.name()}/{self._file.display_name.get()}' "
                f"**{self._file.get_head_revision().name()}**.\n"
                f"> {self.comment.get()}\n\n"
                f"*{self._task.oid()}*"
            )
        )


class SendFileForValidation(flow.Action):

    _file = flow.Parent()
    _map  = flow.Parent(2)
    _task = flow.Parent(3)
    _shot = flow.Parent(5)

    kitsu_target_task   = flow.SessionParam(value_type=KitsuTaskNames).watched()
    kitsu_source_status = flow.Param('H TO SEND').ui(hidden=True)
    kitsu_target_status = flow.Param('I Waiting For Approval').ui(hidden=True)
    task_files          = flow.DictParam({
        'L&S KEY FRAME': ('takes_fix.plas', 'takes_fix', None),
        'L&S ANIMATION': ('takes_ani.plas', 'takes_ani', 'ani'),
    }).ui(hidden=True)

    def allow_context(self, context):
        return (
            context
            and self._file.display_name.get() == 'working_file'
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
        elif not self.is_status_valid():
            return self.get_result(close=False)
        
        file_name, take_name, revision_name = self._ensure_file_to_valid()
        self._update_kitsu_status(file_name, take_name, revision_name)
    
    def child_value_changed(self, child_value):
        if child_value is self.kitsu_target_task:
            self._check_kitsu_status()
    
    def is_status_valid(self):
        kitsu_task_name = self.kitsu_target_task.get()
        source_status = self.kitsu_source_status.get()

        return self._shot.get_task_status(kitsu_task_name) == source_status

    def _ensure_file_to_valid(self):
        file_name, file_display_name, suffix = self.task_files.get()[self.kitsu_target_task.get()]
        suffix = suffix and suffix+'_' or ''
        name, ext = file_name.split('.')

        if not self._map.has_file(name, ext):
            f = self._map.add_file(
                name, ext,
                display_name=file_display_name,
                tracked=True,
                default_path_format='{sequence}_{shot}/{sequence}_{shot}_'+suffix+'{revision}'
            )
        else:
            f = self._map[f'{name}_{ext}']
        
        r = self._file.get_head_revision()
        source_path = r.get_path()
        take_index = len(f.get_revisions().mapped_names()) + 1
        take = f.add_revision(
            name=f't{take_index:02}',
            comment=f'Created from working file {r.name()}'
        )
        self._map.touch()

        take_path = take.get_path()
        os.makedirs(os.path.dirname(take_path), exist_ok=True)
        shutil.copy2(source_path, take_path)

        return f.display_name.get(), take.name(), r.name()
    
    def _check_kitsu_status(self):
        if not self.is_status_valid():
            self.message.set((
                '<font color=#D5000D>'
                'You cannot send this file for validation since '
                f'its Kitsu status is not <b>{self.kitsu_source_status.get()}</b>.'
                '</font>'
            ))
        else:
            self.message.set('')
    
    def _update_kitsu_status(self, file_name, take_name, revision_name):
        kitsu_task_name = self.kitsu_target_task.get()
        user_name = self.root().project().get_user_name()
        self._shot.set_task_status(
            kitsu_task_name,
            self.kitsu_target_status.get(),
            comment=(
                f"**{user_name}** has changed {self._shot.name()} "
                f"status on '{self._task.name()}/{file_name}' "
                f"**{take_name}**.\n"
                f"> Created from working file **{revision_name}**\n\n"
                f"*{self._task.oid()}*"
            )
        )


class TrackedFile(BaseTrackedFile):
    
    to_validate = flow.Child(SendFileForValidation)


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
