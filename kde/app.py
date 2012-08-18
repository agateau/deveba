import time

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from PyKDE4.kdecore import *
from PyKDE4.kdeui import *

import fiximportdir
from deveba import core
from deveba.userinterface import UserInterface
from workerthread import WorkerThread

MAX_TEXTS_LENGTH = 4

class App(KApplication):
    def __init__(self):
        KApplication.__init__(self)

        self.sni = KStatusNotifierItem()
        self.sni.setTitle(i18n("Deveba"))
        self.sni.setCategory(KStatusNotifierItem.SystemServices)
        self.sni.setStatus(KStatusNotifierItem.Active)

        self.sni.setIconByName("task-accepted")

        self.sni.setToolTipTitle(i18n("Deveba"))

        self.texts = []

    @staticmethod
    def options():
        options = KCmdLineOptions()
        options.add("log <file>", ki18n("Write log to file"), "-")
        options.add("c").add("config <file>", ki18n("Config file to use"), core.CONFIG_FILE)
        options.add("+[group]", ki18n("Start backup of $group"))
        return options

    def exec_(self):
        args = KCmdLineArgs.parsedArgs()

        core.setup_logger(unicode(args.getOption("log")))

        config_file = args.getOption("config")
        config = core.load_config(config_file)

        if args.count() > 0:
            group_names = [unicode(args.arg(x)) for x in range(args.count())]
            groups = core.get_group_list(config, group_names)
            self.startSync(groups)
        else:
            print "FIXME: Show window here"

        return KApplication.exec_()

    def startSync(self, groups):
        thread = WorkerThread(groups, self)
        thread.logCalled.connect(self.addLog, Qt.QueuedConnection)

        self.sni.setIconByName("task-ongoing")
        thread.start()
        thread.finished.connect(self.slotSyncFinished)

    def slotSyncFinished(self):
        self.sni.setIconByName("task-accepted")
        QTimer.singleShot(2 * 60 * 1000, self.quit)

    def addLog(self, level, msg):
        if level < UserInterface.LOG_INFO:
            return

        tm = time.localtime()
        line = "%02d:%02d %s" % (tm.tm_hour, tm.tm_min, msg)
        self.texts.append(line)
        if len(self.texts) > MAX_TEXTS_LENGTH:
            self.texts.pop(0)
        html = "<ul>" + "".join(["<li>%s</li>" % x for x in self.texts]) + "</ul>"
        self.sni.setToolTipSubTitle(html)
