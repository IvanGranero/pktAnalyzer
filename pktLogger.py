import signal, sys, time
import gui.graphicalInterface

# logging with filter 
# stop when payload or word
# search in log


def handler_interrupt(signal, frame):
    sys.exit(0)


def main():

    # add try catch to all 
    signal.signal(signal.SIGINT, handler_interrupt)

    if(len(sys.argv) > 2):
        # to start logging thread from the command line e.g. pktLogger can0 -s "flag{"
        print ("command line options not available yet")
       
    gui.graphicalInterface.openMainWindow(sys.argv)
    

if __name__ == "__main__":
    main()