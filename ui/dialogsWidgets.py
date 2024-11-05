from ui.dialogs.repl import REPL
from ui.dialogs.options import OptionsWindow
from ui.dialogs.plot import PlotWindow
from ui.dialogs.find import FindWindow
from ui.dialogs.packetInspector import PacketInspector

class Dialogs:
    def __init__(self, mainwindow):
        self.mainwindow = mainwindow
        self._initialize_dialogs()

    def _initialize_dialogs(self):
        self.dialogs = {
            'repl': REPL(self.mainwindow.data_provider),
            'options_window': OptionsWindow(),
            'plot_window': PlotWindow(self.mainwindow.df_model),
            'find_window': FindWindow(self.mainwindow),
            'packet_tree': PacketInspector(self.mainwindow)
        }

    def __getattr__(self, item):
        return self.dialogs.get(item)

