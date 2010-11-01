from ConfigParser import SafeConfigParser

from path import path

from group import Group
from repository import Repository

GROUP_PREFIX = "group:"

REPO_PREFIX = "repo:"

class ParseError(Exception):
    pass

class Config(object):
    __slots__ = ["groups"]
    def __init__(self):
        self.groups = {}

    def parse(self, name):
        self.parsefp(file(name))

    def parsefp(self, fp):
        parser = SafeConfigParser()
        parser.readfp(fp)
        sections = parser.sections()

        groups = [x for x in sections if x.startswith(GROUP_PREFIX)]
        map(lambda x: self._parse_group(parser, x), groups)

        repos = [x for x in sections if x.startswith(REPO_PREFIX)]
        map(lambda x: self._parse_repo(parser, x), repos)

    def _parse_repo(self, parser, section):
        group_name = parser.get(section, "group")
        group = self.groups.get(group_name)
        if group is None:
            raise ParseError("Unknown group '%s' in '%s'" % (group_name, section))

        repo = Repository()
        repo.path = path(section[len(REPO_PREFIX):]).expanduser()
        repo.group = group
        group.add_repository(repo)

    def _parse_group(self, parser, section):
        name = section[len(GROUP_PREFIX):]
        group = Group()
        group.name = name
        self.groups[name] = group
