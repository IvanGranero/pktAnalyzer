from PyQt5.QtWidgets import QDialog
from PyQt5.uic import loadUi
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import networkx as nx


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
        self.update_dropdowns()

    def update_dropdowns(self):
        columns = self.mainwindow.df_model._data.columns
        self.dropdown_yaxis.clear()
        self.dropdown_yaxis.addItems(columns)
        self.dropdown_xaxis.clear()
        self.dropdown_xaxis.addItem("Index")
        self.dropdown_xaxis.addItems(columns)      

    def plot(self):
        df = self.mainwindow.df_model._data
        yaxis_text = self.dropdown_yaxis.currentText()
        ydata = df.loc[:, yaxis_text]

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
