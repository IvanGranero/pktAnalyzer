from json import load as loadjson
from scapy.config import conf
from scapy.layers.l2 import Ether, ARP
from scapy.layers.can import CANFD, CAN
from scapy.contrib.automotive.doip import *
from scapy.contrib.automotive.uds import *
from scapy.contrib.automotive.someip import *
from scapy.contrib.isotp import *
from scapy.contrib.automotive.xcp import *
from scapy.layers.http import *
#from scapy.layers.http import HTTP, HTTPRequest, HTTPResponse, Raw
from pandas import to_datetime

class ProtocolHandler:
    def __init__(self):
        file_path = "sniffers/proto_fields.json" # user settings?
        with open(file_path, 'r') as file:
            self.important_fields = loadjson(file)
        conf.contribs['CAN']['swap-bytes'] = True   # True for Wireshark dissection False for PC_CAN Socket dissection

    def handle_packet(self, packet):
        pktbytes = bytes(packet)
        pktlength = len(packet)        
        # Handle CAN packets
        if pktlength == 16:
            packet = CAN(pktbytes)

        packet_data = [
            float(packet.time),  # Time
            '', # Source,
            '', # Destination
            '', # Protocol
            pktlength,  # Length
            packet.summary(),  # Info
            '',  # Identifier/Port
            '',  # Data
            pktbytes.hex(),  # Dataframe
            pktbytes.decode('latin1', errors='replace') # Dataprint
        ]

        # Extract additional fields
        layer = packet
        while layer:
            layer_name = layer.__class__.__name__
            if layer_name in self.important_fields:
                for field_info in self.important_fields[layer_name]['fields']:
                    field_name = field_info['name']
                    col_num = field_info['column_number']                
                    try:
                        field_value = layer.getfieldval(field_name)
                        if 'convert_from_to' in field_info:
                            if field_info['convert_from_to'] == 'int_to_hexstring':
                                packet_data[col_num] = hex(field_value)
                            elif field_info['convert_from_to'] == 'int_to_string':
                                packet_data[col_num] = str(field_value)
                            elif field_info['convert_from_to'] == 'bytes_to_hexstring':
                                packet_data[col_num] = field_value.hex()
                        else:
                            packet_data[col_num] = field_value
                    except (AttributeError, KeyError):
                        pass # missing field handling
            else:
                pass  # Unknown layer handling

            layer = layer.payload if layer.payload else None

        packet_data[3] = layer_name  # Protocol
        return packet_data

    def hex_to_packet(self, hex_string, proto):
        packet_bytes = bytes.fromhex(hex_string)
        if proto == 'CAN':
            return CAN(packet_bytes)
        elif proto == 'CANFD':
            return CANFD(packet_bytes)
        # List of layer 2 protocols
        #layers = [Ether, ARP, CAN, CANFD] # CAN and CANFD are not being recognized
        layers = [Ether, ARP]
        for layer in layers:
            try:
                packet = layer(packet_bytes)
                if packet.haslayer(layer):
                    return packet
            except:
                pass
        # If no known primary layer matches, return raw bytes
        return Raw(packet_bytes)

