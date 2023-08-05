from libreflow.baseflow.runners import (
    CHOICES, CHOICES_ICONS,
    EditFileRunner,
    DefaultRunners as BaseDefaultRunners,
)

from ..resources import file_templates
from ..resources.icons import gui as _


CHOICES += ['plas', 'houdoo']


class Palas(EditFileRunner):

    @classmethod
    def supported_extensions(cls):
        return ['.plas']
    
    def show_terminal(self):
        return True
    
    def keep_terminal(self):
        return False


class Houdoo(EditFileRunner):

    @classmethod
    def supported_extensions(cls):
        return ['.houdoo']


class DefaultRunners(BaseDefaultRunners):

    def mapped_names(self, page_num=0, page_size=None):
        return CHOICES
