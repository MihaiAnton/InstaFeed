from abc import abstractmethod, ABC


class IInstagramScraper(ABC):

    @abstractmethod
    def scrape_profile(self, username: str) -> dict:
        """Scrapes a profile and returns a dictionary.

        Arguments:
            username {[string]} -- [instagram username]

        Returns:
            dict: {posts: []}
        """
        pass
