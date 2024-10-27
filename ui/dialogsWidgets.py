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

    def evaluate(self, return_data=False):
        code = self.input.text()
        self.input.clear()
        try:
            result = eval(code, {'df': self.provider.alldata})
            self.output.append(f">>> {code}\n{result}")
            if return_data:
                return result
            else:
                self.provider.data = result
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
            item = QTreeWidgetItem([iface.name])
            self.interface_list.addTopLevelItem(item)

#END OF CLASS OptionsWindow

class PlotWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi("ui/plotWindow.ui", self)        
        self.mainwindow = parent
        self.canvas = FigureCanvas(Figure(figsize=(5, 4)))
        self.plot_layout.addWidget(self.canvas)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.plot_layout.addWidget(self.toolbar)
        self.btn_plot.clicked.connect(self.plot)

    def plot(self):
        xaxis = self.xaxis.text()
        yaxis = self.yaxis.text()
        column_index = self.mainwindow.tableview.selectedIndexes()
        if column_index:
            column_index = column_index[0].column()
        
        ydata = self.mainwindow.data_provider.data.iloc[:, column_index]
        self.canvas.figure.clf()
        ax = self.canvas.figure.add_subplot(111)
        selected_chart = self.chart_types.currentItem().text()
        if selected_chart == 'Line Plot':
            ax.plot(ydata)
        elif selected_chart == 'Scatter Plot':
            ax.scatter(ydata.index, ydata)
        elif selected_chart == 'Bar Chart':
            ydata = ydata.value_counts()
            ax.bar(ydata.index, ydata)
        elif selected_chart == 'Pie Chart':
            ydata = ydata.value_counts()
            ax.pie(ydata, labels=ydata.index)
        elif selected_chart == 'Histogram':
            ax.hist(ydata)
        elif selected_chart == 'Box Plot':
            ax.boxplot(ydata)

        ax.set_title(selected_chart)
        self.canvas.draw() 

#END OF CLASS PlotWindow
