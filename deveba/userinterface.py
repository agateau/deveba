import logging
from handler import HandlerError

class UserInterface(object):
    CANCEL = "Cancel"
    LOG_VERBOSE = 1
    LOG_INFO = 2
    LOG_WARNING = 3
    LOG_ERROR = 4

    def confirm(self, msg, default):
        return default

    def log_verbose(self, msg):
        self.log(self.LOG_VERBOSE, msg)

    def log_info(self, msg):
        self.log(self.LOG_INFO, msg)

    def log_warning(self, msg):
        self.log(self.LOG_WARNING, msg)

    def log_error(self, msg):
        self.log(self.LOG_ERROR, msg)

    def log(self, log_level, msg):
        if log_level == self.LOG_VERBOSE:
            print msg
        elif log_level == self.LOG_INFO:
            logging.info(msg)
        elif log_level == self.LOG_WARNING:
            logging.warning(msg)
        elif log_level == self.LOG_ERROR:
            logging.error(msg)
        else:
            raise Exception("Unknown log level %s" % log_level)

    def question(self, msg, choices, default):
        return default

    def do_sync(self, groups):
        for group in groups:
            for handler in group.handlers.values():
                self.log(self.LOG_INFO, "Synchronizing %s" % handler.path)
                try:
                    handler.sync(self)
                except HandlerError, exc:
                    self.log(self.LOG_ERROR, "Failed: %s" % exc)
        self.log(self.LOG_INFO, "Done")


class TextUserInterface(UserInterface):
    def confirm(self, msg, default):
        line = raw_input("%s (y/n): " % msg)
        return line.lower() == "y"

    def question(self, msg, choices, default):
        def print_choice(pos, text):
            print "%d) %s" % (pos, text)

        print
        print msg
        for pos, choice in enumerate(choices):
            print_choice(pos + 1, choice)
        print_choice(0, "Cancel")
        while True:
            line = raw_input(": ")
            if not line.isdigit():
                print "Invalid answer %s" % line
                continue
            answer = int(line)
            if answer < 0 or answer >= len(choices):
                print "Invalid answer %s" % line
            if answer == 0:
                return self.CANCEL
            else:
                return choices[answer - 1]


class SilentUserInterface(UserInterface):
    def log(self, log_level, msg):
        if log_level == self.LOG_VERBOSE:
            return
        UserInterface.log(self, log_level, msg)
