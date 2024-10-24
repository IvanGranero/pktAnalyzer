import pandas as pd
from re import compile

class DataFrameProvider:
    def __init__(self):
        self.alldata = pd.DataFrame() # dataframe to store all the data
        self.data = pd.DataFrame() # dataframe to store the data to be displayed

    def clear_data(self):
        del self.alldata
        self.alldata = pd.DataFrame()
        del self.data
        self.data = pd.DataFrame()

    def append_data(self, chunk):
        # Identify numeric and string columns
        numeric_cols = chunk.select_dtypes(include='number').columns
        string_cols = chunk.select_dtypes(include=['object', 'string']).columns
        # Fill NA/None values with appropriate defaults
        chunk = chunk.fillna({col: 0 for col in numeric_cols})
        chunk = chunk.fillna({col: '' for col in string_cols})
        # Convert columns to appropriate data types
        chunk = chunk.convert_dtypes()
        # Add a unique index to the DataFrame if not already present
        if 'no' not in chunk.columns:
            chunk['no'] = range(len(self.alldata), len(self.alldata) + len(chunk))
        # Moves the no column to the beginning
        chunk = chunk[['no'] + [col for col in chunk.columns if col != 'no']]
        # Concatenate the chunk to the dataframes
        concat_result = pd.concat([self.alldata, chunk], ignore_index=True)
        self.alldata = concat_result
        self.data = concat_result.copy()

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
        result = eval(filter_argument, {'df': self.alldata})        
        if return_data:
            return result
        else:
            self.data = result

    # def eval_filter(self, filter_argument):
    #     return pd.eval(filter_argument)

    # maybe change them to another python file to add all the analysis decoders such as base64

    def add_strings_column(self, column_source):
        self.alldata['strings'] = self.alldata['dataprint'].apply(self.find_strings)
 
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
        # Decode the byte sequences to strings
        print (strings)
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
