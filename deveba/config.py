import xml.etree.ElementTree as etree

from path import path

from group import Group
from repository import Repository

class ParseError(Exception):
    pass

class Config(object):
    __slots__ = ["groups"]
    def __init__(self):
        self.groups = {}

    def parse(self, name):
        self.parsefp(file(name))

    def parsefp(self, fp):
        tree = etree.parse(fp)
        root = tree.getroot()
        for group_element in root.findall("group"):
            self._parse_group(group_element)

    def _parse_group(self, group_element):
        group = Group()
        group.name = group_element.get("name")
        if group.name is None:
            raise ParseError("Missing 'name' attribute in group")
        self.groups[group.name] = group
        for repo_element in group_element.findall("repo"):
            self._parse_repo(group, repo_element)

    def _parse_repo(self, group, repo_element):
        repo = Repository()
        repo.path = path(repo_element.get("path")).expanduser()
        if repo.path is None:
            raise ParseError("Missing 'path' attribute in repository")
        repo.group = group
        group.repositories[repo.path] = repo
