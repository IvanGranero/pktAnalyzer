from ui.dialogs.repl import REPL
from ui.dialogs.options import OptionsWindow
from ui.dialogs.plot import PlotWindow
from ui.dialogs.find import FindWindow
from ui.dialogs.packetInspector import PacketInspector

class Dialogs:
    def __init__(self, mainwindow):
        self.mainwindow = mainwindow
        self.repl = REPL(mainwindow.data_provider)
        self.options_window = OptionsWindow()
        self.plot_window = PlotWindow(mainwindow)
        self.find_window = FindWindow(mainwindow)
        self.packet_tree = PacketInspector(mainwindow)

