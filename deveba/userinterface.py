class UserInterface(object):
    CANCEL = "Cancel"

    def confirm(self, msg, default):
        return default

    def show_text(self, msg):
        pass

    def question(self, msg, choices, default):
        return default


class InteractiveUserInterface(UserInterface):
    def confirm(self, msg, default):
        line = raw_input("%s (y/n): " % msg)
        return line.lower() == "y"

    def show_text(self, msg):
        print msg

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
    pass
