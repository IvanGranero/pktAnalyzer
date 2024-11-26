from PyQt5.QtWidgets import QScrollArea, QWidget, QVBoxLayout
from PyQt5.QtCore import Qt, QCoreApplication
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from numpy import linspace
from pandas import to_datetime
import networkx as nx
import numpy as np
import pandas as pd
from PyQt5 import QtCore, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(925, 727)
        self.horizontalLayout = QtWidgets.QHBoxLayout(Form)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.plot_layout = QtWidgets.QVBoxLayout()
        self.plot_layout.setObjectName("plot_layout")
        self.horizontalLayout.addLayout(self.plot_layout)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.chart_types = QtWidgets.QListWidget(Form)
        self.chart_types.setObjectName("chart_types")
        item = QtWidgets.QListWidgetItem()
        self.chart_types.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.chart_types.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.chart_types.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.chart_types.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.chart_types.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.chart_types.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.chart_types.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.chart_types.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.chart_types.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.chart_types.addItem(item)
        self.verticalLayout.addWidget(self.chart_types)
        self.labely = QtWidgets.QLabel(Form)
        self.labely.setObjectName("labely")
        self.verticalLayout.addWidget(self.labely)
        self.dropdown_yaxis = QtWidgets.QComboBox(Form)
        self.dropdown_yaxis.setObjectName("dropdown_yaxis")
        self.verticalLayout.addWidget(self.dropdown_yaxis)
        self.labelx = QtWidgets.QLabel(Form)
        self.labelx.setObjectName("labelx")
        self.verticalLayout.addWidget(self.labelx)
        self.dropdown_xaxis = QtWidgets.QComboBox(Form)
        self.dropdown_xaxis.setObjectName("dropdown_xaxis")
        self.verticalLayout.addWidget(self.dropdown_xaxis)
        self.btn_plot = QtWidgets.QPushButton(Form)
        self.btn_plot.setObjectName("btn_plot")
        self.verticalLayout.addWidget(self.btn_plot)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.labelgroupby = QtWidgets.QLabel(Form)
        self.labelgroupby.setObjectName("labelgroupby")
        self.verticalLayout.addWidget(self.labelgroupby)
        self.dropdown_groupby = QtWidgets.QComboBox(Form)
        self.dropdown_groupby.setObjectName("dropdown_groupby")
        self.verticalLayout.addWidget(self.dropdown_groupby)
        self.btn_multipleplots = QtWidgets.QPushButton(Form)
        self.btn_multipleplots.setObjectName("btn_multipleplots")
        self.verticalLayout.addWidget(self.btn_multipleplots)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.labelstatus = QtWidgets.QLabel(Form)
        self.labelstatus.setObjectName("labelstatus")
        self.verticalLayout.addWidget(self.labelstatus)
        self.verticalLayout.setStretch(10, 50)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.horizontalLayout.setStretch(0, 80)
        self.horizontalLayout.setStretch(1, 20)

        self.retranslateUi(Form)
        self.chart_types.setCurrentRow(0)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Data Visualization"))
        __sortingEnabled = self.chart_types.isSortingEnabled()
        self.chart_types.setSortingEnabled(False)
        item = self.chart_types.item(0)
        item.setText(_translate("Form", "Line Plot"))
        item = self.chart_types.item(1)
        item.setText(_translate("Form", "Scatter Plot"))
        item = self.chart_types.item(2)
        item.setText(_translate("Form", "Stack Plot"))
        item = self.chart_types.item(3)
        item.setText(_translate("Form", "Bar Chart"))
        item = self.chart_types.item(4)
        item.setText(_translate("Form", "Pie Chart"))
        item = self.chart_types.item(5)
        item.setText(_translate("Form", "Histogram"))
        item = self.chart_types.item(6)
        item.setText(_translate("Form", "Heat Map"))
        item = self.chart_types.item(7)
        item.setText(_translate("Form", "Box Plot"))
        item = self.chart_types.item(8)
        item.setText(_translate("Form", "Event Plot"))
        item = self.chart_types.item(9)
        item.setText(_translate("Form", "Network Graph"))
        self.chart_types.setSortingEnabled(__sortingEnabled)
        self.labely.setText(_translate("Form", "Y-Axis"))
        self.labelx.setText(_translate("Form", "X-Axis"))
        self.btn_plot.setText(_translate("Form", "Generate Plot"))
        self.labelgroupby.setText(_translate("Form", "Group by:"))
        self.btn_multipleplots.setText(_translate("Form", "Show Grouped Plots"))
        self.labelstatus.setText(_translate("Form", "Ready."))


class PlotWindow(QWidget, Ui_Form):
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
