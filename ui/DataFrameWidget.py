from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem

# Subclass DataFrameWidget to display data
class DataFrameWidget(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

    def clear_table(self):
        self.clearContents()

    def append_data(self, new_data):
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

        #self.resizeColumnsToContents()
        #self.resizeRowsToContents()