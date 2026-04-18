from abc import ABC, abstractmethod
from typing import Any, List, Dict

class IDataGenerator(ABC):
    """
    Interface for data generation strategies following the Strategy Pattern.
    """
    @abstractmethod
    def generate(self, count: int, **kwargs) -> List[tuple]:
        """Generate a list of data tuples."""
        pass

class IDatabaseManager(ABC):
    """
    Interface for database operations abstraction.
    """
    @abstractmethod
    def connect(self):
        """Establish database connection."""
        pass

    @abstractmethod
    def close(self):
        """Close database connection."""
        pass

    @abstractmethod
    def execute_query(self, query: str, params: tuple = None):
        """Execute a single query."""
        pass

    @abstractmethod
    def execute_many(self, query: str, data: List[tuple]):
        """Execute bulk insert operations."""
        pass

    @abstractmethod
    def commit(self):
        """Commit current transaction."""
        pass
