from PyQt5.QtCore import QThread, pyqtSignal
import pandas as pd
from scapy.all import sniff, load_contrib
from sniffers.protocols import protocol_handler
# from scapy.contrib.isotp import ISOTP

# # Load the contrib modules
# load_contrib('automotive.doip')
# load_contrib('automotive.uds')
# load_contrib('automotive.someip')
# load_contrib('isotp')

class PacketLoader(QThread):
    packets_loaded = pyqtSignal()

    def __init__(self, provider, iface, chunk_size=1, parent=None):
        super().__init__(parent)
        self.chunk_size = chunk_size
        self.running = True
        self.provider = provider
        self.packet_list = []
        self.iface = iface
        self.channel = "vcan0"
        self.timeout = 1    # Timeout in seconds for sniffing

        if self.iface == "can":
            load_contrib('cansocket')
            self.sock = CANSocket(channel=self.channel, bitrate=500000)

    def run(self):
        self.packet_list.clear()
        if self.iface == "can":
            while self.running:
                sniff(prn=self.packet_handler, store=False, stop_filter=self.stop_sniffing, timeout=self.timeout, opened_socket=self.sock)
        else:
            while self.running:
                sniff(prn=self.packet_handler, store=False, stop_filter=self.stop_sniffing, timeout=self.timeout)

    def packet_handler(self, packet):
        self.packet_list.append(packet)
        if len(self.packet_list) >= self.chunk_size:
            dfs = pd.concat([protocol_handler(pkt) for pkt in self.packet_list], ignore_index=True)
            self.provider.append_data(dfs)
            self.packets_loaded.emit() # Triggers table view update with live view
            self.packet_list.clear()  # Clear the list for the next batch

    def stop_sniffing(self, packet):
        return not self.running

    def stop(self):
        self.running = False
        self.quit()
        self.wait()
