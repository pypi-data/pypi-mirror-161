from kabaret import flow
from libreflow.baseflow.task import ManagedTask, ManagedTaskCollection


class Task(ManagedTask):
    
    @classmethod
    def get_source_display(cls, oid):
        split = oid.split('/')
        return f'{split[3]} · {split[5]} · {split[7]}'


class Tasks(ManagedTaskCollection):

    def mapped_items(self, page_num=0, page_size=None):
        items = super(Tasks, self).mapped_items(
            page_num, page_size
        )

        mgr = self.root().project().get_task_manager()
        current_site = self.root().project().get_current_site()
        visible_tasks = current_site.visible_tasks.get()

        items = [
            i for i in items
            if not mgr.default_tasks[i.name()].assignation_enabled.get()
            or i.name() in visible_tasks
        ]
        return items
