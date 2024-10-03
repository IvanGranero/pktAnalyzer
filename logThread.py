from collections import deque
import threading
import canPkts
import ethernetPkts
import cudfPkts

buffer = None
stop_logging = False
bus_type = "eth"     # default value

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

def startLogger(network_item):
    global stop_logging
    global thread
    global bus_type
    bus_type = network_item
    # NEED TO ADD INPUT FIELD TO GET INTERFACE FROM USER
    if bus_type=="can":    
        canPkts.setup_can("vcan0")
        dataframe_fields = canPkts.get_fields(bus_type)
    elif bus_type == "eth":
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


def evalFilter(filter_argument):
    return cudfPkts.eval_filter(filter_argument)


def runFilter(filter_argument):
    return cudfPkts.query_filter(filter_argument)

