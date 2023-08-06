from kabaret.app.ui.gui.widgets.flow.flow_view import QtCore, QtGui, QtWidgets
from kabaret.app import resources
from libreflow.resources.icons import libreflow as _

from ....resources.icons import gui as _, shotgrid as _


ICON_BY_STATUS = {
    'error': ('icons.gui', 'error'),
    'warning': ('icons.gui', 'warning'),
    'valid': ('icons.libreflow', 'available'),
}


class ShotItem(QtWidgets.QTreeWidgetItem):
    
    def __init__(self, tree, shot):
        super(ShotItem, self).__init__(tree)
        self._tree = tree
        self._shot = None
        self.set_shot(shot)
    
    def set_shot(self, shot):
        self._shot = shot
        self._update()

    def _update(self):
        self.setText(0, self._shot['sg_name'])

        icon = ICON_BY_STATUS[self._shot['status']]
        self.setIcon(1, QtGui.QIcon(resources.get_icon(icon)))
        icon = ('icons.gui', 'found')
        
        if self._shot['layout_src_path'] is None:
            icon = ('icons.gui', 'not-found')
            self.setToolTip(2, 'Not found on disk')
        else:
            calc = self._shot['layout_src_size']
            units = ["KB", "MB", "GB", "TB"]
            unit = "byte(s)"

            for x in units:
                if calc >= 1024.0:
                    unit = x
                    calc /= 1024.0

            self.setText(4, str(round(calc, 2)) + " " + unit)

            if (calc >= 500.0 and unit == "MB") or (calc >= 1.0 and calc <= 2.0 and unit == "GB"):
                font = self.font(4)
                font.setBold(True)
                self.setFont(4, font)
            elif calc >= 2.0 and unit == "GB":
                color = QtGui.QColor(255, 27, 31)
                font = self.font(4)
                font.setBold(True)
                self.setFont(4, font)
                self.setForeground(4, QtGui.QBrush(color))
        
        self.setIcon(2, QtGui.QIcon(resources.get_icon(icon)))

        status = self._shot['layout_sg_status']
        self.setIcon(3, QtGui.QIcon(resources.get_icon(('icons.shotgrid', status))))
        self.setToolTip(3, status)

        flags = QtCore.Qt.ItemIsEnabled

        if self._shot['status'] != 'error' and self._shot['available']:
            flags |= QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsUserCheckable
            if self._shot['status'] == 'warning':
                self.setCheckState(0, QtCore.Qt.Unchecked)
            else:
                self.setCheckState(0, QtCore.Qt.Checked)

        self.setFlags(flags)
    
    def status(self):
        return self._shot['status']
    
    def is_selected(self):
        return self.checkState(0) == QtCore.Qt.Checked
    
    def to_dict(self):
        return self._shot


class ShotList(QtWidgets.QTreeWidget):
    
    def __init__(self, custom_widget, session):
        super(ShotList, self).__init__()
        self._custom_widget = custom_widget
        self.session = session

        self.setHeaderLabels(self.get_columns())
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        
        self.refresh()

        self.header().resizeSections(QtWidgets.QHeaderView.ResizeToContents)
    
    def get_columns(self):
        return ('Shot', 'Status', 'LO files', 'LO status', 'Size')
    
    def sizeHint(self):
        return QtCore.QSize(300, 500)
    
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Space:
            for item in self.selectedItems():
                if item.checkState(0) == QtCore.Qt.Unchecked:
                    item.setCheckState(0, QtCore.Qt.Checked)
                else:
                    item.setCheckState(0, QtCore.Qt.Unchecked)
    
    def refresh(self, refresh_data=False):
        self.clear()

        shots_data = self._custom_widget.get_shots_data(refresh_data)

        for shot in shots_data:
            ShotItem(self, shot)
