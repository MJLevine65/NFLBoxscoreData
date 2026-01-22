from bs4 import BeautifulSoup, ResultSet, Tag
from ..ParserUtils import find_comment, parse_player_id
from ...processor.boxscoreProcessors import PbpProcessor
import pandas as pd

# Play-By-Play Data
def parse_play_by_play_data(comment_parsers : list[BeautifulSoup], boxscore : str) -> pd.DataFrame | None:

    pbp_data : list[dict[str]] = []
    pbp_table = find_comment(comment_parsers, 'div','div_pbp','table_container')
    pbp_info : ResultSet[Tag] = pbp_table.tbody.select("tr:not(.thead)") if pbp_table != None else None

    if pbp_info == None:
        return None

    play_count : int = 0
    for play in list(pbp_info)[1:]:
        play_count += 1
        play_id : str = boxscore + str(play_count)
        play_data = {"play_id" : play_id, "game_id" : boxscore}
        play_data.update({stat.attrs['data-stat'] : stat.text for stat in play})
        raw = list(play)[7].find_all("a")
        play_data['players'] = " ".join([parse_player_id(i['href'])  for i in raw[1:]])
        play_data['detail'] = play_data['detail'].replace(',','')
        play_data['detail'] = play_data['detail'].replace('.','')
        if play_data['quarter'] != '':
            pbp_data.append(play_data)

    dataframe : pd.DataFrame = pd.DataFrame(pbp_data)
    dataframe.rename(columns ={'qtr_time_remain' : 'time', 'pbp_score_hm' : 'home_score', 'pbp_score_aw' : 'away_score', 'detail' : 'description',
                               'exp_pts_before' : 'epb', 'exp_pts_after' : 'epa'}, inplace = True)
    dataframe.replace('', None, inplace = True)

    return dataframe