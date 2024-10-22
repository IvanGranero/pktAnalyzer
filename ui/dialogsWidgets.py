from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit, QDialog, QTreeWidgetItem
from PyQt5.uic import loadUi
import psutil

class REPL(QWidget):
    def __init__(self, provider):
        super().__init__()
        self.provider = provider
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle('data REPL')
        self.setGeometry(100, 100, 500, 400)

        self.layout = QVBoxLayout()

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.layout.addWidget(self.output)

        self.input = QLineEdit()
        self.input.returnPressed.connect(self.evaluate)
        self.layout.addWidget(self.input)

        self.setLayout(self.layout)

    def evaluate(self):
        code = self.input.text()
        self.input.clear()
        try:
            result = eval(code, {'df': self.provider.alldata}) # should we add packets to the list?
            self.output.append(f">>> {code}\n{result}")
            return result
        except Exception as e:
            self.output.append(f">>> {code}\nError: {e}")
#END OF CLASS REPL

class OptionsWindow(QDialog):
    def __init__(self):
        super().__init__()
        loadUi("ui/optionsWindow.ui", self)
        self.get_network_interfaces()

    def get_network_interfaces(self):
        interfaces = psutil.net_if_addrs()
        for interface in interfaces:
            item = QTreeWidgetItem([interface])
            self.interface_list.addTopLevelItem(item)

        # while layer:
        #     layer_item = QTreeWidgetItem([layer.summary()])
        #     self.packet_inspector.addTopLevelItem(layer_item)
        #     # add all the packet fields
        #     for field_name, field_val in layer.fields.items():
        #         field_item = QTreeWidgetItem([f"{field_name}: {field_val}"])
        #         layer_item.addChild(field_item)

#END OF CLASS OptionsWindow