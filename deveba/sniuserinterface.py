import sys
import time

from userinterface import UserInterface

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from PyKDE4.kdecore import *
from PyKDE4.kdeui import *

MAX_TEXTS_LENGTH = 4

class WorkerThread(QThread):
    def __init__(self, ui, work_function):
        QThread.__init__(self)
        self.ui = ui
        self.work_function = work_function

    def run(self):
        self.work_function()

class SniUserInterface(QObject, UserInterface):
    log_called = pyqtSignal(int, QString)

    def __init__(self):
        QObject.__init__(self)
        self.app = QApplication(sys.argv)

        self.sni = KStatusNotifierItem()
        self.sni.setTitle(i18n("Deveba"))
        self.sni.setCategory(KStatusNotifierItem.SystemServices)
        self.sni.setStatus(KStatusNotifierItem.Active)

        self.sni.setIconByName("kde")

        self.sni.setToolTipTitle(i18n("Deveba"))

        self.texts = []

        self.log_called.connect(self.do_log, Qt.QueuedConnection)

    def log(self, level, msg):
        # This method is called in WorkerThread, we need to switch to the GUI thread first
        self.log_called.emit(level, msg)
        UserInterface.log(self, level, msg)

    @pyqtSlot(QString)
    def do_log(self, level, msg):
        if level < self.LOG_INFO:
            return

        tm = time.localtime()
        line = "%02d:%02d %s" % (tm.tm_hour, tm.tm_min, msg)
        self.texts.append(line)
        if len(self.texts) > MAX_TEXTS_LENGTH:
            self.texts.pop(0)
        self.sni.setToolTipSubTitle("<br>".join(self.texts))

    def do_sync(self, groups):
        def work_function():
            UserInterface.do_sync(self, groups)

        thread = WorkerThread(self, work_function)

        thread.finished.connect(self.app.quit)
        thread.start()
        self.app.exec_()
