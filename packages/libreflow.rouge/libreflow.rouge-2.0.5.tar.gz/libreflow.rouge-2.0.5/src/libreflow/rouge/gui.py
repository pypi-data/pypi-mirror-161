import sys
import os

os.environ['QT_MAC_WANTS_LAYER'] = '1'

from kabaret.app.ui.gui.styles.gray import GrayStyle
from libreflow.resources.icons import libreflow, status
from libreflow.resources import file_templates

from .session import SessionGUI

GrayStyle()


def main(argv):
    (
        session_name,
        host,
        port,
        cluster_name,
        db,
        password,
        debug,
        user,
        site,
        jobs_filter,
        remaining_args,
    ) = SessionGUI.parse_command_line_args(argv)

    if site:
        os.environ['KABARET_SITE_NAME'] = site
    if user:
        os.environ['USER_NAME'] = user
    if jobs_filter:
        os.environ['JOBS_DEFAULT_FILTER'] = jobs_filter
    else:
        os.environ['JOBS_DEFAULT_FILTER'] = site

    session = SessionGUI(session_name=session_name, debug=debug)
    session.cmds.Cluster.connect(host, port, cluster_name, db, password)

    session.start()
    session.close()


if __name__ == '__main__':
    main(sys.argv[1:])