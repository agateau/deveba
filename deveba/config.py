import xml.etree.ElementTree as etree

from path import path

from group import Group
from githandler import GitHandler

class ParseError(Exception):
    pass

class Config(object):
    __slots__ = ["groups", "handler_classes"]
    def __init__(self):
        self.groups = {}
        self.handler_classes = []

    def add_handler_class(self, klass):
        self.handler_classes.append(klass)

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
        repo_path = path(repo_element.get("path")).expanduser()
        if repo_path is None:
            raise ParseError("Missing 'path' attribute in repository")

        for handler_class in self.handler_classes:
            if handler_class.can_handle(repo_path):
                handler = handler_class()
                break
        else:
            raise ParseError("Don't know how to handle directory '%s'" % repo_path)
        handler.path = repo_path
        handler.group = group
        group.handlers[handler.path] = handler
