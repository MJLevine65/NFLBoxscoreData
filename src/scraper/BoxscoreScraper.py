import pandas as pd

from ..database import DatabaseAccessor
from ..parser.boxscoreParsers import GameDataParser, TeamGamelogParser, PlayerGamelogParser, SnapParser, DriveParser, PbpParser
import os

from bs4 import BeautifulSoup, Comment
from logging import info
from ..parser.ParserUtils import find_comment, parse_comment_parsers
from requests import get, Response
from .Scraper import Scraper

class BoxscoreScraper(Scraper):
    def __init__(self):
        super().__init__()
        self.db_accessor = DatabaseAccessor.DatabaseAccessor()

    def fetch_boxscore_data(self, boxscore: str, week : int, year : int, overwrite: bool = False, new_schema : bool = False) -> None:

        url : str = "https://www.pro-football-reference.com/boxscores/" + boxscore + ".htm"

        boxscore_parser : BeautifulSoup = self.make_call(url)

        comment_parsers : list[BeautifulSoup] = parse_comment_parsers(boxscore_parser)

        dataframes : dict[pd.DataFrame] = self.parse_boxscores(boxscore_parser, comment_parsers, boxscore, week, year)

        self.db_accessor.write_data("game_info", "game_id", dataframes['boxscore'])

        self.db_accessor.write_data("team_gamelogs", "game_id, team", dataframes['team_gamelogs'])

        self.db_accessor.write_data("passing_gamelogs", "game_id, player", dataframes['passing_gamelogs'])

        self.db_accessor.write_data("receiving_gamelogs", "game_id, player", dataframes['receiving_gamelogs'])

        self.db_accessor.write_data("rushing_gamelogs", "game_id, player", dataframes['rushing_gamelogs'])

        self.db_accessor.write_data("defense_gamelogs", "game_id, player", dataframes['defense_gamelogs'])

        self.db_accessor.write_data("return_gamelogs", "game_id, player", dataframes['return_gamelogs'])

        self.db_accessor.write_data("kicking_gamelogs", "game_id, player", dataframes['kicking_gamelogs'])

        self.db_accessor.write_data("fumble_gamelogs", "game_id, player", dataframes['fumble_gamelogs'])

        self.db_accessor.write_data("snap_gamelogs", "game_id, player", dataframes['snap_gamelogs'])

        self.db_accessor.write_data("drives", "game_id, team, drive_num", dataframes['drive_data'])

        self.db_accessor.write_data("pbp_data", "play_id", dataframes['pbp_data'])

        # self.db_accessor.write_data("scoring_data", "game_id, team, drive_num", dataframes['scoring_data'])


    def parse_boxscores(self, boxscore_parser : BeautifulSoup, comment_parsers : list[BeautifulSoup], boxscore : str,  week : int, year : int) -> dict[pd.DataFrame]:
        game_info : pd.DataFrame = GameDataParser.parse_game_data(boxscore_parser, comment_parsers, boxscore, week, year)
        home : str = game_info.iloc[0]['home']
        away : str = game_info.iloc[0]['away']
        return {
            'boxscore' : GameDataParser.parse_game_data(boxscore_parser, comment_parsers, boxscore, week, year),
            'team_gamelogs' : TeamGamelogParser.parse_team_gamelogs(boxscore_parser, comment_parsers, boxscore),
            'passing_gamelogs' : PlayerGamelogParser.parse_offense_gamelogs(boxscore_parser, comment_parsers, boxscore, 'passing'),
            'receiving_gamelogs' : PlayerGamelogParser.parse_offense_gamelogs(boxscore_parser, comment_parsers, boxscore, 'receiving'),
            'rushing_gamelogs' : PlayerGamelogParser.parse_offense_gamelogs(boxscore_parser, comment_parsers, boxscore, 'rushing'),
            'defense_gamelogs' :  PlayerGamelogParser.parse_defense_gamelogs(boxscore_parser, comment_parsers, boxscore),
            'return_gamelogs' :  PlayerGamelogParser.parse_return_gamelogs(boxscore_parser, comment_parsers, boxscore),
            'kicking_gamelogs' :  PlayerGamelogParser.parse_kicking_gamelogs(boxscore_parser, comment_parsers, boxscore),
            'fumble_gamelogs' :  PlayerGamelogParser.parse_fumble_gamelogs(boxscore_parser, comment_parsers, boxscore),
            'snap_gamelogs' : SnapParser.parse_snap_data(comment_parsers, boxscore, home, away),
            'drive_data' : DriveParser.parse_drives_data(comment_parsers, boxscore, home, away),
            'pbp_data' : PbpParser.parse_play_by_play_data(comment_parsers, boxscore)
        }


        # scoring_data : pd.DataFrame = parser.parse_scoring_data(parser)
        # home_starters_data, away_starters_data = parser.parse_starters(comment_parsers)
        # home_snaps_data, away_snaps_data = parser.parse_snaps_data(comment_parsers)
        # home_drives_data, away_drives_data = parser.parse_drives_data(comment_parsers)
        # pbp_data : pd.DataFrame = parser.parse_pbp_data(comment_parsers)

        # home : str = game_data['Home'].iloc[0]
        # vis : str = game_data['Away'].iloc[0


    # data = pd.read_csv(data_file)
    # bad_urls = {"boxscore" : [], "errors" : []}
    # def process_url(url:str, year: int, week: int):

    #     url = "https://www.pro-football-reference.com" + url
    #     print(url)
    #     r = requests.get(url)
    #     sleep_fun()
    #     parser = BeautifulSoup(r.text,"html.parser")
    #     comments = parser.find_all(string = lambda text : isinstance(text, Comment))
    #     comments = list(set(comments))
        
    #     #Only want the comments that contain tables
    #     for c in comments:
    #         try:
    #             pd.read_html(c)
    #         except:
    #             comments.remove(c)


    #     comment_parsers = parse_comment_parsers() [BeautifulSoup(comment,"html.parser") for comment in comments]

    #     return {"Year" : year, "Week" : week, "Home" : home, "Away" : vis} | scoring_data | game_info_dict | team_stats_dict | player_stats | starters_dict | snaps | pbp   
    # tqdm.pandas(desc='Progress')
    # new_data = data.progress_apply(lambda x: process_url(x.url, x.year,x.week), axis=1,result_type = 'expand')
    # while True:
    #     try:
    #         new_data.to_csv(file_name,index = False)
    #         break
    #     except:
    #         print("close",file_name)
    #         input()
    # while True:
    #     try:
    #         pd.DataFrame(bad_urls).to_csv(file_name[:-4] + "_bad_urls.csv",index = False)
    #         break
    #     except:
    #         print("close error file")
    #         input()