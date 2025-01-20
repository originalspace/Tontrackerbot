########## HYPERLINK TEMPLATE ##########

from PyQt5.QtWidgets import QWidget, QLabel

class HyperlinkLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__()
        self.setStyleSheet("font-size: 35px")
        self.setOpenExternalLinks(True)
        self.setParent(parent)

class AppDemo(QWidget):
    def __init__(self):
        super().__init__()

        linkTemplate = '<a href={0}>{1}</a>'
        
        label = HyperlinkLabel(self)
        label.setText(linkTemplate.format('https://tonviewer.com/', 'TonViewer'))