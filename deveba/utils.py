import socket

PROGNAME = "deveba"
HOSTNAME = socket.gethostname()


def generate_commit_message(group):
    return f"Automatic commit from {PROGNAME}, running on {HOSTNAME} (group {group})"


def get_commit_author_name():
    return PROGNAME


def get_commit_author_email():
    return PROGNAME + "@" + HOSTNAME
