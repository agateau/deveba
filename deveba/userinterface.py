class UserInterface(object):
    def confirm(self, msg, default):
        raise NotImplementedError

class InteractiveUserInterface(UserInterface):
    def confirm(self, msg, default):
        line = raw_input("%s (y/n): " % msg)
        return line.lower() == "y"

class SilentUserInterface(UserInterface):
    def confirm(self, msg, default):
        return default
