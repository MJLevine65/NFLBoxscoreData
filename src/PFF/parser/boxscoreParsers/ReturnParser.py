

from bs4 import BeautifulSoup
import pandas as pd
from ..Parser import Parser


class ReturnParser(Parser):
    """Parser for return data from boxscore pages"""

    def parse(self, comment_parsers : list[BeautifulSoup], boxscore: str, **args) -> pd.DataFrame:

        player_data = {}
        defense_info = self.find_comment(comment_parsers,'div',f'div_returns','table_container')
        player_data['returns'] = self.get_player_stats(defense_info, boxscore)

        return self.process_return_gamelogs(player_data)
    
    def process_return_gamelogs(self, player_data : dict[pd.DataFrame]):
        
        dataframe : pd.DataFrame = player_data['returns']
        self.clean_columns(dataframe)
        dataframe.rename(columns =\
                        {"kick_ret" : "kick_returns", "kick_ret_td" : "kick_ret_tds", "punt_ret" : "punt_returns",
                        "punt_ret_td" : "punt_ret_tds", "punt_ret_long" : "punt_ret_long"}, inplace = True)
        int_cols = [col for col in dataframe.columns if col not in ['player','team','game_id']]
        dataframe = self.clean_int_columns(dataframe, int_cols)
        return dataframe