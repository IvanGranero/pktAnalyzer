from scapy.layers.can import CANFD, CAN
from sniffers.protocols import protocol_handler

def read_dfpackets(lines):
    pkts = []
    for line in lines:
        try:
            pkt = protocol_handler(read_packet(line))
            pkts.append(pkt)
        except:
            pass
    return pkts

def read_packet(line):
    # Read and strip leading whitespaces
    line = line.lstrip()

    # Check for EOF
    if len(line) < 16:
        raise EOFError
    
    # Determine log file format
    is_log_file_format = line[0] == "("
    fd_flags = None

    if is_log_file_format:
        t_b, intf, f = line.split()
        if '##' in f:
            idn, data = f.split('##')
            fd_flags = data[0]
            data = data[1:]
        else:
            idn, data = f.split('#')
        t = float(t_b[1:-1])  # Extract time
        le = None
    else:
        h, data = line.split(']')
        intf, idn, le = h.split()
        t = None

    # Filter interface if specified
    # if self.ifilter is not None and intf.decode('ASCII') not in self.ifilter:
    #     return None

    # Clean and prepare data
    data = data.replace(' ', '').strip()
    
    # Create packet based on the length and flags
    if len(data) <= 8 and fd_flags is None:
        pkt = CAN(identifier=int(idn, 16), data=bytes.fromhex(data))
    else:
        pkt = CANFD(identifier=int(idn, 16), data=bytes.fromhex(data))
        #pkt = CANFD(identifier=int(idn, 16), fd_flags=fd_flags, data=bytes.fromhex(data))  # it's failing for unrecognized flags

    # Set packet length
    pkt.length = int(le[1:]) if le is not None else len(pkt.data)

    # Set packet flags if applicable
    if len(idn) > 3:
        pkt.flags = 0b100

    # Set packet time if available
    if t is not None:
        pkt.time = t

    return pkt
