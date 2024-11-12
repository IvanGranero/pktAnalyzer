from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit
from PyQt5.QtCore import Qt

class REPL(QWidget):
    def __init__(self, provider):
        super().__init__()
        self.provider = provider
        self.last_input = ""
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle('data REPL')
        self.setGeometry(100, 100, 500, 400)

        self.layout = QVBoxLayout()

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.layout.addWidget(self.output)

        self.input = InputLineEdit(self)
        self.input.returnPressed.connect(self.evaluate)
        self.layout.addWidget(self.input)

        self.setLayout(self.layout)

    def evaluate(self):
        code = self.input.text()
        self.last_input = code  # Store the last input
        self.input.clear()
        try:
            result = self.provider.query_filter(code)
            self.output.append(f">>> {code}\n{result}")
            return result
        except Exception as e:
            self.output.append(f">>> {code}\nError: {e}")

class InputLineEdit(QLineEdit):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Up:
            self.setText(self.parent.last_input)  # Set the text to the last input
        else:
            super().keyPressEvent(event)
