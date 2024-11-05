# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'plotWindow.ui'
#
# Created by: PyQt5 UI code generator 5.15.11
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


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
        self.verticalLayout.setStretch(6, 50)
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
        self.btn_plot.setText(_translate("Form", "Plot"))