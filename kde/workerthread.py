from PyQt4.QtCore import *
from PyQt4.QtGui import *

import fiximportdir
from deveba.userinterface import UserInterface


class WorkerThread(QThread, UserInterface):
    logCalled = pyqtSignal(int, QString)

    def __init__(self, groups):
        QThread.__init__(self)
        self.groups = groups

    def log(self, level, msg):
        UserInterface.log(self, level, msg)
        self.logCalled.emit(level, msg)

    def run(self):
        self.do_sync(self.groups)
