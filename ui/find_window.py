from PyQt5.QtWidgets import QDialog
from re import compile
from utils import ai_prompt
from PyQt5 import QtCore, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(503, 241)
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(Form)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.find_text = QtWidgets.QLineEdit(Form)
        self.find_text.setObjectName("find_text")
        self.horizontalLayout.addWidget(self.find_text)
        self.btn_find = QtWidgets.QPushButton(Form)
        self.btn_find.setObjectName("btn_find")
        self.horizontalLayout.addWidget(self.btn_find)
        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(1, 2)
        self.horizontalLayout.setStretch(2, 1)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.ai_checkBox = QtWidgets.QCheckBox(Form)
        self.ai_checkBox.setObjectName("ai_checkBox")
        self.horizontalLayout_2.addWidget(self.ai_checkBox)
        self.regex_checkBox = QtWidgets.QCheckBox(Form)
        self.regex_checkBox.setObjectName("regex_checkBox")
        self.horizontalLayout_2.addWidget(self.regex_checkBox)
        self.horizontalLayout_2.setStretch(0, 1)
        self.horizontalLayout_2.setStretch(1, 1)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_3.addWidget(self.label_2)
        self.combo_searchfor = QtWidgets.QComboBox(Form)
        self.combo_searchfor.setObjectName("combo_searchfor")
        self.horizontalLayout_3.addWidget(self.combo_searchfor)
        self.horizontalLayout_3.setStretch(0, 2)
        self.horizontalLayout_3.setStretch(1, 6)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.label_3 = QtWidgets.QLabel(Form)
        self.label_3.setObjectName("label_3")
        self.verticalLayout.addWidget(self.label_3)
        self.preview_text = QtWidgets.QPlainTextEdit(Form)
        self.preview_text.setObjectName("preview_text")
        self.verticalLayout.addWidget(self.preview_text)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_4 = QtWidgets.QLabel(Form)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_4.addWidget(self.label_4)
        self.strings_length = QtWidgets.QLineEdit(Form)
        self.strings_length.setObjectName("strings_length")
        self.horizontalLayout_4.addWidget(self.strings_length)
        self.btn_add_strings = QtWidgets.QPushButton(Form)
        self.btn_add_strings.setObjectName("btn_add_strings")
        self.horizontalLayout_4.addWidget(self.btn_add_strings)
        self.horizontalLayout_4.setStretch(1, 3)
        self.horizontalLayout_4.setStretch(2, 3)
        self.verticalLayout.addLayout(self.horizontalLayout_4)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Find"))
        self.label.setText(_translate("Form", "Find what:"))
        self.btn_find.setText(_translate("Form", "Find"))
        self.ai_checkBox.setText(_translate("Form", "AI"))
        self.regex_checkBox.setText(_translate("Form", "Regex"))
        self.label_2.setText(_translate("Form", "Search in:"))
        self.label_3.setText(_translate("Form", "Preview:"))
        self.label_4.setText(_translate("Form", "Min Length:"))
        self.strings_length.setText(_translate("Form", "4"))
        self.btn_add_strings.setText(_translate("Form", "Add Column with Strings"))


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
            prompt = ai_prompt.prepare_regex_prompt(text)
            text = ai_prompt.get_completion (prompt)
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