"""
CS504 : scraper
Team : Vidya Akavoor, Lauren DiSalvo, Sreeja Keesara
Description :

Notes : This code was taken from https://realpython.com/python-web-scraping-practical-introduction/#making-web-requests

February 28, 2019
"""

from contextlib import closing
from requests import get
from requests.exceptions import RequestException

class scraper:
    def simple_get(url):
        """
        Attempts to get the content at `url` by making an HTTP GET request.
        If the content-type of response is some kind of HTML/XML, return the
        text content, otherwise return None.
        """
        try:
            with closing(get(url, stream=True)) as resp:
                if scraper.is_good_response(resp):
                    return resp.content
                else:
                    return None

        except RequestException as e:
            scraper.log_error('Error during requests to {0} : {1}'.format(url, str(e)))
            return None

    def is_good_response(resp):
        """
        Returns True if the response seems to be HTML, False otherwise.
        """
        content_type = resp.headers['Content-Type'].lower()
        return (resp.status_code == 200
                and content_type is not None
                and content_type.find('html') > -1)

    def log_error(e):
        """
        It is always a good idea to log errors.
        This function just prints them, but you can
        make it do anything.
        """
        print(e)