from PyQt5.QtCore import QThread, pyqtSignal
from pandas import read_csv
from sniffers.logReader import LogReader
from scapy.all import PcapReader
from multiprocessing import cpu_count, Pool

class FileLoader(QThread):
    data_loaded = pyqtSignal(tuple)
    finished = pyqtSignal()

    def __init__(self, mainwindow, file_path, selected_filter, chunk_size=1000, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.selected_filter = selected_filter
        self.chunk_size = chunk_size
        self.provider = mainwindow.data_provider
        self._is_running = True
        self.protocols = mainwindow.protocols
        self.parser = LogReader(self.protocols)

    def run(self):
        self.provider.clear_data()
        count = sum(1 for i in open(self.file_path, 'rb'))
        self.data_loaded.emit((count, 0))
        file_extension = self.file_path.split('.')[-1].lower()
        if self.selected_filter.startswith("Parquet"):
            file_extension = 'parquet'
        elif self.selected_filter.startswith("LOG"):
            file_extension = 'log'
        elif self.selected_filter.startswith("CSV"):
            file_extension = 'csv'
        elif self.selected_filter.startswith("PCAP"):
            file_extension = 'pcap'
            
        if file_extension == 'gzip':
            file_extension = self.file_path.split('.')[-2].lower()
        
        if file_extension == 'pcap' or file_extension=='pcapng':     
            with PcapReader(self.file_path) as pcap_reader:
                notEOF = True
                chunk_counter = 0
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

                    dfs = [self.protocols.handle_packet(packet) for packet in packets]
                    self.provider.save_chunk(dfs)
                    chunk_counter += 1
                    self.data_loaded.emit((count, chunk_counter*self.chunk_size))
            self.provider.read_all_parquets()

        elif file_extension == 'log':
            num_cpus = cpu_count()
            chunk_counter = 0
            chunk_iter = read_csv(self.file_path, chunksize=self.chunk_size, header=None)
            while self._is_running:
                chunks = []
                try:
                    for _ in range(num_cpus):
                        chunks.append(next(chunk_iter)[0].tolist())
                except StopIteration:
                    if not chunks:  # If no chunks have been collected, break the loop
                        break
                with Pool(num_cpus) as pool:
                    results_of_list_of_packets = pool.map(self.parser.parse_packets, chunks)
                for list_of_packets in results_of_list_of_packets:
                    self.provider.save_chunk(list_of_packets)
                chunk_counter += 1
                self.data_loaded.emit((count, chunk_counter*self.chunk_size*num_cpus))
            self.provider.read_all_parquets()

        elif file_extension == 'csv':
            chunk_counter = 0
            for chunk in read_csv(self.file_path, chunksize=self.chunk_size):
                if not self._is_running:
                    break
                self.provider.save_chunk(chunk)
                chunk_counter += 1
                self.data_loaded.emit((count, chunk_counter*self.chunk_size))
            self.provider.read_all_parquets()
            
        elif file_extension == 'parquet':
            self.provider.read_parquet(self.file_path)

        else:
            print("Unsupported file type.") # NEED TO RAISE EXCEPTION TO CHANGE STATUS IN THE GUI
        self.provider.delete_temp_folder()
        self.finished.emit()

    def stop(self):
        self._is_running = False
