from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem

# Subclass DataFrameWidget to display data
class DataFrameWidget(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

    def clear_table(self):
        self.clearContents()
        self.setRowCount(0)
        self.setColumnCount(0)


    def append_data(self, new_data, liveview=False):
        current_row_count = self.rowCount()

        if current_row_count == 0:            
            self.setRowCount(new_data.shape[0])
            self.setColumnCount(new_data.shape[1])
            self.setHorizontalHeaderLabels(new_data.columns)
            #self.verticalHeader().setVisible(False)
            self.setSortingEnabled(True)
        else:
            self.setRowCount(current_row_count + new_data.shape[0])
        
        for row in range(new_data.shape[0]):
            for col in range(new_data.shape[1]):
                self.setItem(current_row_count + row, col, QTableWidgetItem(str(new_data.iat[row, col])))

        #self.resizeColumnsToContents()
        #self.resizeRowsToContents()
        if liveview:
            last_row_index = self.rowCount()-1
            self.scrollToBottom()  # Scroll to the bottom of the table
            # Need to add user settings for chose live view or not
            # Manually emit the cellClicked signal
            self.cellClicked.emit(last_row_index, 0)  # Adjust the column index if needed


        