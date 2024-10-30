from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit, QDialog, QTreeWidgetItem
from PyQt5.uic import loadUi
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from scapy.interfaces import get_working_ifaces
import networkx as nx

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
            result = self.provider.query_filter(code)
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
        df = self.mainwindow.data_provider.alldata
        column_index = self.mainwindow.tableview.selectedIndexes()
        if column_index:
            column_index = column_index[0].column()
            self.yaxis.setText(df.columns[column_index]) 
        self.xaxis.setText('Index')
        ydata = df.iloc[:, column_index]
        self.canvas.figure.clf()
        ax = self.canvas.figure.add_subplot(111)
        selected_chart = self.chart_types.currentItem().text()
        if selected_chart == 'Line Plot':
            ax.plot(ydata)
        elif selected_chart == 'Scatter Plot':
            ax.scatter(ydata.index, ydata)
        elif selected_chart == 'Stack Plot':
            pass
            # need to ask for more ydatas
            #ax.stackplot(days, apples, bananas, cherries, labels=['Apples', 'Bananas', 'Cherries'])
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
        elif selected_chart == 'Event Plot':
            ax.eventplot(ydata, orientation='horizontal', linelengths=0.8, color='blue')  
        elif selected_chart == 'Network Graph':
            G = nx.from_pandas_edgelist(df, 'source', 'destination', create_using=nx.DiGraph())
            nx.draw(G, ax=ax, with_labels=True, node_size=2000, node_color="skyblue", pos=nx.spring_layout(G), arrowstyle='-|>', arrowsize=12)

        ax.set_title(selected_chart)
        self.canvas.draw()

#END OF CLASS PlotWindow
