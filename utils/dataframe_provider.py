import pandas as pd
import os
from re import compile
from uuid import uuid4
from shutil import rmtree
from pathlib import Path
from scapy.all import wrpcap

class DataFrameProvider:
    def __init__(self):
        # Define column names and their data types
        self.columns_and_dtypes = {
            'time': 'float64',
            'source': 'string',
            'destination': 'string',
            'protocol': 'string',
            'length': 'int64',
            'info': 'string',
            'identifier': 'string',
            'data': 'string',
            'dataframe': 'string',
            'dataprint': 'string'
        }
        # Disable SettingWithCopyWarning
        pd.options.mode.chained_assignment = None
        self.temp_folder = f"temp_processing_data_{uuid4().hex}"
        self.alldata = pd.DataFrame({col: pd.Series(dtype=typ) for col, typ in self.columns_and_dtypes.items()})

    def __del__(self):
        self.delete_temp_folder()

    def delete_temp_folder(self):
        if os.path.exists(self.temp_folder):
            rmtree(self.temp_folder)

    def clear_data(self):
        # empty DataFrame with the specified columns and data types
        self.alldata = pd.DataFrame({col: pd.Series(dtype=typ) for col, typ in self.columns_and_dtypes.items()})
        self.delete_temp_folder()
        os.makedirs(self.temp_folder)
        self.file_counter = 0

    def save_chunk(self, chunk):
        if not isinstance(chunk, pd.DataFrame):   
            chunk = pd.DataFrame(chunk, columns=self.alldata.columns).reset_index(drop=True)
        self.file_counter += 1        
        file_path = os.path.join(self.temp_folder, f'processed_data_{self.file_counter}.parquet')
        chunk.to_parquet(file_path, index=False)

    def append_packet(self, packet):
        self.alldata.loc[len(self.alldata)] = packet

    def read_parquet(self, filepath):
        self.alldata = pd.read_parquet(filepath).reset_index(drop=True)
    
    def read_all_parquets(self):
        data_dir = Path(self.temp_folder)
        self.alldata = pd.concat(
            (pd.read_parquet(parquet_file) for parquet_file in data_dir.glob('*.parquet'))            
        ).reset_index(drop=True)

    def df_toJSON(self):
        try:
            datos = self.alldata.head(5)
            datos = datos.to_json(default_handler=str, orient="records")
        except Exception as e:
            print (e)
        return datos

    def query_filter(self, filter_argument):
        ## Need to sanitize the input to avoid code injection
        return eval(filter_argument, {'df': self.alldata})


