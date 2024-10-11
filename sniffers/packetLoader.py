from PyQt5.QtCore import QThread, pyqtSignal
import pandas as pd
import socket
from scapy.all import sniff, Packet, get_if_list
from scapy.layers.inet import IP, TCP, UDP
from scapy.layers.http import HTTPRequest, HTTPResponse
from scapy.layers.can import CAN, CAN_FD_MAX_DLEN as CAN_FD_MAX_DLEN
from scapy.contrib.automotive.uds import UDS
from scapy.contrib.automotive.doip import DoIP
from scapy.contrib.isotp import ISOTP

class PacketLoader(QThread):
    packets_loaded = pyqtSignal(pd.DataFrame)

    def __init__(self, chunk_size=1, parent=None):
        super().__init__(parent)
        self.chunk_size = chunk_size
        self.running = True
        self.df = pd.DataFrame()
        # open socket, defaulting to ethernet for now
        #this only works in Linux
        #self.sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(3))
        #self.sock.bind((default_interface, 0))

    def run(self):
        sniff(prn=self.packet_handler, store=False, stop_filter=self.stop_sniffing)        

    def packet_handler(self, packet):
        packet_data = {}
        if packet.haslayer(HTTPRequest) or packet.haslayer(HTTPResponse):
            packet_data['protocol'] = 'HTTP'
            # Add relevant HTTP fields
        elif packet.haslayer(TCP):
            packet_data['protocol'] = 'TCP'
            packet_data['src'] = packet[IP].src
            packet_data['dst'] = packet[IP].dst
            packet_data['sport'] = packet[TCP].sport
            packet_data['dport'] = packet[TCP].dport
        elif packet.haslayer(UDP):
            packet_data['protocol'] = 'UDP'
            packet_data['src'] = packet[IP].src
            packet_data['dst'] = packet[IP].dst
            packet_data['sport'] = packet[UDP].sport
            packet_data['dport'] = packet[UDP].dport
        elif packet.haslayer(DoIP):
            packet_data['protocol'] = 'DoIP'
            # Add relevant DoIP fields
        elif packet.haslayer(UDS):
            packet_data['protocol'] = 'UDS'
            # Add relevant UDS fields
        elif packet.haslayer(ISOTP):
            packet_data['protocol'] = 'ISOTP'
            # Add relevant CAN fields            
        elif packet.haslayer(CAN):
            packet_data['protocol'] = 'CAN'
            # Add relevant CAN fields
        else:
            packet_data['protocol'] = 'Unknown'

        # Append the packet data to the DataFrame
        packet_data = {k:[v] for k,v in packet_data.items()}
        new_df = pd.DataFrame(packet_data)
        self.df = pd.concat([self.df, new_df], ignore_index=True)

        if self.df.shape[0] >= self.chunk_size:            
            self.packets_loaded.emit(self.df)
            self.df.iloc[0:0] #clear the local dataframe

    def stop_sniffing(self, packet):
        return not self.running

    def stop(self):
        self.running = False
        self.quit()
        self.wait()

