from dataclasses import dataclass
import signal, sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidgetItem, QFileDialog, QTreeWidgetItem
from ui.dialogsWidgets import REPL, OptionsWindow, PlotWindow
from ui.dataframeModel import DataFrameModel
from PyQt5.uic import loadUi
from sniffers.sniffer import PacketLoader
from sniffers.protocols import hex_to_packet
from utils.dataframeProvider import DataFrameProvider
from utils.fileLoader import FileLoader
import utils.aiPrompt
import matplotlib.pyplot as plt

# Subclass MainWindow to customize your application's main window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("ui/mainWindow.ui", self)
        self.options_window = None  # Initialize OptionsWindow
        self.plot_window = None # Initialize PlotWindow
        for word in ['eth', 'can']:
            list_item = QListWidgetItem(str(word), self.network_list)
        self.btn_start_logger.clicked.connect(self.start_stop_logger)
        self.inline_search.returnPressed.connect(self.btn_run_filter.click)
        self.btn_run_filter.clicked.connect(self.run_filter)
        self.filter_list.itemPressed.connect(self.update_values_list)
        self.filter_view.itemPressed.connect(self.select_filter)
        self.actionOpen.triggered.connect(self.open_file)
        self.actionSave.triggered.connect(self.save_file)
        self.actionOptions.triggered.connect(self.open_options_window)
        self.actionAscii.triggered.connect(self.find_strings)
        self.actionGraph.triggered.connect(self.open_plot_window)
        self.actionStart.triggered.connect(self.start_logger)
        self.actionOpen_REPL.triggered.connect(self.open_repl)
        self.data_provider = DataFrameProvider()
        self.repl = REPL(self.data_provider)
        self.df_model = DataFrameModel(self.data_provider)
        self.tableview.setModel(self.df_model)
        self.tableview.verticalHeader().setVisible(False)
        self.tableview.clicked.connect(self.show_packet)
                        
    def open_options_window(self):
        if self.options_window is None:
            self.options_window = OptionsWindow()
        self.options_window.exec_() # Open as a modal dialog

    # Close all windows when the main window is closed
    def closeEvent(self, event):
        self.repl.close()
        event.accept()

    def set_status(self, status, warning_or_success='none'):
        self.display_status.setText(status)
        if (warning_or_success == 'warning'):
            self.display_status.setStyleSheet(
                "QLabel { color : red; background-color: transparent; }")
        elif (warning_or_success == 'success'):
            self.display_status.setStyleSheet(
                "QLabel { color : black; background-color: transparent; }")   

    def open_file(self):
        file_dialog_filter = "Parquet files (*.parquet);;LOG Files (*.log);;PCAP files (*.pcap *.pcapng);;CSV Files (*.csv);;All Files (*)"
        options = QFileDialog.Options()
        filepath, _= QFileDialog.getOpenFileName(self, 'Open File', "", file_dialog_filter, options=options)
        if len(filepath) > 0:
            self.set_status("Reading file...")
            self.data_provider.clear_data()
            self.df_model.set_dataframe()
            self.btn_start_logger.setText("Stop reading")
            self.loader = FileLoader(self.data_provider, filepath, chunk_size=1000)
            self.loader.data_loaded.connect(self.df_model.set_dataframe)
            self.loader.finished.connect(self.file_loaded)
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

    def find_strings(self):
        selected_items = self.tableview.selectedItems()
        if selected_items:
            column_index = self.tableview.currentColumn()
            column_name = self.tableview.horizontalHeaderItem(column_index).text()
            self.set_status('Busy... Please wait!')
            self.data_provider.add_strings_column(column_name) #add min_length as argument
            self.update_columns_list()
            self.set_status('Ready.')
        else:
            self.set_status("Select a column to convert to ASCII.")

    def open_plot_window(self):
        if self.plot_window is None:
            self.plot_window = PlotWindow(self) # Pass self (MainWindow instance) as parent
        self.plot_window.show()

    def file_loaded(self):
        self.btn_start_logger.setText("Start logging")
        self.actionRestart.setEnabled(True)
        self.update_columns_list()
        #self.tableview.cellClicked.emit(0, 0)
        self.set_status("Ready.")

    def update_columns_list(self):
        list_columns = self.data_provider.data.columns
        self.filter_list.clear()
        self.filter_view.clear()
        for word in list_columns:
            list_item = QListWidgetItem(str(word), self.filter_list)

    def query_data(self, filter_argument, return_data=False):
        if self.repl.isVisible():
            self.repl.input.setText(filter_argument)
            data = self.repl.evaluate()
        else:
            data = self.data_provider.query_filter(filter_argument, return_data)
        if return_data:
            return data

    def update_values_list(self):
        column_name = self.filter_list.currentItem().text()
        filter_argument = "sorted(df['"+column_name+"'].unique())"
        list = self.query_data(filter_argument, True)
        self.filter_view.clear()
        for word in list:
            list_item = QListWidgetItem(str(word), self.filter_view)

    def select_filter(self):
        column_name = self.filter_list.currentItem().text()
        argument = self.filter_view.currentItem().text()
        column_type = self.data_provider.data[column_name].dtype
        if column_type == 'str' or column_type == 'string':
            argument = '"' + argument + '"'
        #filter_argument = column_name +' == ' + argument
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
                    prompt = utils.aiPrompt.prepare_eval_prompt(data, prompt)
                    filter_argument = utils.aiPrompt.get_completion (prompt)

                self.query_data(filter_argument)                
                self.df_model.set_dataframe()
                self.set_status('Ready.')
            except Exception as e:
                print (e)
                self.set_status('There was a problem with the calculation','warning')
        else:
            self.set_status("Input a query e.g. identifier == 310 or check the AI box and use natural language.")

    def start_logger(self):
        self.btn_start_logger.setText("Start logging")
        self.start_stop_logger()

    def start_stop_logger(self):
        current_text = self.btn_start_logger.text()
        if current_text.endswith("tart logging"):
            if current_text == "Start logging":
                self.data_provider.clear_data()
                self.df_model.set_dataframe()

            self.btn_start_logger.setText("Stop logging")
            self.actionStart.setEnabled(False)
            self.actionRestart.setEnabled(False)
            self.actionStop.setEnabled(True)            
            # CHange to read the interface from the options settings, give it as a parameter to PacketLoader
            iface = self.network_list.currentItem().text()
            self.loader = PacketLoader(self.data_provider, iface, chunk_size=1)
            self.loader.packets_loaded.connect(self.df_model.set_dataframe)
            self.loader.start()
            self.set_status("Logging...") 
        else:              # (current_text == "Stop logging" or current_text == "Stop reading"):
            self.loader.stop()
            self.loader = None
            if current_text == "Stop reading":
                self.btn_start_logger.setText("Restart reading")
            else:
                self.btn_start_logger.setText("Restart logging")
                self.actionRestart.setEnabled(True)
            self.actionStop.setEnabled(False)
            self.actionStart.setEnabled(True)
            self.set_status("Ready.")
            self.update_columns_list()

    def open_repl(self):
        if self.repl.isVisible():
            self.repl.hide()
        else:
            self.repl.show()

    ## Need to move to its own class similar to DataFrameWidget
    def show_packet(self, index):
        row = index.row()
        column = index.column()
        #self.tableview.selectRow(row)
        data = self.data_provider.data.iloc[row]['data']
        proto = self.data_provider.data.iloc[row]['protocol']
        dataprint =  bytes.fromhex(data).decode('latin1')
        data = ' '.join(data[i:i+2] for i in range(0, len(data), 2))
        self.data_inspector.setText(data + "\n" +  dataprint)
        self.packet_inspector.clear()
        # extract the packet from the packetlist
        #layer = self.data_provider.packetlist[row]
        layer = hex_to_packet(data, proto)
        while layer:
            layer_item = QTreeWidgetItem([layer.summary()])
            self.packet_inspector.addTopLevelItem(layer_item)
            # add all the packet fields
            for field_name, field_val in layer.fields.items():
                field_item = QTreeWidgetItem([f"{field_name}: {field_val}"])
                layer_item.addChild(field_item)

            layer_item.setExpanded(True)
            layer = layer.payload if layer.payload else None
#END OF CLASS MainWindow

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