from PyQt5.QtCore import QAbstractTableModel, Qt

class DataFrameModel(QAbstractTableModel):
    def __init__(self, provider, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self.provider = provider

    def rowCount(self, parent=None):
        return self.provider.data.shape[0]

    def columnCount(self, parent=None):
        return self.provider.data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None
        value = self.provider.data.iloc[index.row(), index.column()]
        return str(value)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return self.provider.data.columns[section]
        else:
            return str(self.provider.data.index[section])

    def set_dataframe(self):
        self.beginResetModel()
        self.endResetModel()

    def append_existing_row(self):
        start_row = self.df.shape[0] - 1  # Last row index
        self.beginInsertRows(QModelIndex(), start_row, start_row)
        self.endInsertRows()        

