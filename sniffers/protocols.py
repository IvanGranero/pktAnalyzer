from struct import pack
import pandas as pd
from json import load as loadjson

# Load the important fields from JSON file
with open('sniffers/proto_fields.json', 'r') as file:
    important_fields = loadjson(file)

def protocol_handler(packet):
    layer = packet
    packet_data = {
        'time': packet.time,
        'length': len(packet)
    }

    while layer:
        layer_name = layer.__class__.__name__
        if layer_name in important_fields:
            for key, field in important_fields[layer_name].items():
                try:
                    packet_data[key] = layer.getfieldval(field)
                except (AttributeError, KeyError):
                    pass
        layer = layer.payload if layer.payload else None

    packet_data['protocol'] = layer_name
    try:
        packet_data['Info'] = packet.summary()
    except (AttributeError, KeyError):
        pass
    return pd.DataFrame([packet_data])


