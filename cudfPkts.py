
import pandas as pd

df_dump = pd.DataFrame()

def start_dataframe():
    global df_dump
    #for c in columns:            #way to have different columns options
    df_dump = pd.DataFrame(columns=('timestamp','arbitration_id','dlc', 'data'))

def save_packets(file_name):        
    global df_dump
    print ("Saving buffer to a file")
    #save all buffer into file         
    df_dump.to_csv(file_name) 
    print("Saved as bufferdump.")

def append(pkt):
    global df_dump
    df_dump.loc[len(df_dump.index)] = [pkt.timestamp, pkt.arbitration_id, pkt.dlc, pkt.data] 

def run_filter(filter_argument):
    global df_dump
    return df_dump.query(filter_argument)