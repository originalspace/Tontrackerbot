"""import requests
import json

url = "https://api.telegram.org/<TOKEN>/getUpdates"
response = requests.get(url)
data = json.loads(response.text)
chat_id = data["result"][0]["message"]["chat"]["id"]

print(chat_id)"""

"""from secrets import token_urlsafe
token = token_urlsafe(8)
print(token)"""
"""
"RAKmVgrywOM"

telegram_url = 'https://www.telegram.org'
bot_name = ''
token = ""
url = f'{telegram_url}/{bot_name}?start={token}'
print(url)"""

########################################################

import sys 
from PyQt5.QtWidgets import QApplication, QWidget, QLabel

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
        
        label1 = HyperlinkLabel(self)
        label1.setText(linkTemplate.format('https://tonviewer.com/', 'TonViewer'))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    demo = AppDemo()
    demo.show()

    sys.exit(app.exec_())