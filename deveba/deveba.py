#!/usr/bin/env python
import logging
import sys
from optparse import OptionParser

from path import path

import lognotify

from config import Config
from userinterface import InteractiveUserInterface, SilentUserInterface
from handler import HandlerError
from githandler import GitHandler

CONFIG_FILE = "~/.config/deveba/deveba.xml"

class OptionError(Exception):
    pass

def setup_logger(name, quiet):
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

    handler = lognotify.create_handler("deveba")
    if handler:
        logging.getLogger().addHandler(handler)

def do_list(groups):
    for group in groups:
        print group
        for handler in group.handlers.values():
            print "- %s" % handler

def do_sync(groups, ui):
    for group in groups:
        for handler in group.handlers.values():
            logging.info("Synchronizing %s" % handler.path)
            try:
                handler.sync(ui)
            except HandlerError, exc:
                logging.error("Failed: %s" % exc)
    logging.info("Done")

def get_group_list(all_groups, names):
    groups = []
    for name in names:
        group = all_groups.get(name)
        if not group:
            raise OptionError("No group named '%s'" % name)
        groups.append(group)
    return groups

def main():
    parser = OptionParser()

    parser.add_option("--log",
                      dest="log", default="-",
                      help="write log to FILE", metavar="FILE")

    parser.add_option("-l", "--list",
                      action="store_true", dest="list",
                      help="list groups and repositories")

    parser.add_option("-i", "--interactive",
                      action="store_true", dest="interactive",
                      help="prompt before actions")

    parser.add_option("-a", "--all",
                      action="store_true", dest="all",
                      help="Backup all repositories")

    parser.add_option("-q", "--quiet",
                      action="store_true", dest="quiet",
                      help="only log errors and warnings")

    parser.add_option("-c", "--config",
                      dest="config", default=CONFIG_FILE,
                      help="config file to use (default to %s)" % CONFIG_FILE)

    (options, args) = parser.parse_args()

    setup_logger(options.log, options.quiet)

    config = Config()
    config.add_handler_class(GitHandler)
    config.parse(path(options.config).expanduser())

    if options.list:
        do_list(config.groups.values())
        return 0

    if options.all:
        groups = config.groups.values()
    else:
        groups = get_group_list(config.groups, args)

    if options.interactive:
        ui = InteractiveUserInterface()
    else:
        ui = SilentUserInterface()

    if groups:
        do_sync(groups, ui)
    else:
        logging.error("Nothing to synchronize")

    return 0


if __name__ == "__main__":
    sys.exit(main())
# vi: ts=4 sw=4 et
