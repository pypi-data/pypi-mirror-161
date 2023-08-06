from abc import ABCMeta


class Container(metaclass=ABCMeta):
    def bind(self):
        raise NotImplementedError

    def singleton(self):
        raise NotImplementedError

    def instance(self):
        raise NotImplementedError

    def flush(self):
        raise NotImplementedError

    def make(self):
        raise NotImplementedError

    def resolved(self):
        raise NotImplementedError

    def resolving(self):
        raise NotImplementedError
