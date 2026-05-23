from abc import ABC, abstractmethod


class AIProvider(ABC):

    @abstractmethod
    def generate_steps(self, task: str) -> list[str]:
        pass