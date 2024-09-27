import can

def setup_can(interface):
    global bus
    try:
        print("Bring up %s...." % (interface))
        #os.system("sudo /sbin/ip link set can0 up type can bitrate 500000")
        #time.sleep(0.1)
        bus = can.interface.Bus(interface='socketcan', channel=interface, bitrate=500000)
        #bus = can.interface.Bus(interface='socketcan', channel='vcan0', bitrate=500000)
        #bus = can.interface.Bus(interface='socketcan', channel='can0', bitrate=500000)
        # bus = can.Bus(interface='socketcan', channel='vcan0', bitrate=250000)
        # bus = can.Bus(interface='pcan', channel='PCAN_USBBUS1', bitrate=250000)
        # bus = can.Bus(interface='ixxat', channel=0, bitrate=250000)
        # bus = can.Bus(interface='vector', app_name='CANalyzer', channel=0, bitrate=250000)

    except OSError:
        print("Cannot find %s interface." % (interface))
        exit()

    print('Ready')

def shutdown_can():
    bus.shutdown()


def send_msg(arb_id, data, is_extended=False):
    try:
        msg = can.Message(arbitration_id=arb_id, data=data, is_extended_id= is_extended)
        bus.send(msg)
    except can.CanError:
        print("Message NOT sent")

def recv_msg():
    try:
    #while True:
        message = bus.recv()    # Wait until a message is received.
        
        '''
        c = '{0:f} {1:x} {2:x} '.format(message.timestamp, message.arbitration_id, message.dlc)
        s=''
        for i in range(message.dlc ):
            s +=  '{:02x} '.format(message.data[i])
        #print(' {}'.format(c+s))
        return message, s
        '''

        return message
    
    except KeyboardInterrupt:
        #Catch keyboard interrupt
        #os.system("sudo /sbin/ip link set can0 down")
        print('\n\rRecv Msg Keyboard interrupt')
        bus.shutdown()
        exit(0)
