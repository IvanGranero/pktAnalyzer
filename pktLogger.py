import signal, sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QTableWidget, QTableWidgetItem, QListWidgetItem, QFileDialog
from PyQt5.uic import loadUi
import threading
import sniffers.canPkts
import sniffers.ethernetPkts
import utils.cudfPkts
import utils.aiPrompt
import pandas as pd


# Subclass DataFrameWidget to display data
class DataFrameWidget(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

    def clear_table(self):
        self.clearContents()

    def append_data(self, new_data):
        print (new_data)
        if self.rowCount() == 0:
            print ("NEW")
            self.setRowCount(new_data.shape[0])
            self.setColumnCount(new_data.shape[1])
            self.setHorizontalHeaderLabels(new_data.columns)
            self.verticalHeader().setVisible(False)
            self.setSortingEnabled(True)

        current_row_count = self.rowCount()
        self.setRowCount(current_row_count + new_data.shape[0])
        
        for row in range(new_data.shape[0]):
            for col in range(new_data.shape[1]):
                self.setItem(current_row_count + row, col, QTableWidgetItem(str(new_data.iat[row, col])))


# Subclass MainWindow to customize your application's main window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.w = None
        loadUi("ui/mainWindow.ui", self)        
        for word in ['eth', 'can']:
            list_item = QListWidgetItem(str(word), self.network_list)
        self.btn_start_logger.clicked.connect(self.start_stop_logger)
        self.inline_search.returnPressed.connect(self.btn_run_filter.click)
        self.btn_run_filter.clicked.connect(self.run_filter)
        self.btn_refresh.clicked.connect(self.show_data)
        self.filter_list.itemPressed.connect(self.update_filters)
        self.filter_view.itemPressed.connect(self.select_filter)
        self.actionOpen.triggered.connect(self.open_file)     
        self.start_stop = 0

    def set_status(self, status, warning_or_success='none'):
        self.display_status.setText(status)
        if (warning_or_success == 'warning'):
            self.display_status.setStyleSheet(
                "QLabel { color : red; background-color: transparent; }")
        elif (warning_or_success == 'success'):
            self.display_status.setStyleSheet(
                "QLabel { color : lightgreen; background-color: transparent; }")        

    def open_file(self):
        filepath, dummy = QFileDialog.getOpenFileName(self, 'Open File')
        if len(filepath) > 0:
            self.loader = cudfPkts.DataFrameLoader(filepath)
            self.loader.data_loaded.connect(self.tableview.append_data)
            self.loader.start()

    def show_data(self):
        self.inline_search.setText("index==index")
        self.run_filter()

    def update_filters(self):
        column_name = self.filter_list.currentItem().text()                
        list = cudfPkts.eval_filter('alldata.'+column_name+'.sort_values().unique()')
        self.filter_view.clear() 
        for word in list:
            list_item = QListWidgetItem(str(word), self.filter_view)

    def select_filter(self):
        column_name = self.filter_list.currentItem().text()
        argument = self.filter_view.currentItem().text()
        filter_argument = column_name +' == ' + argument
        self.inline_search.setText(filter_argument)
        self.run_filter()

    def run_filter(self):        
        filter_argument = self.inline_search.text()
        if len(filter_argument) > 0:
            try:
                self.set_status('Busy... Please wait!')

                if self.ai_checkBox.isChecked():
                    prompt = filter_argument
                    data = cudfPkts.df_toJSON()
                    prompt = aiPrompt.prepare_prompt(data, prompt)
                    response = aiPrompt.get_completion (prompt)                    
                    self.set_status(response)
                    filter_argument = response
                
                data = cudfPkts.query_filter(filter_argument)                

                self.tableview.refresh_data(data)
                
                list_columns = data.columns
                self.filter_list.clear() 
                for word in list_columns:
                    list_item = QListWidgetItem(str(word), self.filter_list)
                self.set_status('Ready.')
            except Exception as e:
                print (e)
                self.set_status('There was a problem with the calculation','warning')
        else:
            self.set_status("Input a query e.g. identifier == 310 or check the AI box and use natural language.")



    def start_stop_logger(self):
        if (self.start_stop):
            self.start_stop = 0
            self.stop_event.set()            
            self.btn_start_logger.setText("Start Logging")
        else:
            self.btn_start_logger.setText("Stop Logging")
            self.start_stop = 1
            self.stop_event = threading.Event()
            thread = ethernetPkts.NetworkThread(self.stop_event)
            thread.start()
            thread.join()
            self.tableview.append_data(pd.DataFrame(thread.result))


def openMainWindow(argv):
    app = QApplication(argv)    
    window = MainWindow()
    window.show()
    app.exec()


def handler_interrupt(signal, frame):
    sys.exit(0)


def main():
    # add try catch to all 
    signal.signal(signal.SIGINT, handler_interrupt)
    if(len(sys.argv) > 2):
        # to start logging thread from the command line e.g. pktLogger can0 -s "flag{"
        print ("command line options not available yet")   

    openMainWindow(sys.argv)
    

if __name__ == "__main__":
    main()