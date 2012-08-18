from PyQt4.QtCore import *
from PyQt4.QtGui import *

from PyKDE4.kdecore import *
from PyKDE4.kdeui import *

class Window(KDialog):
    def __init__(self, app):
        KDialog.__init__(self)
        self.app = app
        self.setButtons(KDialog.Close)

        self.listWidget = QListWidget()
        self.setMainWidget(self.listWidget)

    def addLog(self, message):
        item = QListWidgetItem()
        item.setIcon(KIcon(message.iconName()))
        item.setText(message.timeString() + " " + message.text)
        self.listWidget.addItem(item)
        self.listWidget.scrollToItem(item)

    def closeEvent(self):
        self.app.quit()

    def sizeHint(self):
        return QSize(600, 300)
