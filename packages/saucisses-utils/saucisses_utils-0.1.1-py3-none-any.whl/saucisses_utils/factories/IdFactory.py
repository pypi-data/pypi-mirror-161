import abc
from utils.Id import Id

class IdFactory(abc.ABC):
    def generate(self) -> Id:
        pass
