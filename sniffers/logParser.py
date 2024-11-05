from re import compile
#from json import load as loadjson
from scapy.layers.can import CANFD, CAN
from sniffers.protocolsHandler import ProtocolHandler

class Parser:
    def __init__(self):

        # file_path = "sniffers/parsing_patterns.json"    # user settings?
        # with open(file_path, 'r') as file:
        #     patterns_json = loadjson(file)

        patterns_json = {
            "patterns": [
                {"name": "PATTERN_1", "regex": "^\\((?P<timestamp>\\d+\\.\\d+)\\)\\s+(?P<interface>\\w+)\\s+(?P<identifier>[0-9A-F]{3,8})#(?P<data>[0-9A-F]*)\\s*$"},
                {"name": "PATTERN_2", "regex": "^\\((?P<timestamp>\\d+\\.\\d+)\\)\\s+(?P<interface>\\w+)\\s+(?P<identifier>[0-9A-F]{3,8})##(?P<flags>\\d)(?P<data>[0-9A-F]*)\\s*$"},
                {"name": "PATTERN_3", "regex": "^(?P<interface>\\w+)\\s+(?P<identifier>[0-9A-F]{3,8})#(?P<data>[0-9A-F]*)\\s*$"},
                {"name": "PATTERN_4", "regex": "^(?P<interface>\\w+)\\s+(?P<identifier>[0-9A-F]{3,8})##(?P<flags>\\d)(?P<data>[0-9A-F]*)\\s*$"},
                {"name": "PATTERN_5", "regex": "^\\s*(?P<interface>\\w+)\\s+(?P<identifier>[0-9A-F]{3,8})\\s+\\[(?P<length>\\d+)\\]\\s+(?P<data>[0-9A-F\\s]+)\\s*$"},
                {"name": "PATTERN_6", "regex": "^\\((?P<timestamp>\\d+\\.\\d+)\\)\\s*(?P<interface>\\w+)\\s+(?P<identifier>[0-9A-F]{3,8})\\s+\\[(?P<length>\\d+)\\]\\s+(?P<data>[0-9A-F\\s]+)\\s*$"}
            ]
        }

        self.patterns = [compile(p['regex']) for p in patterns_json['patterns']]
        self.protocols = ProtocolHandler()

    def parse_packets(self, lines):
        list_of_packets = []
        for line in lines:
            try:
                pkt = self.protocols.handle_packet(self.parse_packet(line))
                list_of_packets.append(pkt)
            except:
                pass
        return list_of_packets

    def parse_packet(self, line):
        line = line.lstrip()
        for pattern in self.patterns:
            match = pattern.match(line)
            if match:
                items = match.groupdict()
                intf = items['interface']
                idn = items['identifier']
                data = items['data'].replace(' ', '')
                try:
                    if len(data)<=8 and 'flags' not in items:
                        pkt = CAN(identifier=int(idn, 16), data=bytes.fromhex(data))
                    else:
                        flags = items['flags']
                        pkt = CANFD(identifier=int(idn, 16), fd_flags=flags, data=bytes.fromhex(data))
                except Exception as e:
                    pkt = CANFD(identifier=int(idn, 16), data=bytes.fromhex(data))

                pkt.length = int(items['length']) if 'length' in items else len(pkt.data)
                if len(idn) > 3:
                    pkt.flags = 0b100
                if 'timestamp' in items:
                    pkt.time = float(items['timestamp'])  # it might have date in the timestamp

                return pkt
        
        print ("Invalid line format")
        raise ValueError("Invalid line format")
