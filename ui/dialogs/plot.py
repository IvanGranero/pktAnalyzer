from ui.plotWindow import Ui_Form
from PyQt5.QtWidgets import QDialog, QScrollArea, QWidget, QVBoxLayout
from PyQt5.QtCore import Qt, QCoreApplication
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from numpy import linspace
from pandas import to_datetime
import networkx as nx
import numpy as np
import pandas as pd

class PlotWindow(QDialog, Ui_Form):
    def __init__(self, df_model):
        super().__init__()
        self.setupUi(self)
        self.df_model = df_model
        self.setup_ui()
        self.fig_width = 10
        self.fig_height = 5  # Height for each subplot

    def setup_ui(self):
        self.scroll = QScrollArea()
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout()
        self.scroll_content.setLayout(self.scroll_layout)

        self.scroll.setWidget(self.scroll_content)
        self.scroll.setWidgetResizable(True)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.plot_layout.addWidget(self.scroll)
        self.btn_plot.clicked.connect(self.plot)
        self.btn_multipleplots.clicked.connect(self.multiple_plots)
        self.update_dropdowns()

    def update_dropdowns(self):
        columns = self.df_model._data.columns
        self.dropdown_yaxis.clear()
        self.dropdown_yaxis.addItems(columns)
        self.dropdown_xaxis.clear()
        self.dropdown_xaxis.addItem("Index")
        self.dropdown_xaxis.addItems(columns)
        self.dropdown_groupby.clear()
        self.dropdown_groupby.addItems(columns)

    def multiple_plots(self):
        self.labelstatus.setText("Busy plotting multiple plots...")
        QCoreApplication.processEvents()
        df = self.df_model._data
        #df['time'] = to_datetime(df['time'], unit='s')
        yaxis_text = self.dropdown_yaxis.currentText()
        xaxis_text = self.dropdown_xaxis.currentText()
        groupby_text = self.dropdown_groupby.currentText()
        keys_in_group = df[groupby_text].unique()
        
        self.clear_plots()
        # Add new subplots
        for key in keys_in_group:
            subset = df[df[groupby_text] == key]
            fig = Figure(figsize=(self.fig_width, self.fig_height))
            canvas = FigureCanvas(fig)
            ax = fig.add_subplot(111)
            xdata = subset[xaxis_text] if xaxis_text != 'Index' else subset.index
            self.add_subplot(ax, xdata, subset[yaxis_text], f"{groupby_text} = {key}")
            canvas.setMinimumSize(canvas.size())
            self.scroll_layout.addWidget(canvas)
            del fig, canvas
        self.refresh_canvas()
        self.labelstatus.setText("Ready.")

    def plot(self):
        self.labelstatus.setText("Busy plotting...")
        QCoreApplication.processEvents()        
        df = self.df_model._data
        yaxis_text = self.dropdown_yaxis.currentText()
        ydata = df[yaxis_text]
        xaxis_text = self.dropdown_xaxis.currentText()
        xdata = df.index if xaxis_text == 'Index' else df[xaxis_text]
        self.clear_plots()
        fig = Figure(figsize=(self.fig_width, self.fig_height))
        canvas = FigureCanvas(fig)        
        ax = fig.add_subplot(111)
        self.add_subplot(ax, xdata, ydata, yaxis_text)
        canvas.setMinimumSize(canvas.size())
        self.scroll_layout.addWidget(canvas)
        toolbar = NavigationToolbar(canvas, self)
        self.scroll_layout.addWidget(toolbar)
        del fig, canvas, toolbar
        self.refresh_canvas()
        self.labelstatus.setText("Ready.")        

    def add_subplot(self, ax, xdata, ydata, title):
        xdata = xdata.to_numpy()
        ydata = ydata.to_numpy()

        max_points = 1000
        if len(ydata) > max_points:
            idx = np.linspace(0, len(ydata) - 1, max_points).astype(int)
            ydata = ydata[idx]
            xdata = xdata[idx]

        selected_chart = self.chart_types.currentItem().text()
        if selected_chart == 'Line Plot':
            ax.plot(xdata, ydata)
        elif selected_chart == 'Scatter Plot':
            ax.scatter(xdata, ydata)
        elif selected_chart == 'Stack Plot':
            pass  # Additional handling required for multiple ydata series
        elif selected_chart == 'Bar Chart':
            ydata_counts = pd.Series(ydata).value_counts()
            ax.bar(ydata_counts.index, ydata_counts)
        elif selected_chart == 'Pie Chart':
            ydata_counts = pd.Series(ydata).value_counts()
            ax.pie(ydata_counts, labels=ydata_counts.index)
        elif selected_chart == 'Histogram':
            ax.hist(ydata)
        elif selected_chart == 'Box Plot':
            ax.boxplot(ydata)
        elif selected_chart == 'Event Plot':
            ax.eventplot(ydata, orientation='horizontal', linelengths=0.8, color='blue')
        elif selected_chart == 'Network Graph':
            G = nx.from_pandas_edgelist(self.df_model._data, 'source', 'destination', create_using=nx.DiGraph())
            nx.draw(G, ax=ax, with_labels=True, node_size=2000, node_color="skyblue", pos=nx.spring_layout(G), arrowstyle='-|>', arrowsize=12)

        ax.set_title(title)
        return ax
    
    def clear_plots(self):
        for i in reversed(range(self.scroll_layout.count())):
            widget_to_remove = self.scroll_layout.itemAt(i).widget()
            if widget_to_remove is not None:
                widget_to_remove.setParent(None)

    def refresh_canvas(self):
        self.scroll_content.adjustSize()
        self.scroll.updateGeometry()
        self.scroll.repaint()
