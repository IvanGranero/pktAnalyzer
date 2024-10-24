from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit, QDialog, QTreeWidgetItem
from PyQt5.uic import loadUi
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from scapy.interfaces import get_if_list, get_working_ifaces

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
            result = eval(code, {'df': self.provider.alldata})
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
        #self.available_interfaces = get_if_list()
        interfaces = get_working_ifaces()
        self.available_interfaces = []
        for iface in interfaces:
            self.available_interfaces.append(iface.name)
            item = QTreeWidgetItem([iface.name + " " + iface.mac])
            self.interface_list.addTopLevelItem(item)

#END OF CLASS OptionsWindow

class PlotWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.mainwindow = parent
        self.setWindowTitle("Plot Window")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()
        # Create a matplotlib figure and canvas
        self.canvas = FigureCanvas(Figure(figsize=(5, 4)))
        layout.addWidget(self.canvas)
        
        # Add Navigation toolbar
        self.toolbar = NavigationToolbar(self.canvas, self)
        layout.addWidget(self.toolbar)
        
        # Plot something
        self.plot()

        self.setLayout(layout)

    def plot(self):
        ax = self.canvas.figure.add_subplot(111)
        data = self.mainwindow.data_provider.query_filter("df[df['identifier'] == 304]['hexbytes']")
        ax.plot(data, 'r-')
        ax.set_title('Sample Plot')
        self.canvas.draw() 

#END OF CLASS PlotWindow
