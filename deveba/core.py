from path import path

from config import Config
from githandler import GitHandler
from unisonhandler import UnisonHandler

CONFIG_FILE = "~/.config/deveba/deveba.xml"

def get_group_list(config, names):
    groups = []
    for name in names:
        group = config.groups.get(name)
        if not group:
            raise ValueError("No group named '%s'" % name)
        groups.append(group)
    return groups

def load_config(config_filename):
    config = Config()
    config.add_handler_class(GitHandler)
    config.add_handler_class(UnisonHandler)
    config.parse(path(config_filename).expanduser())
    return config


