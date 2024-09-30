from collections import deque
import threading
import canPkts
import ethernetPkts
import cudfPkts

buffer = None
stop_logging = False
bus_type = "eth"     # change to read gui selected bus

def logging(stop):
    
    while True:
        if stop():
            if bus_type=="can":
                canPkts.shutdown_can()
            #print (buffer)
            break

        if bus_type == "can":
            msg = canPkts.recv_msg()
        else:
            msg = ethernetPkts.recv_msg()
      
        cudfPkts.append(msg)

def startLogger():

    global stop_logging
    global thread
    
    # NEED TO ADD INPUT FIELD TO GET INTERFACE FROM USER
    if bus_type=="can":    
        canPkts.setup_can("vcan0")
    dataframe_fields = ethernetPkts.get_fields(bus_type)
    cudfPkts.start_dataframe(dataframe_fields)
    stop_logging = False
    thread = threading.Thread(target=logging, args=(lambda : stop_logging, ))
    thread.start()

def stopLogger():  
    global stop_logging
    global thread

    stop_logging = True
    thread.join() #waits for thread to stop

    cudfPkts.save_packets("bufferdump")

def runFilter(filter_argument):
    return cudfPkts.run_filter(filter_argument)
