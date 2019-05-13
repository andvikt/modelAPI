from logging import getLogger


class _LoggerMixin(object):
    """
    Convinience class, provide individual logger for every class, that inherits it
    We can not pickle loggers, thats why we need it
    """
    def __init__(self, name, namespace):
        self.name = name
        self.namespace=namespace

    @property
    def logger(self):
        return getLogger(f'validation.{self.name}')