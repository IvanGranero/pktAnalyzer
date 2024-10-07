import pandas as pd

alldata = pd.DataFrame()

def start_dataframe(dataframe_fields):
    global alldata
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
    alldata = pd.DataFrame(columns=new_dataframe_fields)

def read_packets(filepath):
    global alldata
    try:        
        alldata = pd.read_parquet(filepath, compression='gzip')
    except Exception as e:
        try:
            print(e)
            alldata = pd.read_csv(filepath, compression="gzip")
        except Exception as e:
            print(e)
            alldata = pd.read_csv(filepath, sep='\t')            
    print("read all data")

def save_packets(file_name):
    global alldata       
    print ("Saving log to a file")
    #save all buffer into file         
    #alldata.to_csv(file_name) 
    # PARQUET GIVING ERROR for unknown values, NEED TOF IND A WAY TO SAVE IGNORING ERRORS     
    alldata = alldata.convert_dtypes()
    try:        
        alldata.to_parquet(file_name+'.parquet.gzip', compression='gzip')
    except Exception as e:
        try:
            print(e)
            alldata.to_csv(file_name+'.gzip', compression='gzip')
        except Exception as e:
            print(e)
            alldata.to_csv(file_name+'.csv', sep='\t')
    print("Saved as bufferdump.")

def append(pkt):
    global alldata
    print (pkt)                 # DON'T REMOVE UNTIL ABLE TO LIVE UPDATE THE TABLE
    try:
        alldata.loc[len(alldata)] = pkt
    except Exception as e:
        print (e)

def df_toJSON():
    try:
        datos = alldata.head(20)
        datos = datos.to_json(default_handler=str, orient="records")
    except Exception as e:
        print (e)
    return datos

def query_filter(filter_argument):
    return alldata.query(filter_argument)

def eval_filter(filter_argument):
    return pd.eval(filter_argument)