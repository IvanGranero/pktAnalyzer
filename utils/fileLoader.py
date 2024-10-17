from PyQt5.QtCore import QThread, pyqtSignal
import pandas as pd
from re import compile
from sniffers.protocols import protocol_handler
from scapy.all import PcapReader


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
        
        if file_extension == 'pcap' or file_extension=='pcapng':
            with PcapReader(self.file_path) as pcap_reader:
                notEOF = True
                while notEOF:
                    try:
                        packets = [pcap_reader.read_packet() for _ in range(self.chunk_size)]
                    except EOFError:
                        notEOF = False
                    if not packets:
                        break
                    dfs = []
                    for packet in packets:
                        df = protocol_handler(packet)
                        dfs.append(df)
                    dfs = pd.concat(dfs, ignore_index=True)
                    self.provider.alldata = pd.concat([self.provider.alldata, dfs], ignore_index=True)
                    self.data_loaded.emit(dfs)

        elif file_extension == 'log':
            # Change to use scapy reader and send it to the protocols handler
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
            self.provider.alldata = pd.read_parquet(self.file_path)
            self.data_loaded.emit(self.provider.alldata)

        else:
            print("Unsupported file type.") # NEED TO RAISE EXCEPTION TO CHANGE STATUS IN THE GUI

        self.provider.alldata = self.provider.alldata.convert_dtypes()
        self.provider.alldata = self.provider.alldata.apply(lambda col: col.astype('int64') if col.dtype == 'Int64' else col)
        self.finished.emit()

    def stop(self):
        self._is_running = False

   
    def canlog_reader_chunked(self): # (self, self.file_path, chunksize=self.chunk_size)):
            pattern = compile(r'\((.*?)\) (\w+) (\w+)(##)?(.*)')        
            data = []
            with open(self.file_path, 'r') as file:
                for line in file:
                    m = pattern.match(line.strip())
                    if m:
                        timestamp, interface, identifier, double_hash, rest = m.groups()
                        flags = rest[0] if double_hash else 0
                        data_field = rest[1:]
                        length = len(data_field) // 2  # Each byte is represented by 2 hex digits
                        data.append([float(timestamp), interface, identifier, flags, length, data_field])
                        if len(data) > self.chunk_size:
                            yield pd.DataFrame(data, columns=['timestamp', 'interface', 'identifier', 'flags', 'length', 'data'])
                            data = []
            if data:
                yield pd.DataFrame(data, columns=['timestamp', 'interface', 'identifier', 'flags', 'length', 'data'])


