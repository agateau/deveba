from PyKDE4.kdecore import *

import fiximportdir
from deveba.userinterface import UserInterface

class LogMessage(object):
    def __init__(self, timestamp, level, text):
        self.timestamp = timestamp
        self.level = level
        self.text = text

    def formatted(self):
        LOG_STRING = {
            UserInterface.LOG_VERBOSE: i18n("Verbose"),
            UserInterface.LOG_INFO: i18n("Info"),
            UserInterface.LOG_WARNING: i18n("Warning"),
            UserInterface.LOG_ERROR: i18n("Error"),
            }
        return "%02d:%02d %s: %s" % (self.timestamp.tm_hour, self.timestamp.tm_min, LOG_STRING[self.level], self.text)
