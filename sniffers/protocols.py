from struct import pack
import pandas as pd
from json import load as loadjson
from scapy.all import load_contrib
from scapy.contrib.isotp import ISOTP

# Load the contrib modules
load_contrib('automotive.doip')
load_contrib('automotive.uds')
load_contrib('automotive.someip')
load_contrib('isotp')

# Load the important fields from JSON file
with open('sniffers/proto_fields.json', 'r') as file:
    important_fields = loadjson(file)

def protocol_handler(packet):
    layer = packet
    packet_data = {
        'time': packet.time,
        'length': len(packet),
        'info': packet.summary()
    }
    # Extract the data from the packet
    try:
        packet_data['data'] = packet.data.hex()
    except:
        packet_data['data'] = bytes(packet).hex()

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

    return pd.DataFrame([packet_data])


