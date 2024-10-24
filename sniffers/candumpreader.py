from scapy.layers.can import CANFD, CAN
import dask.bag as db
import sys

def read_packet(line):
    """Read a packet from the specified file.
    This function will raise EOFError when no more packets are available.
    :return: A single packet read from the file or None if filters apply
    """
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
        pkt = CANFD(identifier=int(idn, 16), fd_flags=fd_flags, data=bytes.fromhex(data))

    # Set packet length
    pkt.length = int(le[1:]) if le is not None else len(pkt.data)

    # Set packet flags if applicable
    if len(idn) > 3:
        pkt.flags = 0b100

    # Set packet time if available
    if t is not None:
        pkt.time = t

    return pkt


if __name__ == "__main__":
    if(len(sys.argv) < 2):
        print("Usage: python candumpreader.py <input_file>")
        sys.exit(1)
    
    file = sys.argv[1]

    # Read the text file in parallel
    bag = db.read_text(file)

    # Example processing: Convert each line to uppercase
    processed_bag = bag.map(lambda x: read_packet(x))

    # Compute and process the results in chunks
    for delayed in processed_bag.to_delayed():
        chunk = delayed.compute()
        # Handle the chunk (result) here
        print(chunk)        