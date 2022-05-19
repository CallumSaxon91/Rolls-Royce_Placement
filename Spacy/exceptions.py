
class NotWikiPage(Exception):
    """This url does not lead to a wikipedia article"""
    pass


class InvalidURLorFilePath(Exception):
    """The entered url or file path is invalid"""
    pass


class NoImageFound(Exception):
    """Image could not be found in assets"""
    pass
