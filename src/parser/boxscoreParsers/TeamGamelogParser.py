import pandas as pd

from bs4 import BeautifulSoup,Tag, ResultSet
from ..ParserUtils import find_comment, parse_boxscore_id, parse_team, parse_stat, parse_game_result
from ...processor.boxscoreProcessors import TeamGamelogProcessor

# Teams Stats Data
def parse_team_gamelogs(parser : BeautifulSoup, comment_parsers : list[BeautifulSoup], boxscore : str) -> pd.DataFrame:
    home_team_gamelog : dict[str] = {"game_id" : parse_boxscore_id(boxscore)}
    away_team_gamelog : dict[str] = {"game_id" : parse_boxscore_id(boxscore)}

    scorebox : Tag = parser.find("div",class_="scorebox")
    scorebox_teams : list[Tag] = [ tag for tag in scorebox.find_all("a",href = True) if "/teams/" in tag['href']]
    home_team_gamelog["team"] = parse_team(list(scorebox_teams)[0]['href'])
    home_team_gamelog["opponent"] = parse_team(list(scorebox_teams)[1]['href'])
    away_team_gamelog["team"] = parse_team(list(scorebox_teams)[1]['href'])
    away_team_gamelog["opponent"] = parse_team(list(scorebox_teams)[0]['href'])
    
    home_team_gamelog["home_team"] = True
    away_team_gamelog["home_team"] = False

    # Parse Coaches
    coaches : list[Tag] = scorebox.find_all("div",class_="datapoint")
    home_team_gamelog["coach"] = list(list(coaches)[0])[2].text
    away_team_gamelog["coach"] = list(list(coaches)[1])[2].text

    # Parse Scores
    scores : list[Tag] = list(scorebox.find_all("div",class_ = "score"))
    home_score, away_score =  scores[0].text, scores[1].text
    home_team_gamelog["score"] , home_team_gamelog["opponent_score"] = home_score, away_score
    home_team_gamelog["result"] = parse_game_result(home_score,away_score)
    away_team_gamelog["score"] , away_team_gamelog["opponent_score"] = away_score, home_score
    away_team_gamelog["result"] = parse_game_result(away_score, home_score)

    # Parse Records
    records : list[str] = [item.text.replace("\n"," ") for item in scorebox.find_all("div") if "-" in item.text and len(item.text) <= 6]
    home_team_gamelog["team_record"] = records[0]
    away_team_gamelog["team_record"] = records[1]

    team_stats_data : Tag = find_comment(comment_parsers,'div','div_team_stats','table_container')
    team_stats_info : ResultSet[Tag] = team_stats_data.tbody.select("tr:not(.thead)")
    for stat in team_stats_info: #stat variable in this case applies to the whole row since each row is a stat\\
        stat = list(stat)
        game_stat : str = parse_stat(stat[0].text)
        if game_stat not in ["net_pass_yards", "total_yards", "turnovers"]:
            home_team_gamelog[game_stat] ,home_team_gamelog[f"opp_{game_stat}"] =  stat[1].text, stat[2].text
            away_team_gamelog[game_stat] ,away_team_gamelog[f"opp_{game_stat}"] =  stat[2].text, stat[1].text

    dataframe : pd.DataFrame = TeamGamelogProcessor.process_team_stats(pd.DataFrame([home_team_gamelog, away_team_gamelog]))

    return dataframe