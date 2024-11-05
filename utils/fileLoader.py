from PyQt5.QtCore import QThread, pyqtSignal
from pandas import read_csv
from sniffers.logParser import Parser
from scapy.all import PcapReader
from concurrent.futures import ThreadPoolExecutor, as_completed
from os import cpu_count


class FileLoader(QThread):
    data_loaded = pyqtSignal(tuple)
    finished = pyqtSignal()

    def __init__(self, provider, file_path, selected_filter, chunk_size=1000, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.selected_filter = selected_filter
        self.chunk_size = chunk_size
        self.provider = provider
        self._is_running = True
        self.parser = Parser()

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
                    dfs = [self.parser.protocols.handle_packet(packet) for packet in packets]
                    self.provider.save_chunk(dfs)
                    chunk_counter += 1
                    self.data_loaded.emit((count, chunk_counter*self.chunk_size))
            self.provider.read_all_parquets()

        elif file_extension == 'log':
            chunk_counter = 0
            chunk_iter = read_csv(self.file_path, chunksize=self.chunk_size, header=None)
            # Initialize ThreadPoolExecutor
            num_workers = int(cpu_count()/2)
            with ThreadPoolExecutor(max_workers=num_workers) as executor:
                futures = []
                while self._is_running:
                    try:
                        chunk = next(chunk_iter)[0].tolist()
                    except StopIteration:
                        break                    
                    # Submit the processing task to the executor
                    future = executor.submit(self.process_chunk, chunk)
                    futures.append(future)
                # Collect results as they complete
                for future in as_completed(futures):
                    future.result()  # Ensure the task is completed
                    chunk_counter += 1
                    self.data_loaded.emit((count, chunk_counter * self.chunk_size))
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

    def process_chunk(self, chunk):
        list_of_packets = self.parser.parse_packets(chunk)
        self.provider.save_chunk(list_of_packets)
        #return len(list_of_packets)

    def stop(self):
        self._is_running = False

