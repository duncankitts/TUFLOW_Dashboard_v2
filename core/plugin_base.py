import re
from abc import ABC, abstractmethod

class TuflowPlugin(ABC):

    @property
    @abstractmethod
    def name(self):
        ...

    @property
    def match_patterns(self):
        """
        List of compiled regex patterns this plugin accepts.
        Override in plugin if needed.
        """
        return []

    def matches(self, filename: str) -> bool:
        filename = filename.lower()
        return any(p.search(filename) for p in self.match_patterns)
