from PyKDE4.kdecore import *

import fiximportdir
from deveba.userinterface import UserInterface

LOG_ICON = {
    UserInterface.LOG_VERBOSE: "dialog-ok",
    UserInterface.LOG_INFO: "dialog-information",
    UserInterface.LOG_WARNING: "dialog-warning",
    UserInterface.LOG_ERROR: "dialog-error",
}


class LogMessage(object):
    def __init__(self, timestamp, level, text):
        self.timestamp = timestamp
        self.level = level
        self.text = text

    def iconName(self):
        return LOG_ICON[self.level]

    def timeString(self):
        return "%02d:%02d" % (self.timestamp.tm_hour, self.timestamp.tm_min)

    def formatted(self):
        return "%s: %s" % (self.timeString, self.text)
