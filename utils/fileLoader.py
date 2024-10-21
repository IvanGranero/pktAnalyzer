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

                    dfs = [protocol_handler(packet) for packet in packets]
                    dfs = pd.concat(dfs, ignore_index=True)
                    dfs = self.provider.append_data(dfs, packets)
                    self.data_loaded.emit(dfs)

        elif file_extension == 'log':
            dfs = []
            pkts = []
            with CandumpReader(self.file_path) as log_reader:
                for i, packet in enumerate(log_reader, start=1):
                    df = protocol_handler(packet)
                    dfs.append(df)
                    pkts.append(packet)
                    if i % self.chunk_size == 0:
                        df_chunk = pd.concat(dfs, ignore_index=True)
                        df_chunk = self.provider.append_data(df_chunk, pkts)
                        self.data_loaded.emit(df_chunk)
                        dfs = []
                        pkts = []
                if dfs:
                    df_chunk = pd.concat(dfs, ignore_index=True)
                    df_chunk = self.provider.append_data(df_chunk, pkts)
                    self.data_loaded.emit(df_chunk)

        elif file_extension == 'csv':
            for chunk in pd.read_csv(self.file_path, chunksize=self.chunk_size):
                if not self._is_running:
                    break                
                chunk = self.provider.append_data(chunk)
                self.data_loaded.emit(chunk)

        elif file_extension == 'parquet':
            chunk = pd.read_parquet(self.file_path)
            chunk = self.provider.append_data(chunk)              
            self.data_loaded.emit(chunk)

        else:
            print("Unsupported file type.") # NEED TO RAISE EXCEPTION TO CHANGE STATUS IN THE GUI

        self.finished.emit()

    def stop(self):
        self._is_running = False
