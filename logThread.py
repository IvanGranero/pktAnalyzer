from collections import deque
import threading
import canPkts
import ethernetPkts
import cudfPkts
import aiPrompt

stop_logging = False
thread = None
bus_type = "eth"     # default value

def logging(stop):
    while True:
        if stop():
            if bus_type=="can":
                canPkts.shutdown_can()
            break
        if bus_type == "can":
            msg = canPkts.recv_msg()
        else:
            msg = ethernetPkts.recv_msg()

        if len (msg) > 0:
            cudfPkts.append(msg)
        else:
            stopLogger()

## for now Create a seperate startReader function
## for later use the same function and use a parent socket 

def readPackets(filepath):
    cudfPkts.read_packets(filepath)
    
def readLog(filepath):
    canPkts.setup_canreader(filepath)
    dataframe_fields = canPkts.get_fields("can")    #only can for now
    cudfPkts.start_dataframe(dataframe_fields)
    msgs = canPkts.read_candump(filepath)
    for msg in msgs:
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

def askopenAI(prompt):
    try:
        data = cudfPkts.df_toJSON()
        prompt = aiPrompt.prepare_prompt(data, prompt)
        response = aiPrompt.get_completion (prompt)
        print (response)            # FOR DEBUGGING ONLY
    except Exception as e:
        print (e)
    return response
