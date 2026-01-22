import pandas as pd
from bs4 import ResultSet, Tag, BeautifulSoup
from ..ParserUtils import parse_player_id, find_comment
from ...processor.boxscoreProcessors import PlayerGamelogProcessor

def parse_offense_gamelogs(parser : BeautifulSoup, comment_parsers : list[BeautifulSoup], boxscore: str, category: str) -> pd.DataFrame:

    player_data = {}
    offense_info = parser.find('div', id="div_player_offense", class_="table_container")
    player_data['offense'] = get_player_stats(offense_info, boxscore)

    advanced_info = find_comment(comment_parsers,'div',f'div_{category}_advanced','table_container')
    player_data[f'adv_{category}'] = get_player_stats(advanced_info, boxscore)

    fun = {"passing" : PlayerGamelogProcessor.process_passing_gamelogs,
           "receiving" : PlayerGamelogProcessor.process_receiving_gamelogs,
            "rushing" : PlayerGamelogProcessor.process_rushing_gamelogs}[category]

    return fun(player_data)

def parse_defense_gamelogs(parser : BeautifulSoup, comment_parsers : list[BeautifulSoup], boxscore: str) -> pd.DataFrame:

    player_data = {}
    defense_info = find_comment(comment_parsers,'div',f'div_player_defense','table_container')
    player_data['defense'] = get_player_stats(defense_info, boxscore)

    advanced_info = find_comment(comment_parsers,'div',f'div_defense_advanced','table_container')
    player_data[f'adv_defense'] = get_player_stats(advanced_info, boxscore)

    return PlayerGamelogProcessor.process_defense_gamelogs(player_data)

def parse_return_gamelogs(parser : BeautifulSoup, comment_parsers : list[BeautifulSoup], boxscore: str) -> pd.DataFrame:

    player_data = {}
    defense_info = find_comment(comment_parsers,'div',f'div_returns','table_container')
    player_data['returns'] = get_player_stats(defense_info, boxscore)

    return PlayerGamelogProcessor.process_return_gamelogs(player_data)

def parse_kicking_gamelogs(parser : BeautifulSoup, comment_parsers : list[BeautifulSoup], boxscore: str) -> pd.DataFrame:

    player_data = {}
    defense_info = find_comment(comment_parsers,'div',f'div_kicking','table_container')
    player_data['kicking'] = get_player_stats(defense_info, boxscore)

    return PlayerGamelogProcessor.process_kicking_gamelogs(player_data)

def parse_fumble_gamelogs(parser : BeautifulSoup, comment_parsers : list[BeautifulSoup], boxscore: str) -> pd.DataFrame:

    player_data = {}
    info = parser.find('div', id="div_player_offense", class_="table_container")
    player_data['fumble'] = get_player_stats(info, boxscore)

    return PlayerGamelogProcessor.process_fumble_gamelogs(player_data)

def get_player_stats(player_stats_table : Tag, boxscore:str) -> pd.DataFrame:

    player_data : list[dict[str]] = [] 

    player_stats_info : ResultSet[Tag] = player_stats_table.tbody.select("tr:not(.thead)")

    for player in player_stats_info:
        player_info : list[Tag] = list(player)

        player : str =  parse_player_id(player_info[0].find('a')['href'])
        team : str = player_info[1].text
        player_stats = {"player" : player, "team" : team, "game_id" : boxscore} 
        player_stats.update({stat.attrs['data-stat'] : int_float_check(stat.text)  for stat in player_info if stat.attrs['data-stat'] not in  ["player","team"]})
        player_data.append(player_stats)

    return pd.DataFrame(player_data)

def int_float_check(x : str):
    if x == '':
        return None
    elif "." in x:
        return float(x.replace('%',''))
    else:
        return int(x)