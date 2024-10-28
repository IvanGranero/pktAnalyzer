from PyQt5.QtCore import QThread, pyqtSignal
from pandas import DataFrame
from scapy.all import sniff
from sniffers.protocols import protocol_handler

class PacketLoader(QThread):
    packets_loaded = pyqtSignal()

    def __init__(self, provider, iface, chunk_size=1, parent=None):
        super().__init__(parent)
        self.chunk_size = chunk_size
        self.running = True
        self.provider = provider
        self.packet_list = []
        self.iface = iface
        self.timeout = 1    # Timeout in seconds for sniffing

    def run(self):
        self.packet_list.clear()
        while self.running:
            sniff(iface=self.iface, prn=self.packet_handler, store=False, stop_filter=self.stop_sniffing, timeout=self.timeout)

    def packet_handler(self, packet):
        # no need for chunk_size since we are sniffing each packet
        pkt = protocol_handler(packet)
        self.provider.append_packet(pkt)
        self.packets_loaded.emit() # Triggers table view update with live view
        self.packet_list.clear()  # Clear the list for the next batch

    def stop_sniffing(self, packet):
        return not self.running

    def stop(self):
        self.running = False
        self.quit()
        self.wait()
