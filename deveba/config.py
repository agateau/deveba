import xml.etree.ElementTree as etree

from path import Path

from deveba.group import Group


class ParseError(Exception):
    pass


class Config(object):
    """
    Parse config and instantiate repository handlers, based on its registered handlers
    """

    __slots__ = ["groups", "handler_classes"]

    def __init__(self):
        self.groups = {}
        self.handler_classes = []

    def add_handler_class(self, klass):
        self.handler_classes.append(klass)

    def parse(self, name):
        with open(name, "r") as fp:
            self.parsefp(fp)

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
        repo_path = Path(repo_element.get("path")).expanduser()
        if repo_path is None:
            raise ParseError("Missing 'path' attribute in repository")

        options = dict(repo_element.attrib)
        del options["path"]
        for handler_class in self.handler_classes:
            handler = handler_class.create(repo_path, options)
            if handler:
                break
        else:
            raise ParseError("Don't know how to handle directory '%s'" % repo_path)
        handler.group = group
        group.handlers.append(handler)
