import cloudscraper
import logging
import pandas as pd

from bs4 import BeautifulSoup, Comment
from io import StringIO
from pathlib import Path
from random import randint
from time import time, sleep
from warnings import filterwarnings

from requests_html import HTMLSession

from ...model.Failure import Failure

filterwarnings('ignore',message =\
"The input looks more like a filename than markup. You may want to open this file and pass the filehandle into Beautiful Soup." )

class Scraper:
    def __init__(self):
        self.request_interval: int = 3 # Time in seconds to wait between requests
        self.last_request_time: float = time() - 3 # Timestamp of the last request in seconds
        self.failures : list[Failure] = []

    def init_logger(self, logger : str, log_file: str):
        self.logger = logging.getLogger(logger)
        file_handler = logging.FileHandler(log_file, mode = "w")
        self.logger.addHandler(file_handler)


    def sleep(self):
        #PFR Website only accepts 20 requests a minute
        time_since_last_request = time() - self.last_request_time
        if time_since_last_request > self.request_interval:
            self.last_request_time = time()
            return
        else:
            r: int = randint(1,10)/10
            sleep((self.request_interval-time_since_last_request)+r)
            self.last_request_time = time()
    
    def make_call(self,url:str) -> BeautifulSoup:
        scraper = cloudscraper.create_scraper(browser={'browser': 'firefox','platform': 'windows','mobile': False}, debug=True)
        self.sleep()
        #response: requests.Response = requests.get(url, headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36", "Content-Type":"text/html"})
        response = scraper.get(url,headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36", "Content-Type":"text/html"})
        if response.status_code != 200:
            raise Exception("Request to " + url + " failed " + str(response.content))
        
        self.parser : BeautifulSoup = BeautifulSoup(response.text,"html.parser")

        return self.parser
    
    def parse_comment_parsers(self) -> list[BeautifulSoup]:
        """Extract and parse HTML comments containing tables from a BeautifulSoup parser"""
        comments : list[str] = self.parser.find_all(string = lambda text : isinstance(text, Comment))
        comments = list(set(comments))
        
        #Only want the comments that contain tables
        for comment in comments:
            try:
                pd.read_html(StringIO(comment))
            except ValueError:
                comments.remove(comment)

        return [BeautifulSoup(comment,"html.parser") for comment in comments]
    
    def add_failure(self, category : str, exception : Exception, url : str) -> Failure:
        self.failures.append(
            Failure(
                category = category,
                error = str(exception),
                url = url 
            )
        )










