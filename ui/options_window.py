from PyQt5.QtWidgets import QDialog, QTreeWidgetItem
from scapy.interfaces import get_working_ifaces
from PyQt5 import QtCore, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(536, 394)
        self.verticalLayoutWidget = QtWidgets.QWidget(Dialog)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(9, 9, 511, 371))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(6, 0, 6, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.interface_list = QtWidgets.QTreeWidget(self.verticalLayoutWidget)
        self.interface_list.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.interface_list.setObjectName("interface_list")
        self.interface_list.headerItem().setText(0, "Interface")
        self.verticalLayout.addWidget(self.interface_list)
        self.buttonBox = QtWidgets.QDialogButtonBox(self.verticalLayoutWidget)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept) # type: ignore
        self.buttonBox.rejected.connect(Dialog.reject) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Options"))


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
