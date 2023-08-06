from kabaret.app.ui.gui.widgets.flow.flow_view import QtCore, QtGui, QtWidgets, CustomPageWidget
from kabaret.app import resources

from .shot_list import ShotList


class UploadSGPlayblastsWidget(CustomPageWidget):

    def build(self):
        self.shot_list = ShotList(self, self.session)
        self.shots_count = QtWidgets.QLabel(self.shot_list.get_shots_count())
        
        icon = QtGui.QIcon(resources.get_icon(('icons.gui', 'refresh')))
        self.button_refresh = QtWidgets.QPushButton(icon, '')
        self.checkbox_selectall = QtWidgets.QCheckBox('Select all')
        self.copy_feedback = QtWidgets.QLabel('')
        self.button_copy_last_delivery = QtWidgets.QPushButton('Copy last delivery')
        self.button_upload = QtWidgets.QPushButton('Upload')
        
        self.button_refresh.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        self.button_refresh.setToolTip('Refresh shot list and reset selection')
        self.button_refresh.setMaximumHeight(40)
        self.checkbox_selectall.setCheckState(QtCore.Qt.Checked)
        self.button_copy_last_delivery.setMaximumWidth(150)
        self.button_copy_last_delivery.setMaximumHeight(40)
        self.button_upload.setMaximumWidth(150)
        self.button_upload.setMaximumHeight(40)

        glo = QtWidgets.QGridLayout()
        glo.addWidget(self.shots_count, 0, 0, 1, 6)
        glo.addWidget(self.shot_list, 1, 0, 1, 6)
        glo.addWidget(self.button_refresh, 2, 0)
        glo.addWidget(self.checkbox_selectall, 2, 1)
        glo.addWidget(self.copy_feedback, 2, 3, QtCore.Qt.AlignRight)
        glo.addWidget(self.button_copy_last_delivery, 2, 4)
        glo.addWidget(self.button_upload, 2, 5)
        glo.setColumnStretch(2, 2)
        self.setLayout(glo)
    
        # Install callbacks
        self.button_refresh.clicked.connect(self._on_button_refresh_clicked)
        self.checkbox_selectall.stateChanged.connect(self._on_checkbox_selectall_state_changed)
        self.button_copy_last_delivery.clicked.connect(self._on_button_copy_last_delivery_clicked)
        self.button_upload.clicked.connect(self._on_button_upload_clicked)

    def _on_button_refresh_clicked(self):
        self.checkbox_selectall.setCheckState(QtCore.Qt.Checked)
        self.shot_list.refresh(force_update=True)
        self.shots_count.setText(self.shot_list.get_shots_count())
        self.copy_feedback.setText('')
    
    def _on_checkbox_selectall_state_changed(self, state):
        for i in range(self.shot_list.topLevelItemCount()):
            state = QtCore.Qt.CheckState(state)
            self.shot_list.topLevelItem(i).setCheckState(0, state)
    
    def _on_button_copy_last_delivery_clicked(self):
        copy_last_delivery = self.session.cmds.Flow.call(
            self.oid, 'copy_last_delivery', [None], {}
        )
        if copy_last_delivery == 'Not found':
            self.copy_feedback.setText('No delivery log found')
        if copy_last_delivery == 'Copied':
            self.copy_feedback.setText('Copied!')
    
    def _on_button_upload_clicked(self):
        selected_shots = []

        for i in range(self.shot_list.topLevelItemCount()):
            shot = self.shot_list.topLevelItem(i)
            if shot.checkState(0) == QtCore.Qt.Checked:
                selected_shots.append(shot.item)
        
        self.session.cmds.Flow.call(
            self.oid, 'upload', [selected_shots], {}
        )

        self.shot_list.refresh(force_update=True)
        self.shots_count.setText(self.shot_list.get_shots_count())
        self.copy_feedback.setText('')
