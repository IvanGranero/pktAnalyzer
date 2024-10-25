from pandas import DataFrame
from struct import pack
from json import load as loadjson
from scapy.all import load_contrib, load_layer
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

def protocol_handler(packet):
    layer = packet
    packet_data = {
        'time': float(packet.time),
        'length': len(packet),
        'info': packet.summary(),
        'data': bytes(packet).hex(),
        'dataprint': bytes(packet).decode('ascii', errors='replace').replace('\ufffd', '')
    }

    # Extracts all the fields from packet
    while layer:
        layer_name = layer.__class__.__name__
        if layer_name in important_fields:
            for key, field in important_fields[layer_name].items():
                try:
                    packet_data[key] = layer.getfieldval(field)
                except (AttributeError, KeyError):
                    pass
        else:
            pass
            #print(f"Unknown layer: {layer_name}")

        layer = layer.payload if layer.payload else None

    packet_data['protocol'] = layer_name

    return DataFrame([packet_data])

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


