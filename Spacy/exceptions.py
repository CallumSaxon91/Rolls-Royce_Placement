
class NotWikiPage(Exception):
    """This url does not lead to a wikipedia article"""
    pass


class NoImageFound(Exception):
    """Image could not be found in assets"""
    pass
