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

    def add_strings_column(self):
        min_length = self.strings_length.text()
        column = self.combo_searchfor.currentText()
        self.mainwindow.data_provider.add_strings_column(column, int(min_length))
        self.mainwindow.inline_search.setText("df[df['strings'] != '']")
        self.mainwindow.run_filter()

    def find(self):
        text = self.find_text.text()
        column = self.combo_searchfor.currentText()
        if self.ai_checkBox.isChecked():
            self.regex_checkBox.setChecked(True)
            prompt = aiPrompt.prepare_regex_prompt(text)
            text = aiPrompt.get_completion (prompt)
        self.preview_text.setPlainText(text)
        use_regex = self.regex_checkBox.isChecked()
        if use_regex:
            compiled_pattern = compile(text)
            mask = self.mainwindow.data_provider.alldata[column].apply(lambda x: bool(compiled_pattern.search(str(x))))
        else:
            mask = self.mainwindow.data_provider.alldata[column].apply(lambda x: text in str(x))

        self.mainwindow.update_table(self.mainwindow.data_provider.alldata[mask])
        #self.update_dropdowns()
        #preview_text
