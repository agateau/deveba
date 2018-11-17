import logging
import sys

from path import Path

from deveba.config import Config
from deveba.commandhandler import CommandHandler
from deveba.githandler import GitHandler
from deveba.rsynchandler import RsyncHandler
from deveba.unisonhandler import UnisonHandler

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
    config.add_handler_class(RsyncHandler)
    config.add_handler_class(UnisonHandler)
    config.add_handler_class(CommandHandler)
    config.parse(Path(config_filename).expanduser())
    return config

def setup_logger(name, quiet=False):
    args = {}
    if quiet:
        level = logging.WARNING
    else:
        level = logging.INFO
    args["level"] = level

    if name == "-":
        args["stream"] = sys.stderr
    else:
        args["filename"] = name

    args["format"] = "%(levelname)s: %(asctime)s: %(message)s"

    logging.basicConfig(**args)
