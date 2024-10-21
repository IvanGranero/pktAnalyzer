from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem

# Subclass DataFrameWidget to display data
class DataFrameWidget(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.no_column = []

    def clear_table(self):
        self.clearContents()
        self.setRowCount(0)
        self.setColumnCount(0)
        self.no_column.clear()

    def append_data(self, new_data, liveview=False):
        current_row_count = self.rowCount()

        if current_row_count == 0:
            self.setRowCount(new_data.shape[0])
            self.setColumnCount(new_data.shape[1])
            self.setHorizontalHeaderLabels(new_data.columns)
            self.verticalHeader().setVisible(False)
            self.setSortingEnabled(True)
        else:
            self.setRowCount(current_row_count + new_data.shape[0])
        
        for row in range(new_data.shape[0]):
            for col in range(new_data.shape[1]):
                self.setItem(current_row_count + row, col, QTableWidgetItem(str(new_data.iat[row, col])))

        # keeps the index list
        self.no_column.extend( new_data.iloc[:, 0].tolist() )

        # adjusting size of column no.
        self.resizeColumnToContents(0)
        # Need to add user settings for chose live view or not
        if liveview:
            last_row_index = self.rowCount()-1
            self.scrollToBottom()  # Scroll to the bottom of the table
            self.cellClicked.emit(last_row_index, 0)  # Adjust the column index if needed


        