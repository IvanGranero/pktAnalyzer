from PyQt5.QtCore import QThread, pyqtSignal
import pandas as pd
from sniffers.protocols import protocol_handler
from scapy.all import PcapReader
from scapy.layers.can import CandumpReader


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
            dfs = []
            with CandumpReader(self.file_path) as log_reader:
                for i, packet in enumerate(log_reader, start=1):
                    df = protocol_handler(packet)
                    dfs.append(df)
                    if i % self.chunk_size == 0:
                        df_chunk = pd.concat(dfs, ignore_index=True)
                        self.provider.alldata = pd.concat([self.provider.alldata, df_chunk], ignore_index=True)
                        self.data_loaded.emit(df_chunk)
                        dfs = []
                if dfs:
                    df_chunk = pd.concat(dfs, ignore_index=True)
                    self.provider.alldata = pd.concat([self.provider.alldata, df_chunk], ignore_index=True)
                    self.data_loaded.emit(df_chunk)

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
