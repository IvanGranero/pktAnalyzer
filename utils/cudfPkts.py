import pandas as pd
from PyQt5.QtCore import QThread, pyqtSignal

alldata = pd.DataFrame()

class DataFrameLoader(QThread):
    data_loaded = pyqtSignal(pd.DataFrame)

    def __init__(self, file_path, chunk_size=100, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.chunk_size = chunk_size

    def run(self):
        for chunk in pd.read_csv(self.file_path, chunksize=self.chunk_size):
            self.data_loaded.emit(chunk)

    # need to add the stop option when loading a file, use same approach as PacketLoader to stop


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
        datos = alldata.head(10)
        datos = datos.to_json(default_handler=str, orient="records")
    except Exception as e:
        print (e)
    return datos

def query_filter(filter_argument):
    return alldata.query(filter_argument)

def eval_filter(filter_argument):
    return pd.eval(filter_argument)