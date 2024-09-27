
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QTableWidgetItem
#from PyQt5 import QtWidgets
from PyQt5.uic import loadUi
import logThread

# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.w = None        
        loadUi("gui/mainWindow.ui", self)      
        self.btn_start_logger.clicked.connect(self.start_stop_logger)
        self.inline_search.returnPressed.connect(self.btn_run_filter.click)
        self.btn_run_filter.clicked.connect(self.run_filter)
        self.btn_refresh.clicked.connect(self.show_data)
        self.start_stop = 0

    def set_status(self, status, warning_or_success='none'):
        self.display_status.setText(status)
        if (warning_or_success == 'warning'):
            self.display_status.setStyleSheet(
                "QLabel { color : red; background-color: transparent; }")
        elif (warning_or_success == 'success'):
            self.display_status.setStyleSheet(
                "QLabel { color : lightgreen; background-color: transparent; }")        

    def show_data(self):
        self.inline_search.setText("index==index")
        self.run_filter()

    def run_filter(self):
        filter_argument = self.inline_search.text()
        if len(filter_argument) > 0:
            try:
                self.set_status('Busy... Please wait!')
                data = logThread.runFilter(filter_argument)
                self.tableview.clearContents()
                self.tableview.setRowCount(len(data.index))
                self.tableview.setColumnCount(len(data.columns))
                self.tableview.verticalHeader().setVisible(False)
                self.tableview.setSortingEnabled(True)        
                num_rows = len(data.index)
                num_columns = len(data.columns)
                for i in range(num_rows):
                    for j in range(num_columns):
                        self.tableview.setItem(i, j, QTableWidgetItem(str(data.iat[i, j])))    
                self.tableview.resizeColumnsToContents()
                self.tableview.resizeRowsToContents()
                self.set_status('Ready.')
            except:
                self.set_status('There was a problem with your FILTER argument','warning')
        else:
            self.set_status("type a filter argument e.g. arbitration_id == 310")
    
    def start_stop_logger(self):
        if (self.start_stop):
            logThread.stopLogger()
            self.btn_start_logger.setText("Start LoggerThread")
            self.start_stop = 0
        else:
            self.w = StartLoggerWindow()
            self.w.show()
            if ( self.w.exec_() ): #returns 1 if clicked OK
                print (self.w.inline_stop.text())

                logThread.startLogger()
                self.btn_start_logger.setText("Stop LoggerThread")       
                self.start_stop = 1

            
class StartLoggerWindow(QDialog):
    def __init__(self):
        super().__init__()
        loadUi("gui/startLogger.ui", self)


def openMainWindow(argv):

    app = QApplication(argv)

    window = MainWindow()
    window.show()

    app.exec()