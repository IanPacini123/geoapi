from abc import ABC, abstractmethod

class BaseEndpointCall(ABC):
    @abstractmethod
    def coletar(self):
        pass

    @abstractmethod
    def formatar(self, item) -> str:
        pass
