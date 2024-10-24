from PyQt5.QtCore import QThread, pyqtSignal
import pandas as pd
from sniffers.protocols import protocol_handler
from scapy.all import PcapReader
from scapy.layers.can import CandumpReader

class FileLoader(QThread):
    data_loaded = pyqtSignal()
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
                while notEOF and self._is_running:
                    packets = []
                    try:
                        for _ in range(self.chunk_size):
                            packet = pcap_reader.read_packet()
                            if packet:
                                packets.append(packet)
                            else:
                                break
                    except EOFError:
                        notEOF = False
                    if not packets:
                        break

                    dfs = [protocol_handler(packet) for packet in packets]
                    dfs = pd.concat(dfs, ignore_index=True)
                    self.provider.append_data(dfs)
                    self.data_loaded.emit()

        elif file_extension == 'log':
            dfs = []
            pkts = []
            with CandumpReader(self.file_path) as log_reader:
                for i, packet in enumerate(log_reader, start=1):
                    if not self._is_running:
                        break                     
                    df = protocol_handler(packet)
                    dfs.append(df)
                    pkts.append(packet)
                    if i % self.chunk_size == 0:
                        df_chunk = pd.concat(dfs, ignore_index=True)
                        self.provider.append_data(df_chunk)
                        self.data_loaded.emit()
                        dfs = []
                        pkts = []
                if dfs and self._is_running:
                    df_chunk = pd.concat(dfs, ignore_index=True)
                    self.provider.append_data(df_chunk)
                    self.data_loaded.emit()

        elif file_extension == 'csv':
            for chunk in pd.read_csv(self.file_path, chunksize=self.chunk_size):
                if not self._is_running:
                    break
                self.provider.append_data(chunk)
                self.data_loaded.emit()

        elif file_extension == 'parquet':
            chunk = pd.read_parquet(self.file_path)
            self.provider.append_data(chunk)
            self.data_loaded.emit()

        elif file_extension == 'pickle':
            df = pd.read_pickle(self.file_path)
            self.provider.append_data(df)
            self.data_loaded.emit()

        else:
            print("Unsupported file type.") # NEED TO RAISE EXCEPTION TO CHANGE STATUS IN THE GUI

        self.finished.emit()

    def stop(self):
        self._is_running = False
