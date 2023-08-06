from kabaret.app.ui.gui.widgets.flow.flow_view import QtCore, QtGui, QtWidgets
from kabaret.app import resources

from ...resources.icons import gui as _, shotgrid as _


class ShotListItem(QtWidgets.QTreeWidgetItem):

    ICON_BY_STATUS = {
        'valid':   ('icons.gui', 'available'),
        'warning': ('icons.gui', 'warning'),
        'error':   ('icons.gui', 'error')
    }

    def __init__(self, tree, shot, custom_widget, session):
        super(ShotListItem, self).__init__(tree)
        self.custom_widget = custom_widget
        self.session = session
        self.item = shot

        self.refresh()

    def shot_data(self):
        return self.session.cmds.Flow.call(
            self.custom_widget.oid, 'get_shot_data', [self.item], {}
        )
    
    def refresh(self):
        d = self.shot_data()

        self.setText(0, d.display_name.get())
        self.setIcon(0, self.get_icon(self.ICON_BY_STATUS[d.status.get()]))
        
        if d.status.get() == 'valid':
            self.setCheckState(0, QtCore.Qt.Checked)
        else:
            self.setCheckState(0, QtCore.Qt.Unchecked)

    def status(self):
        return self.shot_data().status.get()
    
    @staticmethod
    def get_icon(icon_ref):
        return QtGui.QIcon(resources.get_icon(icon_ref))


class ShotList(QtWidgets.QTreeWidget):
    
    def __init__(self, custom_widget, session):
        super(ShotList, self).__init__()
        self.custom_widget = custom_widget
        self.session = session

        self.setHeaderLabel(self.get_header_label())

        self.refresh()

        self.itemChanged.connect(self._on_item_changed)
    
    def get_header_label(self):
        label = 'Shot'
        return label
    
    def sizeHint(self):
        return QtCore.QSize(300, 500)
    
    def refresh(self, force_update=False):
        self.clear()
        shots = self.session.cmds.Flow.call(
            self.custom_widget.oid, 'get_shots', [force_update], {}
        )

        for shot in shots:
            ShotListItem(self, shot, self.custom_widget, self.session)
    
    def get_shots_count(self, force_update=False):
        shots_count = self.session.cmds.Flow.call(
            self.custom_widget.oid, 'get_shots_count', [force_update], {}
        )
        if shots_count > 1:
            return str(shots_count) + " shots"
        return str(shots_count) + " shot"

    def _on_item_changed(self, item, column):
        if column == 0 and item.status() == 'error' or item.status() == 'warning':
            item.setCheckState(column, QtCore.Qt.Unchecked)