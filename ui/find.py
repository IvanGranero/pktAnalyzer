from PyQt5.QtWidgets import QDialog
from re import compile
from utils import aiPrompt
from ui.findWindow import Ui_Form

class FindWindow(QDialog, Ui_Form):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.mainwindow = parent
        self.btn_find.clicked.connect(self.find)
        self.btn_add_strings.clicked.connect(self.add_strings_column)
        self.update_dropdowns()

    def update_dropdowns(self):
        columns = self.mainwindow.df_model._data.columns
        self.combo_searchfor.clear()
        self.combo_searchfor.addItems(columns)

    def find(self):
        text = self.find_text.text()
        column = self.combo_searchfor.currentText()
        if self.ai_checkBox.isChecked():
            self.regex_checkBox.setChecked(True)
            prompt = aiPrompt.prepare_regex_prompt(text)
            text = aiPrompt.get_completion (prompt)
        self.preview_text.setPlainText(text)
        use_regex = self.regex_checkBox.isChecked()
        #if self.hexdecode_checkBox.isChecked():
        def hex_to_text(hex_string):
            try:
                return bytes.fromhex(hex_string).decode('latin1', errors='replace')
            except ValueError:
                return hex_string
        
        if use_regex:
            compiled_pattern = compile(text)
            mask = self.mainwindow.data_provider.alldata[column].apply(lambda x: bool(compiled_pattern.search(hex_to_text(str(x)))))
        else:
            mask = self.mainwindow.data_provider.alldata[column].apply(lambda x: text in hex_to_text(str(x)))

        # if use_regex:
        #     compiled_pattern = compile(text)
        #     mask = self.mainwindow.data_provider.alldata[column].apply(lambda x: bool(compiled_pattern.search(str(x))))
        # else:
        #     mask = self.mainwindow.data_provider.alldata[column].apply(lambda x: text in str(x))

        self.mainwindow.update_table(self.mainwindow.data_provider.alldata[mask])
        #self.update_dropdowns()
        #preview_text

    def add_strings_column(self):
        min_length = int(self.strings_length.text())
        column = self.combo_searchfor.currentText()
        # Apply the function and fill any NaN values with empty strings
        df = self.mainwindow.data_provider.alldata #reference to main data frame
        df['strings'] = df.loc[:, column].apply(lambda x: self.find_strings(x, min_length)).fillna('')
        self.mainwindow.inline_search.setText("df[df['strings'] != '']")
        self.mainwindow.run_filter()

    def find_strings(self, data, min_length=4):
        pattern = compile(r'[\x20-\x7E]{%d,}' % min_length)
        if not isinstance(data, str): data = str(data)
        strings = pattern.findall(data)
        strings = ', '.join(strings)
        return strings

    def add_base64_column(self, column):
        self.alldata['base64decoded'] = self.alldata[column].apply(self.find_and_decode_base64_from_hex)
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