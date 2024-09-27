from collections import deque
import threading
import canPkts
import cudfPkts

buffer = None
stop_logging = False

def logging(stop):
    
    while True:
        if stop():
            canPkts.shutdown_can()
            #print (buffer)
            break

        msg = canPkts.recv_msg()
        cudfPkts.append(msg)

def startLogger():

    global stop_logging
    global thread
    
    # NEED TO ADD INPUT FIELD TO GET INTERFACE FROM USER
    canPkts.setup_can("vcan0")
    cudfPkts.start_dataframe()
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
