#!/usr/bin/env python
import logging
import sys
from optparse import OptionParser

from path import path

from config import Config
from proginfo import InteractiveProgInfo, ProgInfo

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

def do_list(groups):
    for group in groups:
        print group
        for repo in group.repositories.values():
            print "- %s" % repo

def do_backup(groups, proginfo):
    for group in groups:
        logging.info("# Group %s" % group.name)
        group.backup(proginfo)

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

    parser.add_option("--list",
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
    config.parse(path(options.config).expanduser())

    if options.list:
        do_list(config.groups.values())
        return 0

    if options.all:
        groups = config.groups.values()
    else:
        groups = get_group_list(config.groups, args)

    if options.interactive:
        proginfo = InteractiveProgInfo()
    else:
        proginfo = ProgInfo()

    do_backup(groups, proginfo)

    return 0


if __name__ == "__main__":
    sys.exit(main())
# vi: ts=4 sw=4 et
