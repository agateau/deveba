#!/usr/bin/env python
# encoding: utf-8
import sys
import signal

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from PyKDE4.kdecore import *
from PyKDE4.kdeui import *

from app import App


def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    aboutData = KAboutData(
        "deveba-kde",  # appName
        "",  # catalogName
        ki18n("Deveba"),  # programName
        "1.0",
    )
    aboutData.setLicense(KAboutData.License_GPL_V3)
    aboutData.setShortDescription(ki18n("Distributed Versionized Backup"))
    aboutData.setCopyrightStatement(ki18n("(c) 2012 Aurélien Gâteau"))
    aboutData.setProgramIconName("kde")

    KCmdLineArgs.init(sys.argv, aboutData)

    KCmdLineArgs.addCmdLineOptions(App.options())

    app = App()
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
# vi: ts=4 sw=4 et
