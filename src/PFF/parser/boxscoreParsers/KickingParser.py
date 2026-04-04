from bs4 import BeautifulSoup
import pandas as pd
from ..Parser import Parser


class KickingParser(Parser):

    def parse(self, comment_parsers : list[BeautifulSoup], boxscore: str, **args) -> pd.DataFrame:

        player_data = {}
        kicking_info = self.find_comment(comment_parsers,'div',f'div_kicking','table_container')
        player_data['kicking'] = self.get_player_stats(kicking_info, boxscore)

        return self.process_kicking_gamelogs(player_data)
    
    def process_kicking_gamelogs(self, player_data : dict[pd.DataFrame]):
        dataframe : pd.DataFrame = player_data['kicking']
        self.clean_columns(dataframe)
        dataframe.rename(columns =\
                        {"xpm" : "xp_made", "xpa" : "xp_attempts", "fgm" : "fg_made","fga" : "fg_attempts",
                        "punt" : "punts", "punts_yds" : "punt_yds"}, inplace = True)
        int_cols = [col for col in dataframe.columns if col not in ['player','team','game_id']]
        dataframe = self.clean_int_columns(dataframe, int_cols)
        return dataframe