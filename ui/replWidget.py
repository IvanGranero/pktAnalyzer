from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit

class REPL(QWidget):
    def __init__(self, provider):
        super().__init__()
        self.provider = provider
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle('data REPL')
        self.setGeometry(100, 100, 500, 400)

        self.layout = QVBoxLayout()

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.layout.addWidget(self.output)

        self.input = QLineEdit()
        self.input.returnPressed.connect(self.evaluate)
        self.layout.addWidget(self.input)

        self.setLayout(self.layout)

    def evaluate(self):
        code = self.input.text()
        self.input.clear()
        try:
            result = eval(code, {'df': self.provider.alldata}) # should we add packets to the list?
            self.output.append(f">>> {code}\n{result}")
            return result
        except Exception as e:
            self.output.append(f">>> {code}\nError: {e}")

