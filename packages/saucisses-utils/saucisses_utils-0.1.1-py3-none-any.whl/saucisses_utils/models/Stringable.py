import abc


class Stringable(abc.ABC):
    @abc.abstractmethod
    def __str__(self) -> str:
        pass
