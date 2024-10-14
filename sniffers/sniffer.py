from PyQt5.QtCore import QThread, pyqtSignal
import pandas as pd
from scapy.all import sniff, load_contrib
from sniffers.protocols import protocol_handler

class PacketLoader(QThread):
    packets_loaded = pyqtSignal(pd.DataFrame)

    def __init__(self, provider, iface, chunk_size=1, parent=None):
        super().__init__(parent)
        self.chunk_size = chunk_size
        self.running = True
        self.provider = provider
        self.df = pd.DataFrame()
        self.iface = iface
        self.channel = "vcan0"
        if self.iface == "can":
            load_contrib('cansocket')
            #scapy.load_layer("can")
            self.sock = CANSocket(channel=self.channel, bitrate=500000)  #NEED TO CHANGE TO AN INTERFACE FROM USER
        #this only works in Linux
        #self.sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(3))
        #self.sock.bind((default_interface, 0))

    def run(self):
        if self.iface == "can":
            sniff(prn=self.packet_handler, store=False, stop_filter=self.stop_sniffing, opened_socket=self.sock)
        else:
            sniff(prn=self.packet_handler, store=False, stop_filter=self.stop_sniffing)        

    def packet_handler(self, packet):
        new_df = protocol_handler(packet)
        self.df = pd.concat([self.df, new_df], ignore_index=True)

        if self.df.shape[0] >= self.chunk_size:
            self.df = self.df.convert_dtypes()
            self.df = self.df.apply(lambda col: col.astype('int64') if col.dtype == 'Int64' else col)
            self.provider.alldata = pd.concat([self.provider.alldata, self.df], ignore_index=True)
            self.packets_loaded.emit(self.df)
            self.df.iloc[0:0] #clear the local dataframe

    def stop_sniffing(self, packet):
        return not self.running

    def stop(self):
        self.running = False
        self.quit()
        self.wait()

