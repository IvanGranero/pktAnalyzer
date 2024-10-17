from scapy.layers.inet import IP, TCP, UDP
from scapy.layers.http import HTTPRequest, HTTPResponse
from scapy.layers.can import CAN, CAN_FD_MAX_DLEN as CAN_FD_MAX_DLEN
from scapy.contrib.automotive.uds import UDS
from scapy.contrib.automotive.doip import DoIP
from scapy.contrib.isotp import ISOTP
import pandas as pd

class ProtocolHandler:
    def handle(self, packet, packet_data={}):
        self.process_packet(packet, packet_data)
        packet_data['info'] = packet.summary()
        return packet_data

    def process_packet(self, packet, packet_data={}):
        raise NotImplementedError("Subclasses must implement this method")

class HTTPHandler(ProtocolHandler):
    def process_packet(self, packet, packet_data={}):
        packet_data['protocol'] = 'HTTP'

class TCPHandler(ProtocolHandler):
    def process_packet(self, packet, packet_data={}):
        packet_data['protocol'] = 'TCP'
        if packet.haslayer(IP):        
            packet_data['src'] = packet[IP].src
            packet_data['dst'] = packet[IP].dst
        packet_data['sport'] = packet[TCP].sport
        packet_data['dport'] = packet[TCP].dport

class UDPHandler(ProtocolHandler):
    def process_packet(self, packet, packet_data={}):
        packet_data['protocol'] = 'UDP'
        if packet.haslayer(IP):
            packet_data['src'] = packet[IP].src
            packet_data['dst'] = packet[IP].dst
        packet_data['sport'] = packet[UDP].sport
        packet_data['dport'] = packet[UDP].dport


class DoIPHandler(ProtocolHandler):
    def process_packet(self, packet, packet_data={}):
        packet_data['protocol'] = 'DoIP'

class UDSHandler(ProtocolHandler):
    def process_packet(self, packet, packet_data={}):
        packet_data['protocol'] = 'UDS'

class ISOTPHandler(ProtocolHandler):
    def process_packet(self, packet, packet_data={}):
        packet_data['protocol'] = 'ISOTP'

class CANHandler(ProtocolHandler):
    def process_packet(self, packet, packet_data={}):
        packet_data['protocol'] = 'CAN'
        for field in CAN().fields_desc:
            try:
                field = field.name
                if field == 'flags':        
                    packet_data[field] = packet.fields[field].flagrepr()                
                else:
                    packet_data[field] = packet.fields[field]
            except: 
                packet_data[field] = None

        datahex = packet.fields['data'].hex()
        datahex_with_spaces = ' '.join(datahex[i:i+2] for i in range(0, len(datahex), 2))
        packet_data['data'] = datahex_with_spaces

protocol_handlers = {
    'HTTPRequest': HTTPHandler(),
    'HTTPResponse': HTTPHandler(),
    'TCP': TCPHandler(),
    'UDP': UDPHandler(),
    'DoIP': DoIPHandler(),
    'UDS': UDSHandler(),
    'ISOTP': ISOTPHandler(),
    'CAN': CANHandler()
}

def protocol_handler(packet, packet_data = {}):
    for protocol, handler in protocol_handlers.items():
        if packet.haslayer(eval(protocol)):
            handler.handle(packet, packet_data)
    packet_data = {k: [v] for k, v in packet_data.items()}
    new_df = pd.DataFrame(packet_data)
    return new_df