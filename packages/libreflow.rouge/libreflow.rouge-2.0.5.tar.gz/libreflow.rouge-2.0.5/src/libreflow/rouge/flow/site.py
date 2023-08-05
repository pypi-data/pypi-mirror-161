from kabaret import flow
from libreflow.baseflow.site import WorkingSite as BaseWorkingSite


class WorkingSite(BaseWorkingSite):

    visible_tasks = flow.OrderedStringSetParam()
