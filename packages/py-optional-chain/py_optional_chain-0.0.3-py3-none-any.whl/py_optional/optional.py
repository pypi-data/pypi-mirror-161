class Optional:
    def __init__(self, value):
        self.__value = value

    def of(value):
        return Optional(value)

    def is_empty(self) -> bool:
        return self.__value is None

    def get(self):
        assert(not self.is_empty())
        return self.__value

    def map(self, func):
        return Optional(func(self.get())) if not self.is_empty() else EMPTY

    def filter(self, func):
        return self if not self.is_empty() and func(self.get()) else EMPTY

    def or_else(self, default):
        return self.get() if not self.is_empty() else default

    def apply(self, func):
        if not self.is_empty():
            return func(self.get())


EMPTY = Optional(None)
