

class ImageNotFound(Exception):
    """Could not find an image file at this location"""
    def __init__(self, fp:str):
        self.fp = fp
        self.message = f"Could not find image file at location: {fp}"
        super().__init__(self.message)


class PipelineNotLoaded(Exception):
    """
        Tried to run process that depends on a pipeline before a
        pipeline was loaded
    """
    def __str__(self) -> str:
        return "Cannot complete this process because a pipeline " \
               "has not been loaded"

