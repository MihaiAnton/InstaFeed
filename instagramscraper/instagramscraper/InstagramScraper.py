from abc import abstractmethod, ABC


class IInstagramScraper(ABC):

    @abstractmethod
    def login(self, username, password) -> bool:
        pass
