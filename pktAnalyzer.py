from sys import argv
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidgetItem, QFileDialog
from ui.dialogsWidgets import Dialogs
from ui.dataframeModel import DataFrameModel
from PyQt5.uic import loadUi
from sniffers.sniffer import PacketLoader
from utils.dataframeProvider import DataFrameProvider
from utils.fileLoader import FileLoader
from utils import aiPrompt
from sniffers.protocolsHandler import ProtocolHandler

# Subclass MainWindow to customize your application's main window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("ui/mainWindow.ui", self)
        self.selected_interface = None
        self.data_provider = DataFrameProvider()
        self.df_model = DataFrameModel(self.data_provider.alldata)
        self.protocols = ProtocolHandler()
        self.dialogs = Dialogs(self)
        self.repl = self.dialogs.repl
        self.options_window = self.dialogs.options_window
        self.plot_window = self.dialogs.plot_window
        self.find_window = self.dialogs.find_window
        self.tableview.setModel(self.df_model)
        self.tableview.verticalHeader().setVisible(True)
        ## connect signals
        self.tableview.selectionModel().currentChanged.connect(self.dialogs.packet_tree.show_packet)
        self.btn_start_logger.clicked.connect(self.start_stop_logger)
        self.inline_search.returnPressed.connect(self.btn_run_filter.click)
        self.btn_run_filter.clicked.connect(self.run_filter)
        self.filter_list.itemPressed.connect(self.update_values_list)
        self.filter_view.itemPressed.connect(self.select_filter)
        self.actionOpen.triggered.connect(self.open_file)
        self.actionSave.triggered.connect(self.save_file)
        self.actionOptions.triggered.connect(self.open_options_window)
        self.actionGraph.triggered.connect(self.plot_window.show)
        self.actionFind.triggered.connect(self.find_window.show)
        self.actionStart.triggered.connect(self.start_logger)
        self.actionOpen_REPL.triggered.connect(self.open_repl)        
    
    def open_options_window(self):
        if self.options_window.exec_(): # QDialog Accepted
            selected_items = self.options_window.interface_list.selectedItems()
            selected_texts = [item.text(0) for item in selected_items]
            if selected_texts:
                self.selected_interface = selected_texts

    # Close all windows when the main window is closed
    def closeEvent(self, event):
        self.repl.close()
        event.accept()

    def update_table(self, data=None):
        if data is None:
            data = self.data_provider.alldata
        self.df_model.update_data(data)
        self.set_details()

    def set_details(self, data_loaded=None):
        if data_loaded is None:
            alldata_rows = self.data_provider.alldata.shape[0]
            data_rows = self.df_model.rowCount()
            text = " Displaying: "
        else:
            alldata_rows, data_rows = data_loaded
            text = " Loading: "

        percentage = 0 if alldata_rows == 0 else (data_rows / alldata_rows) * 100
        alldata_rows = "Total Packets: " + str(alldata_rows)
        data_rows = text + str(data_rows)
        percentage = " (" + "{:.2f}".format(percentage) + "%)"
        self.display_details.setText( alldata_rows  +  data_rows + percentage )

    def set_status(self, status, warning_or_success='none'):
        self.display_status.setText(status)
        if (warning_or_success == 'warning'):
            self.display_status.setStyleSheet(
                "QLabel { color : red; background-color: transparent; }")
        else:
            self.display_status.setStyleSheet(
                "QLabel { color : black; background-color: transparent; }")   

    def open_file(self):
        file_dialog_filter = "All Files (*);;Parquet files (*.parquet);;LOG Files (*.log);;PCAP files (*.pcap *.pcapng);;CSV Files (*.csv)"
        options = QFileDialog.Options()
        filepath, selected_filter= QFileDialog.getOpenFileName(self, 'Open File', "", file_dialog_filter, options=options)
        if len(filepath) > 0:
            self.set_status("Reading file...")
            self.btn_start_logger.setText("Stop reading")
            #adjust chunk_size based on available memory (psutil.virtual_memory(), .available(), .total() )
            self.loader = FileLoader(self, filepath, selected_filter, chunk_size=1000)
            self.loader.data_loaded.connect(lambda data_loaded: self.set_details(data_loaded))
            self.loader.finished.connect(self.file_loaded)
            self.setWindowTitle(f"pktAnalyzer - {filepath}")
            self.loader.start()

    def save_file(self):
        file_dialog_filter = "Parquet file (*.parquet);;LOG File (*.log);;PCAP file (*.pcap *.pcapng);;CSV File (*.csv);;All Files (*)"
        options = QFileDialog.Options()
        filepath, selected_filter= QFileDialog.getSaveFileName(self, 'Save File', "", file_dialog_filter, options=options)
        #filepath = os.path.normpath(filepath)
        if len(filepath) > 0:
            self.set_status("Saving file...")
            self.data_provider.save_packets(filepath, selected_filter)
            self.set_status("File saved.", 'success')

    def file_loaded(self):
        self.btn_start_logger.setText("Start logging")
        self.actionRestart.setEnabled(True)        
        self.update_columns_list()
        self.set_status("File loaded.", 'success')
        self.df_model.update_data(self.data_provider.alldata)
        self.set_details()

    def update_columns_list(self):
        list_columns = self.data_provider.alldata.columns
        self.filter_list.clear()
        self.filter_view.clear()
        for word in list_columns:
            list_item = QListWidgetItem(str(word), self.filter_list)

    def query_data(self, filter_argument):
        if self.repl.isVisible():
            self.repl.input.setText(filter_argument)
            data = self.repl.evaluate()
        else:
            data = self.data_provider.query_filter(filter_argument)
        return data

    def update_values_list(self):
        column_name = self.filter_list.currentItem().text()
        list = self.df_model._data[column_name].drop_duplicates().sort_values().tolist()
        self.filter_view.clear()
        for word in list:
            list_item = QListWidgetItem(str(word), self.filter_view)

    def select_filter(self):
        column_name = self.filter_list.currentItem().text()
        argument = self.filter_view.currentItem().text()
        column_type = str(self.data_provider.alldata[column_name].dtype)
        if column_type in {'object', 'str', 'string'}:
            argument = f"'{argument}'"
        filter_argument = "df[df['"+ column_name + "'] == "+argument+"]"
        self.inline_search.setText(filter_argument)
        self.run_filter()

    def run_filter(self):
        filter_argument = self.inline_search.text()
        if len(filter_argument) > 0:
            try:
                self.set_status('Busy... Please wait!')
                if self.ai_checkBox.isChecked():
                    prompt = filter_argument
                    data = self.data_provider.df_toJSON()
                    prompt = aiPrompt.prepare_eval_prompt(data, prompt)
                    filter_argument = aiPrompt.get_completion (prompt)

                filtered_data = self.query_data(filter_argument)
                self.df_model.update_data(filtered_data)
                self.set_details()
                self.set_status('Ready.')
            except Exception as e:
                print (e)
                self.set_status('There was a problem with the calculation','warning')
        else:
            self.update_table()

    def start_logger(self):
        self.btn_start_logger.setText("Start logging")
        self.start_stop_logger()

    def start_stop_logger(self):
        current_text = self.btn_start_logger.text()
        if current_text.endswith("tart logging"):
            if current_text == "Start logging":
                self.data_provider.clear_data()
                self.df_model.update_data(self.data_provider.alldata)

            self.btn_start_logger.setText("Stop logging")
            self.actionStart.setEnabled(False)
            self.actionRestart.setEnabled(False)
            self.actionStop.setEnabled(True)            
            self.loader = PacketLoader(self, self.selected_interface, chunk_size=1)
            self.loader.packets_loaded.connect(self.update_table) ## CHange to another function to add just one row
            self.loader.start()
            self.set_status("Logging...") 
        else:
            self.loader.stop()
            self.loader = None
            if current_text == "Stop reading":
                self.data_provider.alldata_size = self.data_provider.alldata.shape[0]
                self.btn_start_logger.setText("Start logging")
            else:
                self.btn_start_logger.setText("Restart logging")
                self.actionRestart.setEnabled(True)
            self.actionStop.setEnabled(False)
            self.actionStart.setEnabled(True)
            self.set_status("Ready.")
            self.update_table()
            self.update_columns_list()

    def open_repl(self):
        if self.repl.isVisible():
            self.repl.hide()
        else:
            self.repl.show()

#END OF CLASS MainWindow

def openMainWindow(argv):
    app = QApplication(argv)
    window = MainWindow()
    window.show()
    app.exec()

def main():
    openMainWindow(argv)

if __name__ == "__main__":
    main()