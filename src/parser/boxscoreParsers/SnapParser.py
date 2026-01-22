import pandas as pd

from bs4 import BeautifulSoup,Tag
from ..ParserUtils import find_comment, parse_boxscore_id, parse_team, parse_stat, parse_player_id
from ...processor.boxscoreProcessors import SnapProcessor

def parse_snap_data(comment_parsers : list[BeautifulSoup], boxscore : str, home : str, away : str) -> pd.DataFrame | None:

    snaps_data : list[dict[str]] = []
    starters : list[str] = []

    home_snap_table = find_comment(comment_parsers, 'div', 'div_home_snap_counts','table_container')
    home_snap_info = home_snap_table.tbody.select("tr:not(.thead)") if home_snap_table != None else None

    home_starter_info = find_comment(comment_parsers, 'div', 'div_home_starters','table_container')
    home_starter_info = home_starter_info.tbody.select("tr:not(.thead)") if home_snap_table != None else None

    away_snap_table = find_comment(comment_parsers, 'div', 'div_vis_snap_counts','table_container')
    away_snap_info = away_snap_table.tbody.select("tr:not(.thead)") if away_snap_table != None else None

    away_starter_info = find_comment(comment_parsers, 'div', 'div_vis_starters','table_container')
    away_starter_info = away_starter_info.tbody.select("tr:not(.thead)") if away_snap_table != None else None

    if home_snap_info == None:
        print("skipped")
        return None
    

    for player in list(home_starter_info) + list(away_starter_info):
        player_info : list[Tag] = list(player)
        player : str =  parse_player_id(player_info[0].find('a')['href'])
        starters.append(player)

    for player in home_snap_info:
        player_info = list(player)
        player : str =  parse_player_id(player_info[0].find('a')['href'])
        starter : str = True if player in starters else False
        player_snaps_data : dict[str] = { "player" : player, "game_id" : boxscore, "team" : home, "starter" : starter}
        player_snaps_data.update({stat.attrs['data-stat'] : stat.text for stat in player_info if stat.attrs['data-stat'] not in ['player']})
        snaps_data.append(player_snaps_data)
                            
        
    for player in away_snap_info:
        player_info = list(player)
        player : str =  parse_player_id(player_info[0].find('a')['href'])
        starter : str = True if player in starters else False
        player_snaps_data : dict[str] = { "player" : player, "game_id" : boxscore, "team" : away, "starter" : starter}
        player_snaps_data.update({stat.attrs['data-stat'] : stat.text for stat in player_info if stat.attrs['data-stat'] not in ['player']})
        snaps_data.append(player_snaps_data)

    snaps_table : pd.DataFrame = pd.DataFrame(snaps_data)

    return SnapProcessor.process_snap_data(snaps_table)