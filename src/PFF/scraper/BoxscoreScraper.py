import pandas as pd
import logging
import os

from bs4 import BeautifulSoup
from tqdm import tqdm

from ...database import NFLDatabaseAccessor
from ..parser.boxscoreParsers import GameDataParser, TeamGamelogParser, PlayerGamelogParser, SnapParser, DriveParser, PbpParser, DefenseParser, KickingParser, ReturnParser, ScoringDataParser

from .Scraper import Scraper

class BoxscoreScraper(Scraper):
    def __init__(self):
        super().__init__()
        self.db_accessor = NFLDatabaseAccessor.DatabaseAccessor()
        self.init_logger("BoxscoreScraper", "../data/logs/boxscore_scraper.log")

        # Scrapers
        self.game_info_scraper = GameDataParser.GameDataParser()
        self.team_gamelog_scraper = TeamGamelogParser.TeamGamelogParser()
        self.offense_scraper = PlayerGamelogParser.OffenseParser()
        self.defense_scraper = DefenseParser.DefenseParser()
        self.kicking_scraper = KickingParser.KickingParser()
        self.return_scraper = ReturnParser.ReturnParser()
        self.snap_scraper = SnapParser.SnapParser()
        self.drive_scraper = DriveParser.DriveParser()
        self.pbp_scraper = PbpParser.PbpParser()
        self.scoring_scraper = ScoringDataParser.ScoringDataParser()

    def scrape(self, data):
        for _, row in tqdm(data.iterrows(), total=len(data), desc = f"Fetching Boxscores"):
            url = row['url'].split("/")[-1].replace(".htm","")
            self.fetch_boxscore_data(url,row['week'],row['year'], overwrite = True)

    def fetch_boxscore_data(self, boxscore: str, week : int, year : int, overwrite: bool = False, new_schema : bool = False) -> None:

        url : str = "https://www.pro-football-reference.com/boxscores/" + boxscore + ".htm"

        self.make_call(url)

        self.comment_parsers : list[BeautifulSoup] = self.parse_comment_parsers()

        dataframes : dict[pd.DataFrame] = self.parse_boxscores(boxscore, week, year)

        if dataframes is None:
            print(f"Skipping boxscore {boxscore} due to errors.")
            return
        
        tables = self.load_tables()
        
        for table, df in dataframes.items():
            self.db_accessor.write_data(table, tables[table], df)


    def parse_boxscores(self, boxscore : str,  week : int, year : int) -> dict[pd.DataFrame] | None:
        boxscore_parser = self.parser
        data = {}
        try:
            game_info : pd.DataFrame = self.game_info_scraper.parse(boxscore_parser, self.comment_parsers, boxscore, week, year)
            home : str = game_info.iloc[0]['home']
            away : str = game_info.iloc[0]['away']
        except Exception as e:
            self.add_failure("game_info", e, boxscore)
            print(e)
            return None
        
        data = {'game_info' : game_info}
        scrapers : dict[str, Scraper]= self.load_scrapers()
        
        scraper_args : dict[str, object] = {'parser' : boxscore_parser,
                         'comment_parsers' : self.comment_parsers,
                         'boxscore' : boxscore,
                         'home' : home,
                         'away' : away}
        
        for name, scraper in scrapers.items():
            try:
                data[name] = scraper.parse(**scraper_args)
            except Exception as e:
                self.add_failure(name, e, boxscore)
                self.logger.error(f"Error parsing {name} for boxscore {boxscore}: {str(e)}")
        
        return data
    
    # Returns a map of table names to primary keys
    @staticmethod
    def load_tables() ->  dict[str, str]:
        return {
            "game_info" : "game_id",
            "team_gamelogs" : "game_id, team",
            "offense_gamelogs" : "game_id, player",
            "defense_gamelogs" : "game_id, player",
            "return_gamelogs" : "game_id, player",
            "kicking_gamelogs" : "game_id, player",
            "snap_gamelogs" : "game_id, player",
            "drives" : "game_id, team, drive_num",
            "pbp_data" : "play_id",
            "scoring_data" : "game_id, team, quarter, time"
        }
    
    @staticmethod
    def load_scrapers(self) -> dict[str, Scraper]:
        return {
        'team_gamelogs' : self.team_gamelog_scraper,
        'offense_gamelogs' : self.offense_scraper,
        'defense_gamelogs' : self.defense_scraper,
        'return_gamelogs' : self.return_scraper,
        'kicking_gamelogs' : self.kicking_scraper,
        'snap_gamelogs' : self.snap_scraper,
        'drives' : self.drive_scraper,
        'pbp_data' : self.pbp_scraper,
        'scoring_data' : self.scoring_scraper
        }