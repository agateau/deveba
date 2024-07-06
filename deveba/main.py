#!/usr/bin/env python
import logging
import sys
from optparse import OptionParser

from deveba import core

from deveba.userinterface import TextUserInterface, SilentUserInterface


def do_list(groups):
    for group in groups:
        print(group)
        for handler in group.handlers:
            print(f"- {handler}")


def main():
    parser = OptionParser()

    parser.add_option(
        "--log", dest="log", default="-", help="write log to FILE", metavar="FILE"
    )

    parser.add_option(
        "-l",
        "--list",
        action="store_true",
        dest="list",
        help="list groups and repositories",
    )

    parser.add_option(
        "-i",
        "--interactive",
        action="store_true",
        dest="interactive",
        help="prompt before actions",
    )

    parser.add_option(
        "-a", "--all", action="store_true", dest="all", help="Backup all repositories"
    )

    parser.add_option(
        "-q",
        "--quiet",
        action="store_true",
        dest="quiet",
        help="only log errors and warnings",
    )

    parser.add_option(
        "-c",
        "--config",
        dest="config",
        default=core.CONFIG_FILE,
        help=f"config file to use (default to {core.CONFIG_FILE})",
    )

    (options, args) = parser.parse_args()

    core.setup_logger(options.log, options.quiet)

    config = core.load_config(options.config)

    if options.list:
        do_list(list(config.groups.values()))
        return 0

    if options.all:
        groups = list(config.groups.values())
    else:
        groups = core.get_group_list(config, args)

    if not groups:
        logging.error("Nothing to synchronize")
        return 1

    ui = TextUserInterface() if options.interactive else SilentUserInterface()

    return ui.do_sync(groups)


if __name__ == "__main__":
    sys.exit(main())
# vi: ts=4 sw=4 et
