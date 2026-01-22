import pandas as pd

from bs4 import BeautifulSoup,Tag
from ..ParserUtils import find_comment, parse_boxscore_id, parse_team, parse_stat
from ...processor.boxscoreProcessors import GameDataProcessor

def parse_game_data(parser : BeautifulSoup, comment_parsers : list[BeautifulSoup], boxscore : str, week : int , year : int) -> pd.DataFrame:
    game_data = { 'game_id' : parse_boxscore_id(boxscore), "year" : year, "week" : week }

    scorebox : Tag = parser.find("div",class_="scorebox")

    scorebox_teams : list[Tag] = [ tag for tag in scorebox.find_all("a",href = True) if "/teams/" in tag['href']]
    game_data["home"] = parse_team(list(scorebox_teams)[0]['href'])
    game_data["away"] = parse_team(list(scorebox_teams)[1]['href'])

    # Parse Date, Start Time, Stadium
    scorebox_meta : list[Tag] = list(list(scorebox.find_all("div",class_="scorebox_meta"))[0])
    game_data["date"] = scorebox_meta[1].text
    game_data["start_time"] = scorebox_meta[2].text.replace("Start Time: ","")
    game_data["stadium"] = scorebox_meta[3].text.replace("Stadium: ","")

    game_info : list[Tag] = find_comment(comment_parsers,tag = 'div', id_str = 'div_game_info', class_str='table_container').find_all("tr")
    for row in game_info[1:]:
        row = list(row)
        game_data[parse_stat(row[0].text)] = row[1].text

    dataframe : pd.DataFrame = GameDataProcessor.process_boxscore_data(pd.DataFrame([game_data])) 

    return dataframe