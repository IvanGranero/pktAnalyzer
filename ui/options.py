from PyQt5.QtWidgets import QDialog, QTreeWidgetItem
from scapy.interfaces import get_working_ifaces
from ui.optionsWindow import Ui_Dialog

class OptionsWindow(QDialog, Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.get_network_interfaces()

    def get_network_interfaces(self):
        interfaces = get_working_ifaces()
        self.available_interfaces = []
        for iface in interfaces:
            self.available_interfaces.append(iface.name)
            item = QTreeWidgetItem([iface.name])
            self.interface_list.addTopLevelItem(item)
