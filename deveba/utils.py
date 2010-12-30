import socket

PROGNAME = "deveba"
HOSTNAME = socket.gethostname()

def generate_commit_message(group):
    msg = "Automatic commit from %s, running on %s (group %s)" % (PROGNAME, HOSTNAME, group)

def get_commit_author_name():
    return PROGNAME

def get_commit_author_email():
    return PROGNAME + "@" + HOSTNAME
