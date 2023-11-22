from abc import ABC, abstractmethod


class Workflow(ABC):
    pass

    @abstractmethod
    def validate(self):
        pass
