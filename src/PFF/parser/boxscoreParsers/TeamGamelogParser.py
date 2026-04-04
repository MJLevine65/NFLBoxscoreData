import pandas as pd
from bs4 import BeautifulSoup, Tag, ResultSet
from collections import defaultdict
from ..Parser import Parser


class TeamGamelogParser(Parser):
    """Parser for team gamelog data from boxscore pages"""

    def parse(self, parser : BeautifulSoup, comment_parsers : list[BeautifulSoup], boxscore : str, **args) -> pd.DataFrame:
        """Parse team gamelog stats for both home and away teams.
        
        Args:
            parser: BeautifulSoup parser of boxscore page.
            comment_parsers: List of parsers for HTML comments.
            boxscore: Boxscore ID string.
        
        Returns:
            DataFrame with processed team gamelog data.
        """
        home_team_gamelog : dict[str] = {"game_id" : self.parse_boxscore_id(boxscore)}
        away_team_gamelog : dict[str] = {"game_id" : self.parse_boxscore_id(boxscore)}

        scorebox : Tag = parser.find("div", class_="scorebox")
        scorebox_teams : list[Tag] = [ tag for tag in scorebox.find_all("a", href=True) if "/teams/" in tag['href']]
        home_team_gamelog["team"] = self.parse_team(list(scorebox_teams)[0]['href'])
        home_team_gamelog["opponent"] = self.parse_team(list(scorebox_teams)[1]['href'])
        away_team_gamelog["team"] = self.parse_team(list(scorebox_teams)[1]['href'])
        away_team_gamelog["opponent"] = self.parse_team(list(scorebox_teams)[0]['href'])
        
        home_team_gamelog["home_team"] = True
        away_team_gamelog["home_team"] = False

        # Parse Coaches
        coaches : list[Tag] = scorebox.find_all("div", class_="datapoint")
        home_team_gamelog["coach"] = list(list(coaches)[0])[2]['href']
        away_team_gamelog["coach"] = list(list(coaches)[1])[2]['href']

        # Parse Scores
        scores : list[Tag] = list(scorebox.find_all("div", class_="score"))
        home_score, away_score = scores[0].text, scores[1].text
        home_team_gamelog["score"], home_team_gamelog["opponent_score"] = home_score, away_score
        home_team_gamelog["result"] = self.parse_game_result(home_score, away_score)
        away_team_gamelog["score"], away_team_gamelog["opponent_score"] = away_score, home_score
        away_team_gamelog["result"] = self.parse_game_result(away_score, home_score)

        # Parse Records
        records : list[str] = [item.text.replace("\n", " ") for item in scorebox.find_all("div") if "-" in item.text and len(item.text) <= 6]
        home_team_gamelog["team_record"] = records[0]
        away_team_gamelog["team_record"] = records[1]

        team_stats_data : Tag = self.find_comment(comment_parsers, 'div', 'div_team_stats', 'table_container')
        team_stats_info : ResultSet[Tag] = team_stats_data.tbody.select("tr:not(.thead)")
        for stat in team_stats_info:
            stat = list(stat)
            game_stat : str = self.parse_stat(stat[0].text)
            if game_stat not in ["net_pass_yards", "total_yards", "turnovers"]:
                home_team_gamelog[game_stat], home_team_gamelog[f"opp_{game_stat}"] = stat[1].text, stat[2].text
                away_team_gamelog[game_stat], away_team_gamelog[f"opp_{game_stat}"] = stat[2].text, stat[1].text

        dataframe : pd.DataFrame = self.process_team_stats(pd.DataFrame([home_team_gamelog, away_team_gamelog]))
        return dataframe

    def process_team_stats(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """Process all team stats data - normalize formats and calculate derived stats.
        
        Args:
            dataframe: Raw team stats DataFrame.
        
        Returns:
            Processed DataFrame with normalized stats.
        """
        self._process_passing_data(dataframe)
        self._process_rushing_data(dataframe)
        self._process_turnover_data(dataframe)
        self._process_penalty_data(dataframe)
        self._process_downs_data(dataframe)
        self._process_possession(dataframe)

        return dataframe

    def _process_passing_data(self, dataframe: pd.DataFrame) -> None:
        """Process passing statistics"""
        passing_cols = defaultdict(list)

        for i, row in dataframe.iterrows():
            passing_data = [int(stat) for stat in row["cmp_att_yd_td_int"].split("-")]
            passing_cols["passing_attempts"].append(passing_data[0])
            passing_cols["passing_completions"].append(passing_data[1])
            passing_cols["passing_yds"].append(passing_data[2])
            passing_cols["passing_tds"].append(passing_data[3])
            passing_cols["offensive_interceptions"].append(passing_data[4])

            opp_passing_data = [int(stat) for stat in row["opp_cmp_att_yd_td_int"].split("-")]
            passing_cols["passing_yds_allowed"].append(opp_passing_data[2])
            passing_cols["passing_tds_allowed"].append(opp_passing_data[3])
            passing_cols["defensive_interceptions"].append(opp_passing_data[4])
            
        for key, item in passing_cols.items():
            dataframe[key] = item

        dataframe.drop(columns=["cmp_att_yd_td_int", "opp_cmp_att_yd_td_int"], inplace=True)

    def _process_rushing_data(self, dataframe: pd.DataFrame) -> None:
        """Process rushing statistics"""
        rushing_cols = defaultdict(list)

        for i, row in dataframe.iterrows():
            rushing_data : list[int] = [int(stat) for stat in row["rush_yds_tds"].split("-")]
            rushing_cols['rushing_attempts'].append(rushing_data[0])
            rushing_cols['rushing_yds'].append(rushing_data[1])
            rushing_cols['rushing_tds'].append(rushing_data[2])

            opp_rushing_data : list[int] = [int(stat) for stat in row["opp_rush_yds_tds"].split("-")]
            rushing_cols['rushing_yds_allowed'].append(opp_rushing_data[1])
            rushing_cols['rushing_tds_allowed'].append(opp_rushing_data[2])
        for key, item in rushing_cols.items():
            dataframe[key] = item

        dataframe.drop(columns=["rush_yds_tds", "opp_rush_yds_tds"], inplace=True)

    def _process_turnover_data(self, dataframe : pd.DataFrame):
        """Process turnover and sack statistics"""
        turnover_cols = defaultdict(list)

        for i, row in dataframe.iterrows():

            if "sacked_yards" in dataframe.columns:
                sack_data : list[int] = [int(stat) for stat in row["sacked_yards"].split("-")]
                turnover_cols['sacks_taken'].append(sack_data[0])
                turnover_cols['sack_yds_lost'].append(sack_data[1])

                opp_sack_data : list[int] = [int(stat) for stat in row["opp_sacked_yards"].split("-")]
                turnover_cols['sacks'].append(opp_sack_data[0])
                turnover_cols['sack_yds'].append(opp_sack_data[1])

            if "fumbles_lost" in dataframe.columns:
                fumble_data : list[int] = [int(stat) for stat in row["fumbles_lost"].split("-")]
                opp_fumble_data : list[int] = [int(stat) for stat in row.get("opp_fumbles_lost", None).split("-")]
                if len(fumble_data) > 1:
                    turnover_cols['fumbles'].append(fumble_data[0])
                    turnover_cols['fumbles_lost'].append(fumble_data[1])
                    turnover_cols['forced_fumbles'].append(opp_fumble_data[0])
                    turnover_cols['forced_fumbles_recovered'].append(opp_fumble_data[1])
                else:
                    turnover_cols['fumbles'].append(fumble_data[0])
                    turnover_cols['fumbles_lost'].append(fumble_data[1])

        for key, item in turnover_cols.items():
            dataframe[key] = item

        dataframe.drop(columns=["sacked_yards", "opp_sacked_yards", "opp_fumbles_lost"], inplace=True, errors='ignore')

    def _process_penalty_data(self, dataframe : pd.DataFrame):
        """Process penalty statistics"""
        penalty_cols = defaultdict(list)

        for i, row in dataframe.iterrows():
            if "penalties_yards" in dataframe.columns:
                penalty_data : list[int] = [int(stat) for stat in row["penalties_yards"].split("-")]
                penalty_cols['penalties'].append(penalty_data[0])
                penalty_cols['penalty_yds'].append(penalty_data[1])

        for key, item in penalty_cols.items():
            dataframe[key] = item

        dataframe.drop(columns=["penalties_yards", "opp_penalties_yards"], inplace=True, errors='ignore')

    def _process_downs_data(self, dataframe : pd.DataFrame):
        """Process down conversion statistics"""
        downs_cols = defaultdict(list)

        for i, row in dataframe.iterrows():
            if "first_downs" in dataframe.columns:
                downs_cols['first_downs'].append(int(row['first_downs']))

            if "third_down_conv" in dataframe.columns:
                third_down_data : list[int] = [int(stat) for stat in row["third_down_conv"].split("-")]
                downs_cols['third_downs'].append(third_down_data[0])
                downs_cols['third_down_conversions'].append(third_down_data[1])

            if "fourth_down_conv" in dataframe.columns:
                fourth_down_data : list[int] = [int(stat) for stat in row["fourth_down_conv"].split("-")]
                downs_cols['fourth_downs'].append(fourth_down_data[0])
                downs_cols['fourth_down_conversions'].append(fourth_down_data[1])

        for key, item in downs_cols.items():
            dataframe[key] = item

        dataframe.drop(columns=["opp_first_downs", "third_down_conv", "opp_third_down_conv", "fourth_down_conv", "opp_fourth_down_conv"], inplace=True, errors='ignore')

    def _process_possession(self, dataframe : pd.DataFrame):
        """Process time of possession statistics"""
        possession_cols = defaultdict(list)

        for i, row in dataframe.iterrows():
            if "time_of_possession" in dataframe.columns:
                possession = row['time_of_possession']
                possession_cols['possession'].append(int(possession.split(":")[0]) * 60 + int(possession.split(":")[1]))

        for key, item in possession_cols.items():
            dataframe[key] = item

        dataframe.drop(columns=["time_of_possession", "opp_time_of_possession"], inplace=True, errors='ignore')

        return dataframe