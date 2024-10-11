from scapy.all import sniff

def packet_callback(packet):
    packet_data = {
        'timestamp': packet.time,
        'src': packet[0]

    }


sniff(count=1, opened_socket=sock, timeout=1, store=False, prn=packet_callback)