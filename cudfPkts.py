import pandas as pd

df_dump = pd.DataFrame()

def start_dataframe(dataframe_fields):
    global df_dump
    
    #inspecting for repeated column names
    new_dataframe_fields = [] 
    counts = {}
    for el in dataframe_fields:
        temp_count = counts.get(el, 0) + 1
        counts[el] = temp_count        
        if temp_count == 1 and dataframe_fields.count(el) == 1:
            new_dataframe_fields.append(el)
        else:
            new_dataframe_fields.append(el + str(temp_count))

    df_dump = pd.DataFrame(columns=new_dataframe_fields)

def save_packets(file_name):        
    global df_dump
    print ("Saving buffer to a file")
    #save all buffer into file         
    #df_dump.to_csv(file_name) 
    # PARQUET GIVING ERROR for unknown values, NEED TOF IND A WAY TO SAVE IGNORING ERRORS 
    df_dump.to_parquet(file_name+'.parquet.gzip', compression='gzip')
    
    print("Saved as bufferdump.")

def append(pkt):
    global df_dump
    print (pkt)     # only for debugging REMOVE AFTER
    if pkt[0] != None:
        df_dump.loc[len(df_dump)] = pkt

def run_filter(filter_argument):
    global df_dump
    return df_dump.query(filter_argument)


