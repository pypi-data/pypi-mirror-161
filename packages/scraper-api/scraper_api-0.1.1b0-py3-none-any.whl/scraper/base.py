"""
Base class for all scrapers

Examples:
    >>> from scraper.base import AbstractScraper
    >>> import requests
    >>> class Scraper(AbstractScraper):
    >>>     def scrape(self, url: str) -> str:
    >>>         return requests.get(url).text
    >>> scraper = Scraper()
    >>> scraper.scrape("https://www.example.com/")

In this example we define our Scraper derived from AbstractScraper
"""
from abc import ABCMeta, abstractmethod


class AbstractScraper(metaclass=ABCMeta):
    """
    Interface of scraper class
    """

    @abstractmethod
    def collect_data(self, **kwargs) -> dict:
        """
        Method to collect data from page

        Args:
            **kwargs: common kwargs

        Returns:
            (dict): return processed data
        """

    @abstractmethod
    def scrape(self, url: str) -> str:
        """
        Main method to start to scrape data from url
        Args:
            url: (str): url of web-site

        Returns:
            str: Text plain
        """
