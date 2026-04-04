from bs4 import BeautifulSoup, Comment, Tag, ResultSet
import pandas as pd
from pandas import read_html
from io import StringIO


class Parser:
    """Base class for all data parsers with common utility methods"""

    @staticmethod
    def parse_comment_parsers(parser : BeautifulSoup) -> list[BeautifulSoup]:
        """Extract and parse HTML comments containing tables from a BeautifulSoup parser.
        
        Args:
            parser: BeautifulSoup parser to extract comments from.
            
        Returns:
            List of BeautifulSoup parsers for each HTML comment containing tables.
        """
        comments : list[str] = parser.find_all(string = lambda text : isinstance(text, Comment))
        comments = list(set(comments))
        
        #Only want the comments that contain tables
        for comment in comments:
            try:
                read_html(StringIO(comment))
            except ValueError:
                comments.remove(comment)

        return [BeautifulSoup(comment,"html.parser") for comment in comments]

    @staticmethod
    def find_comment(comment_parsers : list[BeautifulSoup], tag : str, id_str : str, class_str : str) -> list[Tag] | None:
        """Find a specific tag within commented HTML sections.
        
        Args:
            comment_parsers: List of BeautifulSoup parsers for HTML comments.
            tag: HTML tag being searched for.
            id_str: ID attribute of tag being searched for.
            class_str: Class attribute of tag being searched for.
        
        Returns:
            Tag matching criteria or None if not found.
        """
        for comment_parser in comment_parsers:
            tags : list[Tag] = comment_parser.find(tag, id = id_str, class_ = class_str)
            if tags != None:
                return tags
        return tags if tags != None else None

    @staticmethod
    def parse_player_id(player_url : str) -> str:
        """
        ExtExtract player ID from player profile URL.
        
        Args:
            player_url: URL string of the player's page on PFR.
        
        Returns:
            Player ID string used by PFR.
        """
        return player_url.split("/")[-1].replace(".htm","")

    @staticmethod
    def parse_boxscore_id(boxscore_url : str) -> str:
        """
        ExtExtract boxscore ID from boxscore URL.
        
        Args:
            boxscore_url: URL string of the boxscore page on PFR.
        
        Returns:
            Boxscore ID string used by PFR.
        """
        return boxscore_url.split("/")[-1].replace(".htm","")

    @staticmethod
    def parse_team(team_url : str) -> str:
        """Extract team abbreviation from team profile URL."""
        return team_url.split("/")[2]

    @staticmethod
    def parse_stat(stat: str) -> str:
        """Convert stat string to standardized column name format"""
        return stat.strip()\
                .replace(" ","_")\
                .replace("/","_")\
                .replace("-","_")\
                .replace(".","").lower()

    @staticmethod
    def parse_game_result(first_score : int, sec_score : int) -> str:
        """Determine game result (win/loss/tie) by comparing scores"""
        if first_score > sec_score:
            return "W"
        elif first_score < sec_score:
            return "L"
        else:
            return "T"
        
    def get_player_stats(self, player_stats_table : Tag, boxscore:str) -> pd.DataFrame:

        player_data : list[dict[str]] = [] 

        player_stats_info : ResultSet[Tag] = player_stats_table.tbody.select("tr:not(.thead)")

        for player in player_stats_info:
            player_info : list[Tag] = list(player)

            player : str =  self.parse_player_id(player_info[0].find('a')['href'])
            team : str = player_info[1].text
            player_stats = {"player" : player, "team" : team, "game_id" : boxscore} 
            player_stats.update({stat.attrs['data-stat'] : self.int_float_check(stat.text)  for stat in player_info if stat.attrs['data-stat'] not in  ["player","team"]})
            player_data.append(player_stats)

        return pd.DataFrame(player_data)

    def int_float_check(self, x : str):
        if x == '':
            return None
        elif "." in x:
            return float(x.replace('%',''))
        else:
            return int(x)

    def select_stats(self, dataframe : pd.DataFrame, selector : str) -> pd.DataFrame:
        pass_cols = [col for col in dataframe.columns if selector in col]
        return dataframe[["player","team","game_id"] + pass_cols]

    def clean_columns(self, dataframe : pd.DataFrame):
        dataframe.drop(columns = [col for col in dataframe if "DROP" in col], inplace = True)
        dataframe.drop(columns = [col for col in dataframe if "per" in col], inplace = True)
        dataframe.drop(columns = [col for col in dataframe if "pct" in col], inplace = True)

        dataframe.rename(columns = {col : col.replace("pass_","") for col in dataframe.columns}, inplace = True)
        dataframe.rename(columns = {col : col.replace("rush_","") for col in dataframe.columns}, inplace = True)
        dataframe.rename(columns = {col : col.replace("rec_","") for col in dataframe.columns}, inplace = True)
        dataframe.rename(columns = {col : col.replace("def_","") for col in dataframe.columns}, inplace = True)

    def clean_int_columns(self, dataframe : pd.DataFrame, int_cols : list[str]) -> pd.DataFrame:
        for col in int_cols:
            dataframe[col].fillna(0, inplace=True)
            dataframe = dataframe.astype({col : int} )
        return dataframe