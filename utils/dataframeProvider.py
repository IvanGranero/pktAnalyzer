import pandas as pd
from re import compile
from uuid import uuid4
import os
from shutil import rmtree
from pathlib import Path

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
        self.clear_data()

    def __del__(self):
        self.delete_temp_folder()

    def delete_temp_folder(self):
        if os.path.exists(self.temp_folder):
            rmtree(self.temp_folder)

    def clear_data(self):
        # empty DataFrame with the specified columns and data types
        self.alldata = pd.DataFrame({col: pd.Series(dtype=typ) for col, typ in self.columns_and_dtypes.items()})
        self.data = self.alldata.copy() # dataframe to store the data to be displayed
        self.delete_temp_folder()
        os.makedirs(self.temp_folder)
        self.alldata_size = 0
        self.data_size = 0
        self.file_counter = 0

    def append_df(self, new_df):
        self.file_counter += 1
        file_path = os.path.join(self.temp_folder, f'processed_data_{self.file_counter}.parquet')
        new_df.to_parquet(file_path, index=False)
        self.data = new_df.copy()
        self.data_size += new_df.shape[0]

    def append_rows(self, rows):
        new_df = pd.DataFrame(rows, columns=self.alldata.columns)
        self.file_counter += 1        
        file_path = os.path.join(self.temp_folder, f'processed_data_{self.file_counter}.parquet')
        new_df.to_parquet(file_path, index=False)
        self.data = new_df.copy()
        self.data_size += new_df.shape[0]        

    def append_packet(self, packet):
        self.alldata.loc[len(self.alldata)] = packet
        self.data.loc[len(self.data)] = packet
        self.alldata_size += 1
        self.data_size += 1

    def read_parquet(self, filepath):
        self.alldata = pd.read_parquet(filepath)
        self.data = self.alldata.copy()
        self.alldata_size = self.alldata.shape[0]
        self.data_size = self.alldata_size        
    
    def read_all_parquets(self):
        data_dir = Path(self.temp_folder)
        self.alldata = pd.concat(
            pd.read_parquet(parquet_file)
            for parquet_file in data_dir.glob('*.parquet')
        ).reset_index(drop=True)
        self.data = self.alldata.copy()
        self.alldata_size = self.alldata.shape[0]
        self.data_size = self.alldata_size


    def save_packets(self, filepath, selected_filter):
        if selected_filter.startswith("Parquet"):
            if not filepath.endswith(".parquet"):
                filepath += ".parquet"
            self.data.to_parquet(filepath)

        elif selected_filter.startswith("LOG"):
            if not filepath.endswith(".log"):
                filepath += ".log"
            # Need to add a function to save canlog packets

        elif selected_filter.startswith("PCAP"):
            if not (filepath.endswith(".pcap") or filepath.endswith(".pcapng")):
                filepath += ".pcap"  # Default to .pcap if neither is specified
            # Need to add wrpcap function to save the packets

        elif selected_filter.startswith("CSV"):
            if not filepath.endswith(".csv"):
                filepath += ".csv"
            self.data.to_csv(filepath, sep='\t')

    def df_toJSON(self):
        try:
            datos = self.alldata.head(5)
            datos = datos.to_json(default_handler=str, orient="records")
        except Exception as e:
            print (e)
        return datos

    def query_filter(self, filter_argument, return_data=False):
        #return self.alldata.query(filter_argument)
        ## Need to sanitize the input to avoid code injection
        result = eval(filter_argument, {'df': self.alldata, 'data': self.data})
        if return_data:
            return result
        else:
            self.data = result

    # def eval_filter(self, filter_argument):
    #     return pd.eval(filter_argument)

    # maybe change them to another python file to add all the analysis decoders such as base64

    def add_strings_column(self, column_index):
        self.alldata['strings'] = self.alldata.iloc[:, column_index].apply(self.find_strings)
        self.data['strings'] = self.alldata['strings']
 
    def to_ascii(self, datahex):
        return ''.join(
            chr(int(datahex[i:i + 2], 16)) if 32 <= int(datahex[i:i + 2], 16) <= 126 else '.'
            for i in range(0, len(datahex), 2)
        )

    def find_strings(self, data, min_length=4):
        # Compile a regex pattern to match sequences of printable ASCII characters
        pattern = compile('[\x20-\x7E]{%d,}' % min_length)
        # Find all matches of the pattern in the data
        strings = pattern.findall(data)
        strings = ', '.join(strings)
        return strings

    def add_base64_column(self, column_source):
        self.alldata['base64decoded'] = self.alldata['hexbytes'].apply(self.find_and_decode_base64_from_hex)
        self.alldata['base64decoded'] = self.alldata['base64decoded'].astype(str)

    def find_and_decode_base64_from_hex(hex_string):
        # Convert hex string to bytes
        raw_data = bytes.fromhex(hex_string)
        
        # Regular expression to match base64 encoded strings
        base64_pattern = compile(r'(?<![A-Za-z0-9+/=])([A-Za-z0-9+/]{4})*'
                                    r'([A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?(?![A-Za-z0-9+/=])')
        
        # Decode the bytes to string to apply regex
        raw_data_str = raw_data.decode('latin1')  # Using 'latin1' to avoid decoding errors
        # Find all base64 strings in the raw data string
        base64_strings = base64_pattern.findall(raw_data_str)
        decoded_strings = []

        for base64_string in base64_strings:
            # Base64 string tuple, get the full match
            full_base64 = ''.join(base64_string)
            try:
                # Decode the base64 string
                decoded_data = base64.b64decode(full_base64).decode('utf-8', errors='replace')
                decoded_strings.append(decoded_data)
            except Exception as e:
                print(f"Could not decode: {full_base64}, Error: {e}")

        return decoded_strings
