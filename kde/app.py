import time

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from PyKDE4.kdecore import *
from PyKDE4.kdeui import *

import fiximportdir
from deveba import core
from deveba.userinterface import UserInterface
from logmessage import LogMessage
from window import Window
from workerthread import WorkerThread

MAX_TEXTS_LENGTH = 4


class App(KApplication):
    def __init__(self):
        KApplication.__init__(self)
        self.setQuitOnLastWindowClosed(False)

        self.sni = KStatusNotifierItem()
        self.sni.setTitle(i18n("Deveba"))
        self.sni.setCategory(KStatusNotifierItem.SystemServices)
        self.sni.setStatus(KStatusNotifierItem.Active)

        self.sni.setIconByName("task-accepted")

        self.sni.setToolTipTitle(i18n("Deveba"))

        self.window = Window(self)
        self.window.hide()
        self.window.finished.connect(self.slotWindowClosed)
        self.sni.setAssociatedWidget(self.window)

        self.logMessages = []
        self.success = True
        self.workerThread = None

    @staticmethod
    def options():
        options = KCmdLineOptions()
        options.add("log <file>", ki18n("Write log to file"), "-")
        options.add("c").add(
            "config <file>", ki18n("Config file to use"), core.CONFIG_FILE
        )
        options.add("+[group]", ki18n("Start backup of $group"))
        return options

    def exec_(self):
        args = KCmdLineArgs.parsedArgs()

        core.setup_logger(str(args.getOption("log")))

        config_file = args.getOption("config")
        config = core.load_config(config_file)

        if args.count() > 0:
            group_names = [str(args.arg(x)) for x in range(args.count())]
            groups = core.get_group_list(config, group_names)
            self.startSync(groups)
        else:
            self.window.show()

        return KApplication.exec_()

    def startSync(self, groups):
        self.success = True
        self.workerThread = WorkerThread(groups)
        self.workerThread.logCalled.connect(self.addLog, Qt.QueuedConnection)

        self.sni.setIconByName("task-ongoing")
        self.workerThread.start()
        self.workerThread.finished.connect(self.slotSyncFinished)

    def slotSyncFinished(self):
        if self.success:
            self.sni.setIconByName("task-accepted")
        self.workerThread = None
        QTimer.singleShot(2 * 60 * 1000, self.quitIfNoWindow)

    def slotWindowClosed(self):
        if self.workerThread is None:
            self.quit()

    def quitIfNoWindow(self):
        if not self.window.isVisible():
            self.quit()

    def addLog(self, level, msg):
        if level < UserInterface.LOG_INFO:
            return

        timestamp = time.localtime()
        message = LogMessage(timestamp, level, msg)
        self.logMessages.append(message)

        texts = [x.formatted() for x in self.logMessages[-MAX_TEXTS_LENGTH:]]
        html = "<ul>" + "".join(["<li>%s</li>" % x for x in texts]) + "</ul>"
        self.sni.setToolTipSubTitle(html)

        if level >= UserInterface.LOG_WARNING:
            self.success = False
            self.sni.setIconByName("dialog-error")

        self.window.addLog(message)
