from kabaret import flow
from kabaret.flow_entities.entities import Entity
from libreflow.baseflow.film import Film as BaseFilm

from .shot import Shots


class ValidatedShots(flow.values.SessionValue):

    DEFAULT_EDITOR = 'multichoice'

    STRICT_CHOICES = False

    _action = flow.Parent()

    def __init__(self, parent, name):
        super(ValidatedShots, self).__init__(parent, name)
        self._shot_names = None
    
    def choices(self):
        if self._shot_names is None:
            self._shot_names = []
            
            kitsu = self.root().project().kitsu_api()
            validated_shots = kitsu.get_shots({
                self._action.task.get(): [self._action.validated_kitsu_status.get()]
            })
            for sq, sh in validated_shots:
                n = f'{sq}{sh}'
                self._shot_names.append(n)
        
        return self._shot_names
    
    def refresh_choices(self):
        self._shot_names = None
        self.revert_to_default()


class KitsuTaskNames(flow.values.SessionValue):

    DEFAULT_EDITOR = 'choice'

    STRICT_CHOICES = False

    _action = flow.Parent()

    def choices(self):
        tm = self.root().project().get_task_manager()
        kitsu = self.root().project().kitsu_api()
        subtasks = tm.get_subtasks('lighting')

        return [
            kitsu.get_task_name('lighting', st)
            for st in subtasks
        ]
    
    def revert_to_default(self):
        names = self.choices()
        if names:
            self.set(names[0])


class SendForValidation(flow.Action):

    validated_kitsu_status = flow.Param().ui(hidden=True)

    task = flow.SessionParam(value_type=KitsuTaskNames).watched()
    validated_shots = flow.SessionParam([], value_type=ValidatedShots)

    _film = flow.Parent()

    def needs_dialog(self):
        self.task.revert_to_default()
        return True
    
    def get_buttons(self):
        return ['Send', 'Cancel']
    
    def run(self, button):
        if button == 'Cancel':
            return
        
        for shot_name in self.validated_shots.get():
            f = self._get_lighting_file(shot_name)
            if f is not None and f.get_head_revision() is not None:
                f.to_validate.kitsu_target_task.set(self.task.get())
                f.to_validate.run('Confirm')
        
        self.validated_shots.refresh_choices()
        return self.get_result(close=False)
    
    def child_value_changed(self, child_value):
        if child_value is self.task:
            self.validated_shots.refresh_choices()
    
    def _get_lighting_file(self, shot_name):
        shot = self._film.shots[shot_name]
        files = shot.tasks['lighting'].files
        f = None

        if files.has_file('working_file', 'plas'):
            f = files['working_file_plas']
        
        return f


class Film(BaseFilm):
    
    shots = flow.Child(Shots).ui(
        expanded=True,
        show_filter=True,
    )

    sequences = flow.Child(flow.Object).ui(hidden=True)

    send_for_validation = flow.Child(SendForValidation)
