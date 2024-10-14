from PyQt5.QtCore import QThread, pyqtSignal
import pyarrow.parquet as pq
import pandas as pd
from scapy.layers.can import CandumpReader
from re import match

class FileLoader(QThread):
    data_loaded = pyqtSignal(pd.DataFrame)
    finished = pyqtSignal()

    def __init__(self, provider, file_path, chunk_size=100, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.chunk_size = chunk_size
        self.provider = provider
        self._is_running = True

    def run(self):
        file_extension = self.file_path.split('.')[-1].lower()
        if file_extension == 'gzip':
            file_extension = self.file_path.split('.')[-2].lower()
        
        if file_extension == 'log':                                  
            for chunk in self.canlog_reader_chunked():
                if not self._is_running:
                    break                
                self.provider.alldata = pd.concat([self.provider.alldata, chunk], ignore_index=True)
                self.data_loaded.emit(chunk)

        elif file_extension == 'csv':
            for chunk in pd.read_csv(self.file_path, chunksize=self.chunk_size):
                if not self._is_running:
                    break                
                self.provider.alldata = pd.concat([self.provider.alldata, chunk], ignore_index=True)    
                self.data_loaded.emit(chunk)

        elif file_extension == 'parquet':
            table = pq.read_table(self.file_path)
            self.provider.alldata = table.to_pandas()
            self.data_loaded.emit(self.provider.alldata)            

        else:
            print("Unsupported file type.") # NEED TO RAISE EXCEPTION TO CHANGE STATUS IN THE GUI

        self.provider.alldata = self.provider.alldata.convert_dtypes()
        self.provider.alldata = self.provider.alldata.apply(lambda col: col.astype('int64') if col.dtype == 'Int64' else col)
        self.finished.emit()

    def stop(self):
        self._is_running = False

    def canlog_reader_chunked(self): # (self, self.file_path, chunksize=self.chunk_size)):
            data = []

            with open(self.file_path, 'r') as file:
                for line in file:

                    m = match(r'\((.*?)\) (\w+) (\w+)(##)?(.*)', line.strip())
                    if m:
                        timestamp, interface, identifier, double_hash, rest = m.groups()
                        
                        if double_hash:
                            flags = rest[0]
                            data_field = rest[1:]
                        else:
                            flags = None
                            data_field = rest[1:]
                        
                        length = len(data_field) // 2  # Each byte is represented by 2 hex digits
                        data.append([float(timestamp), interface, identifier, flags, length, data_field])
    
                        if len(data) > self.chunk_size:
                            yield pd.DataFrame(data, columns=['timestamp', 'interface', 'identifier', 'flags', 'length', 'data'])
                            data = []
