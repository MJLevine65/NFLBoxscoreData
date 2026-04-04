from .Scraper import Scraper
from bs4 import BeautifulSoup, Comment
from logging import getLogger, info
import pandas as pd
from pathlib import Path
import requests
from tqdm import tqdm

import os

class YearScraper(Scraper):
    def __init__(self):
        super().__init__()

    def scrape_seasons(self, year_interval: tuple[int,int]):
        year_start: int = year_interval[0]
        year_end: int = year_interval[1]
        parser: BeautifulSoup

    def fetch_boxscore_urls(self, year_interval: tuple[int,int]):
        year_start: int = year_interval[0]
        year_end: int = year_interval[1]
        parser: BeautifulSoup
        weeks: list[str]
        parser_urls: list[str]
        path: Path = Path(__file__)


        logger = getLogger(__name__)
        logger.warning("Fetching Boxscore URLs for years " + str(year_start) + " to " + str(year_end))

        
        for year in [str(i) for i in range(year_start,year_end+1) ]:

            logger.warning("Fetching Boxscore URLs for year " + year)
            data: dict[str: list[str]] = {'url' : [], 'year' : [], 'week' : []}
            parser = self.make_call("https://www.pro-football-reference.com/years/" + year + "/")

            parser_urls = [item['href'] for item in parser.find_all("a",href = True)]
            weeks = list(set([url for url in parser_urls if str(year) + "/week_" in url]))
            logger.warning("Found " + str(len(weeks)) + " weeks in " + year)

            weeks.sort(key=lambda x: int(x.split("week_")[1].split(".")[0]))

            print(weeks)
            for week, url in enumerate(weeks):
                logger.warning("Fetching Boxscore URLs for week " + str(week+1))
                parser = self.make_call("https://www.pro-football-reference.com" + url)
                parser_urls = [item['href'] for item in parser.find_all("a",href = True)]
                for item in parser_urls:
                    if valid_boxscore_url(item) and item not in data['url']:
                        data['url'].append("https://www.pro-football-reference.com" +item)
                        data['year'].append(year)
                        data['week'].append(week+1)
            df = pd.DataFrame(data)
            data_directory  = Path(os.getcwd() + "/data/urls/boxscores/")

            print("Saving boxscore URLs for year " + year + " to " + str(data_directory / (year + "_boxscores.csv")))
            if not data_directory.exists():
                data_directory.mkdir(parents = True, exist_ok = True)

            df.to_csv(data_directory / (year + "_boxscores.csv"),index = False)

def valid_boxscore_url(url : str) -> bool:
    if "/boxscores/" in url and url.split("boxscores/")[1] not in ["", "game-scores.htm", "game_scores_find.cgi"]:
        return True
    return False
