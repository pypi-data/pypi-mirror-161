import argparse
from qtpy import QtCore

from kabaret.app.ui.gui import KabaretStandaloneGUISession
from kabaret.script_view import ScriptView
from kabaret.app.actors.flow import Flow

from libreflow.utils.kabaret.jobs.jobs_view import JobsView
from libreflow.utils.kabaret.jobs.jobs_actor import Jobs
from libreflow.utils.kabaret.subprocess_manager import SubprocessManager, SubprocessView

from .custom_home import CustomHomeRoot


class SessionGUI(KabaretStandaloneGUISession):

    def __init__(self, session_name='Standalone', tick_every_ms=10, debug=False, script_view=True, jobs_view=True):
        super(SessionGUI, self).__init__(session_name, tick_every_ms, debug)
        self._script_view = script_view
        self._jobs_view = jobs_view

    def register_view_types(self):
        super(SessionGUI, self).register_view_types()

        type_name = self.register_view_type(SubprocessView)
        self.add_view(
            type_name,
            view_id='Processes',
            hidden=not self.debug_mode,
            area=QtCore.Qt.RightDockWidgetArea,
        )

        if self._script_view:
            type_name = self.register_view_type(ScriptView)
            self.add_view(
                type_name,
                hidden=not self.debug_mode,
                area=QtCore.Qt.RightDockWidgetArea
            )
        if self._jobs_view:
            type_name = self.register_view_type(JobsView)
            self.add_view(
                type_name,
                hidden=not self.debug_mode,
                area=QtCore.Qt.RightDockWidgetArea,
            )

    def _create_actors(self):
        super(SessionGUI, self)._create_actors()
        
        Flow(self, CustomHomeRootType=CustomHomeRoot)
        subprocess_manager = SubprocessManager(self)
        jobs = Jobs(self)

    @staticmethod
    def parse_command_line_args(args):
        (
            session_name,
            host,
            port,
            cluster_name,
            db,
            password,
            debug,
            remaining_args,
        ) = KabaretStandaloneGUISession.parse_command_line_args(args)

        parser = argparse.ArgumentParser(
            description='Libreflow.rouge Session Arguments'
        )

        parser.add_argument(
            '-u', '--user', dest='user'
        )
        parser.add_argument(
            '-s', '--site', dest='site'
        )
        parser.add_argument(
            '-j', '--jobs_filter', dest='jobs_filter'
        )

        values, remaining_args = parser.parse_known_args(remaining_args)

        return (
            session_name,
            host, port, cluster_name,
            db, password, debug,
            values.user, values.site, values.jobs_filter, remaining_args
        )
