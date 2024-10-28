from pandas import DataFrame
from struct import pack
from json import load as loadjson
from scapy.all import load_contrib, load_layer
from scapy.config import conf
#from scapy.contrib.isotp import ISOTP
from scapy.layers.l2 import Ether, ARP
from scapy.layers.http import HTTP, HTTPRequest, HTTPResponse, Raw
from scapy.layers.can import CANFD, CAN

# Load the contrib modules
load_contrib('automotive.doip')
load_contrib('automotive.uds')
load_contrib('automotive.someip')
load_contrib('isotp')
load_layer('http')

# Load the important fields from JSON file
with open('sniffers/proto_fields.json', 'r') as file:
    important_fields = loadjson(file)

conf.contribs['CAN']['swap-bytes'] = True   # True for Wireshark dissection False for PC_CAN Socket dissection

def protocol_handler(packet):
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
        pktbytes.decode('ascii', errors='replace').replace('\ufffd', '')  # Dataprint
    ]

    # Extract additional fields
    layer = packet
    while layer:
        layer_name = layer.__class__.__name__
        if layer_name in important_fields:
            for field_info in important_fields[layer_name]['fields']:
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

def hex_to_packet(hex_string, proto):
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

