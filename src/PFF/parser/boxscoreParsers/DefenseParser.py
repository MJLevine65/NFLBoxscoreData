

from bs4 import BeautifulSoup
import pandas as pd
from ..Parser import Parser


class DefenseParser(Parser):

    def parse(self, comment_parsers : list[BeautifulSoup], boxscore: str, **args) -> pd.DataFrame:

        player_data = {}
        defense_info = self.find_comment(comment_parsers,'div',f'div_player_defense','table_container')
        player_data['defense'] = self.get_player_stats(defense_info, boxscore)

        advanced_info = self.find_comment(comment_parsers,'div',f'div_defense_advanced','table_container')
        player_data[f'adv_defense'] = self.get_player_stats(advanced_info, boxscore)

        return self.process_defense_gamelogs(player_data)
    
    def process_defense_gamelogs(self, player_data : dict[pd.DataFrame]):
        if not player_data['adv_defense'].empty:
        
            # Process regular and advanced data
            dataframe = pd.merge(player_data['adv_defense'], player_data['defense'], how = 'left', on = ['player','game_id','team'], suffixes = ['','DROP']) 
        else:
            dataframe = player_data['defense']

        self.clean_columns(dataframe)
        dataframe.rename(columns =\
                        { "int" : "interceptions", "cmp" : "rec_allowed", "cmp_yds" : "rec_yds_allowed",
                        "rating" : "rating_allowed", "air_yds" : "air_yds", "yac" : "yac_allowed",
                        "qb_hurry" : "hurries", "tackles_missed" : "missed_tackles", "cmp_td" : "rec_tds_allowed",
                        "int_yds" : "interception_yds", "int_td" : "pick_sixes", "int_long" : "interception_long", "qb_knockdown" : "knockdowns",
                        "defended" : "passes_defended", "tackles_solo" : "solo_tackles", "tackles_assists" : "assisted_tackles",
                        "tackles_loss" : "tackles_for_loss", "fumbles_rec" : "fumble_rec", "fumbles_td" : "fumble_rec_tds",
                        "fumbles_forced" : "forced_fumbles", "fumbles_yds" : "fumble_yds"}, inplace = True)
        int_cols = [col for col in dataframe.columns if col not in ['player','team','game_id', 'rating_allowed','sacks']]
        dataframe = self.clean_int_columns(dataframe, int_cols)
        dataframe.drop(columns = ['pressures', 'tackles_combined'],inplace = True, errors = 'ignore')
        return dataframe