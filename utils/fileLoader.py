from PyQt5.QtCore import QThread, pyqtSignal
import pandas as pd
from sniffers.protocols import protocol_handler
from sniffers.candumpreader import read_packets
from scapy.all import PcapReader
from scapy.layers.can import CandumpReader
import multiprocessing as mp

class FileLoader(QThread):
    data_loaded = pyqtSignal()
    finished = pyqtSignal()

    def __init__(self, provider, file_path, chunk_size=1000, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.chunk_size = chunk_size
        self.provider = provider
        self._is_running = True

    def run(self):
        self.provider.clear_data()
        count = sum(1 for i in open(self.file_path, 'rb'))
        self.provider.alldata_size = count
        self.data_loaded.emit()
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
                    self.provider.append_rows(dfs)
                    self.data_loaded.emit()
            self.provider.read_all_parquets()

        elif file_extension == 'log':
            num_cpus = mp.cpu_count()
            # Initialize the chunk iterator
            chunk_iter = pd.read_csv(self.file_path, chunksize=self.chunk_size, header=None)
            while self._is_running:
                chunks = []
                try:
                    for _ in range(num_cpus):
                        chunks.append(next(chunk_iter)[0].tolist())
                except StopIteration:
                    if not chunks:  # If no chunks have been collected, break the loop
                        break
                with mp.Pool(num_cpus) as pool:
                    results_of_list_of_packets = pool.map(read_packets, chunks)                 
                for list_of_packets in results_of_list_of_packets:
                    self.provider.append_rows(list_of_packets)
                self.data_loaded.emit()
            self.provider.read_all_parquets()

        elif file_extension == 'csv':
            for chunk in pd.read_csv(self.file_path, chunksize=self.chunk_size):
                if not self._is_running:
                    break
                self.provider.append_df(chunk)
                self.data_loaded.emit()
            self.provider.read_all_parquets()
            
        elif file_extension == 'parquet':
            self.provider.read_parquet(self.file_path)
            self.data_loaded.emit()

        else:
            print("Unsupported file type.") # NEED TO RAISE EXCEPTION TO CHANGE STATUS IN THE GUI

        self.finished.emit()

    def stop(self):
        self._is_running = False
