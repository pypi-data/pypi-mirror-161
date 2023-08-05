from kabaret import flow
from kabaret.flow_entities.entities import Property
from libreflow.baseflow.shot import (
    ShotCollection,
    Shot as BaseShot,
    Sequence as BaseSequence
)

from .task import Tasks


class Shot(BaseShot):
    '''
    This shot class holds a `kitsu_shots` property which
    provides the Kitsu shot entities bound to this object.

    This property is suited for binding multiple Kitsu shots
    to a single flow shot.
    Its value must be a dictionnary mapping the sequence names
    with the lists of bound shot names:
        {<sequence_name>: [<shot_name>, ...]}
    '''

    kitsu_shots = Property().ui(hidden=True)
    
    tasks = flow.Child(Tasks).ui(
        expanded=True
    )

    @classmethod
    def get_source_display(cls, oid):
        split = oid.split('/')
        return f'{split[3]} · {split[5]}'

    def ensure_tasks(self):
        """
        Creates the tasks of this shot based on the task
        templates of the project, skipping any existing task.
        """
        mgr = self.root().project().get_task_manager()

        for dt in mgr.default_tasks.mapped_items():
            if not self.tasks.has_mapped_name(dt.name()) and not dt.optional.get():
                t = self.tasks.add(dt.name())
                t.enabled.set(dt.enabled.get())
        
        self.tasks.touch()

    def get_default_contextual_edits(self, context_name):
        if context_name == 'settings':
            sequence, shot = self.name().split('_', maxsplit=1)
            return dict(sequence=sequence, shot=shot)
    
    def set_task_status(self, task_name, task_status, comment=''):
        kitsu_shots = self.kitsu_shots.get()

        if not kitsu_shots:
            raise Exception(
                f'Kitsu shots associated to {self.oid()} undefined'
            )
        
        kitsu = self.root().project().kitsu_api()

        for sequence_name, shot_names in kitsu_shots.items():
            for shot_name in shot_names:
                kitsu.set_shot_task_status(
                    sequence_name, shot_name, task_name, task_status, comment
                )
    
    def get_task_status(self, task_name):
        kitsu_shots = self.kitsu_shots.get()

        if not kitsu_shots:
            raise Exception(
                f'Kitsu shots associated to {self.oid()} undefined'
            )
        
        sequence_name, shot_names = list(kitsu_shots.items())[0]
        
        kitsu = self.root().project().kitsu_api()
        return kitsu.get_shot_task_status_name(
            sequence_name, shot_names[0], task_name
        )


class Shots(ShotCollection):
    
    def add_shot(self, name, kitsu_shots):
        s = self.add(name)
        s.kitsu_shots.set(kitsu_shots)
        s.ensure_tasks()

        return s
