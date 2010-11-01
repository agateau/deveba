class HandlerError(Exception):
    pass

class Handler(object):
    def work(self, path, author, group):
        """
        Perform repository backup in 'path', as part as group 'group'. Use 'author' for commit.
        """
        return NotImplementedError
