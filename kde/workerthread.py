from PyQt4.QtCore import *
from PyQt4.QtGui import *

from deveba.userinterface import UserInterface

class WorkerThread(QThread, UserInterface):
    logCalled = pyqtSignal(int, QString)

    def __init__(self, groups, parent):
        QThread.__init__(self, parent)
        self.groups = groups

    def log(self, level, msg):
        UserInterface.log(self, level, msg)
        self.logCalled.emit(level, msg)

    def run(self):
        self.do_sync(self.groups)
