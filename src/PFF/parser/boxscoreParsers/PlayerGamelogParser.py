import pandas as pd
from bs4 import ResultSet, Tag, BeautifulSoup
import numpy as np
from ..Parser import Parser

class OffenseParser(Parser):
    """Parser for player gamelog data from boxscore pages"""

    def parse(self, parser : BeautifulSoup, comment_parsers : list[BeautifulSoup], boxscore: str, **args) -> pd.DataFrame:

        player_data = {}
        offense_info = parser.find('div', id="div_player_offense", class_="table_container")
        player_data['offense'] = self.get_player_stats(offense_info, boxscore)

        fun = {"passing" : self.process_passing_gamelogs,
                "receiving" : self.process_receiving_gamelogs,
                "rushing" : self.process_rushing_gamelogs}
        
        dataframe : pd.DataFrame =  self.process_fumble_gamelogs(player_data['offense'])

        for cat in fun.keys():
            advanced_info = self.find_comment(comment_parsers,'div',f'div_{cat}_advanced','table_container')
            player_data[f'adv_{cat}'] = self.get_player_stats(advanced_info, boxscore)

            dataframe = pd.merge(dataframe, fun[cat](player_data), how = 'outer', on = ['player','game_id','team'], suffixes = ['','DROP'])

        dataframe.replace({np.nan: None}, inplace = True)
        int_cols = [col for col in dataframe.columns if col not in ['player','team','game_id', 'pass_rating','tgt_rating','adot']]
        dataframe =  self.clean_int_columns(dataframe, int_cols)

        return dataframe

    def process_passing_gamelogs(self, player_data : dict[pd.DataFrame]):

        if player_data['adv_passing'].empty:
            return  self.select_stats(player_data['offense'], 'pass')
        
        # Process regular and advanced data
        dataframe : pd.DataFrame = player_data['offense']
        dataframe = pd.merge(player_data['adv_passing'],  self.select_stats(dataframe, 'pass'), how = 'left', on = ['player','game_id','team'], suffixes = ['','DROP']) 
        self.clean_columns(dataframe)
        dataframe.rename(columns =\
                        { "cmp" : "pass_cmps", "att" : "pass_attempts", "drops" : "pass_drops", "poor_throws" : "poor_throws",
                        "yds" : "pass_yards", "air_yds" : "pass_air_yds", "target_yds" : "int_air_yds", "yac" : "pass_yac", "long" : "pass_long",
                        "td" : "pass_tds", "int" : "interceptions", "yac" : "pass_yac", "first_down" : "pass_1D",
                        "sacked_yds" : "sack_yds", "sacked" : "sacks", "blitzed" : "blitzes", "hurried" : "hurries", "pressured" : "pressures",
                        }, inplace = True)
        dataframe['pass_1D'] = dataframe['pass_1D'].fillna(0)
        dataframe = dataframe.astype({'pass_1D' : int} )
        dataframe.drop(columns = ['pressures'],inplace = True, errors = 'ignore')
        return dataframe

    def process_receiving_gamelogs(self, player_data : dict[pd.DataFrame]):

        if player_data['adv_receiving'].empty:
            return  self.select_stats(player_data['offense'], 'rec')
        
        # Process regular and advanced data
        dataframe : pd.DataFrame = player_data['offense']
        dataframe = pd.merge(player_data['adv_receiving'],  self.select_stats(dataframe, 'rec'), how = 'left', on = ['player','game_id','team'], suffixes = ['','DROP']) 
        self.clean_columns(dataframe)
        dataframe.rename(columns =\
                        {"rec" : "receptions", "drops" : "rec_drops", "yds" : "rec_yards", "yac" : "rec_yac", "long" : "rec_long", "air_yds" : "rec_air_yds",
                        "td" : "rec_tds", "first_down" : "rec_1D", "target_int" : "tgt_ints", "broken_tackles" : "rec_bt", "rating" : "tgt_rating"}, inplace = True)
        return dataframe

    def process_rushing_gamelogs(self, player_data : dict[pd.DataFrame]):

        if player_data['adv_rushing'].empty:
            return  self.select_stats(player_data['offense'], 'rush')
        
        # Process regular and advanced data
        dataframe : pd.DataFrame = player_data['offense']
        dataframe = pd.merge(player_data['adv_rushing'],  self.select_stats(dataframe, 'rush'), how = 'left', on = ['player','game_id','team'], suffixes = ['','DROP']) 
        self.clean_columns(dataframe)
        dataframe.rename(columns =\
                        {"att" : "rush_attempts", "yds" : "rush_yards", "td" : "rush_tds", "yac" : "rush_yac",
                        "first_down" : "rush_1D", "yds_before_contact" : "rush_ybc", "long" : "rush_long", "broken_tackles" : "rush_bt"}, inplace = True)
        
        return dataframe
    
    def process_fumble_gamelogs(self, dataframe: pd.DataFrame):

        self.clean_columns(dataframe)
        dataframe = dataframe[['game_id','player','team','fumbles','fumbles_lost']]
        int_cols = [col for col in dataframe.columns if col not in ['player','team','game_id']]
        dataframe = self.clean_int_columns(dataframe, int_cols)
        return dataframe
 



