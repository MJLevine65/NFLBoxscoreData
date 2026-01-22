from bs4 import BeautifulSoup, Comment
import pandas as pd
from pathlib import Path
import requests
from random import randint
from time import time, sleep
from tqdm import tqdm
from typing import Dict
from warnings import filterwarnings
import cloudscraper

#comment input isn't a file
filterwarnings('ignore',message =\
"The input looks more like a filename than markup. You may want to open this file and pass the filehandle into Beautiful Soup." )

class Scraper:
    def __init__(self):
        self.request_interval: int = 3 # Time in seconds to wait between requests
        self.last_request_time: float = time() - 3 # Timestamp of the last request in seconds

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
        scraper = cloudscraper.create_scraper()
        self.sleep()
        #response: requests.Response = requests.get(url, headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36", "Content-Type":"text/html"})
        response = scraper.get(url)
        if response.status_code != 200:
            raise Exception("Request to " + url + " failed with status code " + str(response.status_code))
        return BeautifulSoup(response.text,"html.parser")


if __name__ == "__main__":
    parse_boxscores("BoxscoreData/2023_boxscores.csv","test.csv")









