from PyQt5.QtWidgets import QTreeWidgetItem
from sniffers.protocolsHandler import ProtocolHandler

class PacketInspector:
    def __init__(self, parent=None):
        super().__init__()
        self.mainwindow = parent
        self.protocols = ProtocolHandler()
     
    def show_packet(self, current, previous):
        hex_to_packet = self.protocols.hex_to_packet
        row = current.row()
        column = current.column()
        #self.mainwindow.tableview.selectRow(row)
        data = self.mainwindow.df_model._data.iloc[row]['dataframe']
        proto = self.mainwindow.df_model._data.iloc[row]['protocol']
        #dataprint =  bytes.fromhex(data).decode('latin1', errors='replace').replace('\ufffd', '  ')
        dataprint = '  '.join(
                    chr(int(data[i:i + 2], 16)) if 32 <= int(data[i:i + 2], 16) <= 126 else '.'
                    for i in range(0, len(data), 2)
                )
        data = ' '.join(data[i:i+2] for i in range(0, len(data), 2))
        formatted_text = f"<pre style='font-family: Courier New; font-size: 10pt;'>{data}\n{dataprint}</pre>"
        self.mainwindow.data_inspector.setHtml(formatted_text)
        self.mainwindow.packet_inspector.clear()
        layer = hex_to_packet(data, proto)
        while layer:
            layer_item = QTreeWidgetItem([layer.summary()])
            self.mainwindow.packet_inspector.addTopLevelItem(layer_item)
            # add all the packet fields
            for field_name, field_val in layer.fields.items():
                field_item = QTreeWidgetItem([f"{field_name}: {field_val}"])
                layer_item.addChild(field_item)

            layer_item.setExpanded(True)
            layer = layer.payload if layer.payload else None