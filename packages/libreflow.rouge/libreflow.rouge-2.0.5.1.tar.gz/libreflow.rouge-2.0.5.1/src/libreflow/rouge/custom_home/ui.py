import six
import os
from kabaret.app.ui.gui.widgets.flow.flow_view import (
    CustomPageWidget,
    QtWidgets,
    QtCore,
    QtGui,
)


class ProjectThumbnailWidget(QtWidgets.QAbstractButton):

    def __init__(self, width, height, image_path=None, alt_text='', parent=None, image=None):
        super(ProjectThumbnailWidget, self).__init__(parent)
        self.setThumbnail = True
        self.alt_text = alt_text

        if image:
            ba = QtCore.QByteArray.fromBase64(bytes(image.split(',')[1], 'utf-8'))
            pixmap = QtGui.QPixmap()
            pixmap.loadFromData(ba, 'PNG')
            self.thumbnail = pixmap
        elif image_path:
            print('loading thumbnail from path')
            self.thumbnail = QtGui.QPixmap(image_path)
        else:
            self.setThumbnail = False

        self.width = width
        self.height = height

    def sizeHint(self):
        return QtCore.QSize(self.width, self.height)

    def paintEvent(self, event):
        QPainter = QtGui.QPainter()
        QPainter.begin(self)

        if self.setThumbnail:
            QPainter.drawPixmap(0, 0, self.width, self.height, self.thumbnail)
        else:
            rect = QtCore.QRect(0, 0, self.width - 1, self.height - 1)

            QPainter.drawRect(rect)
            font = QPainter.font()
            font.setPixelSize(int(self.height / 3))
            QPainter.setFont(font)

            QPainter.drawText(
                rect, QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter, self.alt_text
            )
        QPainter.end()


class ProjectWidget(QtWidgets.QWidget):

    def __init__(self, parent=None, project=None, HomePageWidget=None):
        super(ProjectWidget, self).__init__(parent)
        self.grid_layout = QtWidgets.QGridLayout()
        self.HomePageWidget = HomePageWidget
        
        try:
            project_thumbnail = self.HomePageWidget.session.cmds.Flow.call(
                '/%s' % project, 'get_project_thumbnail', {}, {}
            )
        except AttributeError:
            project_thumbnail = None
        
        # Project
        self.thumbnail_button = ProjectThumbnailWidget(
            600, 150, image_path=None, alt_text=project, image=project_thumbnail
        )

        self.thumbnail_button.clicked.connect(
            lambda project=project, button='thumbnail': self.on_project_button_clicked(
                project, button
            )
        )

        # Bookmarks
        self.fav_button = ProjectThumbnailWidget(
            128, 32,  alt_text='Bookmarks'
        )
        self.fav_button.clicked.connect(
            lambda project=project, button='fav': self.on_project_button_clicked(
                project, button
            )
        )

        self.grid_layout.addWidget(self.thumbnail_button, 0, 0, 3, 1)
        self.grid_layout.addWidget(self.fav_button, 0, 1)

        try:
            requiered_versions = self.HomePageWidget.session.cmds.Flow.call(
                '/%s' % project, 'get_required_versions', {}, {}
            )
            
            start_line = 3

            for r in requiered_versions:
                color = '#74787a'
                if r[3] > 0:
                    color = '#b9c2c8'
                required_update = ''
                if r[3] == 1:
                    required_update = ' <strong>Update to %s available</strong>' % r[2]
                elif r[3] == 2:
                    required_update = ' <font color=\'red\'><strong>Update required to %s</strong></font>' % r[2]
                text = '<font color=\'%s\'>%s %s %s</font>' % (color, r[0], r[1], required_update)
                t = QtWidgets.QLabel(text)
                t.setMargin(20)
                t.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
                self.grid_layout.addWidget(t, start_line, 0, 3, 1)

                start_line += 1
        except AttributeError:
            pass

        # Update users last connexion
        try:
            self.HomePageWidget.session.cmds.Flow.call(
                '/%s' % project, 'update_user_last_visit', {}, {}
            )
        except AttributeError:
            pass
        
        self.setLayout(self.grid_layout)

    def on_project_button_clicked(self, project, button):
        if button == 'thumbnail':
            oid = '/%s' % project
        elif button == 'fav':
            oid = '/%s/user' % project
        
        self.HomePageWidget.session.cmds.Flow.call('/' + project, 'touch', {}, {})
        self.HomePageWidget.page.goto(oid)


class ProjectHomePageWidget(CustomPageWidget):
    
    def build(self):
        self.projectsButtons = {}
        project_list = QtWidgets.QVBoxLayout()

        for name, infos in self.session.cmds.Flow.call('/Home', 'get_projects', {}, {}):
            if infos['status'] == 'Archived':
                continue

            project_list.addWidget(ProjectWidget(None, name, self))
        
        self.setLayout(project_list)
