#!/usr/bin/env python
import logging
import sys
from optparse import OptionParser

import core

from userinterface import TextUserInterface, SilentUserInterface
try:
    from PyKDE4.kdecore import *
    from PyKDE4.kdeui import *
    HAS_PYKDE = True
except ImportError:
    HAS_PYKDE = False

USER_INTERFACE_DICT = {
    "text": TextUserInterface,
    "silent": SilentUserInterface
}

if HAS_PYKDE:
    from sniuserinterface import SniUserInterface
    USER_INTERFACE_DICT["sni"] = SniUserInterface
    DEFAULT_USER_INTERFACE = "sni"
else:
    DEFAULT_USER_INTERFACE = "silent"

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

def do_list(groups):
    for group in groups:
        print group
        for handler in group.handlers.values():
            print "- %s" % handler

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
                      help="prompt before actions [DEPRECATED]")

    parser.add_option("--interface",
                      dest="interface", default=DEFAULT_USER_INTERFACE,
                      help="user interface to use. Possible values: %s. (default to %s)"
                      % (USER_INTERFACE_DICT.keys(), DEFAULT_USER_INTERFACE))

    parser.add_option("-a", "--all",
                      action="store_true", dest="all",
                      help="Backup all repositories")

    parser.add_option("-q", "--quiet",
                      action="store_true", dest="quiet",
                      help="only log errors and warnings")

    parser.add_option("-c", "--config",
                      dest="config", default=core.CONFIG_FILE,
                      help="config file to use (default to %s)" % core.CONFIG_FILE)

    (options, args) = parser.parse_args()

    setup_logger(options.log, options.quiet)

    config = core.load_config(options.config)

    if options.list:
        do_list(config.groups.values())
        return 0

    if options.all:
        groups = config.groups.values()
    else:
        groups = core.get_group_list(config, args)

    if not groups:
        logging.error("Nothing to synchronize")
        return 1

    if options.interactive:
        print "Deprecated option '--interactive' should be replaced with '--interface=text'"
        ui = TextUserInterface()
    else:
        ui = USER_INTERFACE_DICT[options.interface]()

    ui.do_sync(groups)

    return 0


if __name__ == "__main__":
    sys.exit(main())
# vi: ts=4 sw=4 et
