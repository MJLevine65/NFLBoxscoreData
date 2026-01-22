import pandas as pd
from collections import defaultdict

def process_team_stats(dataframe: pd.DataFrame) -> pd.DataFrame:

    process_passing_data(dataframe)
    process_rushing_data(dataframe)
    process_turnover_data(dataframe)
    process_penalty_data(dataframe)
    process_downs_data(dataframe)
    process_posession(dataframe)

    return dataframe

def process_passing_data(dataframe: pd.DataFrame) -> None:
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

    dataframe.drop(columns = ["cmp_att_yd_td_int", "opp_cmp_att_yd_td_int"], inplace = True)

def process_rushing_data(dataframe: pd.DataFrame) -> None:
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

    dataframe.drop(columns = ["rush_yds_tds", "opp_rush_yds_tds"], inplace = True)

def process_turnover_data(dataframe : pd.DataFrame):
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

    dataframe.drop(columns = ["sacked_yards", "opp_sacked_yards", "opp_fumbles_lost"], inplace = True, errors = 'ignore')

def process_penalty_data(dataframe : pd.DataFrame):
    penalty_cols = defaultdict(list)

    for i,row in dataframe.iterrows():
        if "penalties_yards" in dataframe.columns:
            penalty_data : list[int] = [int(stat) for stat in row["penalties_yards"].split("-")]
            penalty_cols['penalties'].append(penalty_data[0])
            penalty_cols['penalty_yds'].append(penalty_data[1])

    for key, item in penalty_cols.items():
        dataframe[key] = item

    dataframe.drop(columns = ["penalties_yards", "opp_penalties_yards"], inplace = True, errors = 'ignore')

def process_downs_data(dataframe : pd.DataFrame):
    downs_cols = defaultdict(list)

    for i, row in dataframe.iterrows():
        if "first_downs" in dataframe.columns:
            downs_cols['first_downs'].append(int(row['first_downs']))

        if "third_down_conv" in dataframe.columns:
            third_down_data : list[int] =  [int(stat) for stat in row["third_down_conv"].split("-")]
            downs_cols['third_downs'].append(third_down_data[0])
            downs_cols['third_down_conversions'].append(third_down_data[1])

        if "fourth_down_conv" in dataframe.columns:
            fourth_down_data : list[int] =  [int(stat) for stat in row["fourth_down_conv"].split("-")]
            downs_cols['fourth_downs'].append(fourth_down_data[0])
            downs_cols['fourth_down_conversions'].append(fourth_down_data[1])

    for key, item in downs_cols.items():
        dataframe[key] = item

    dataframe.drop(columns = ["opp_first_downs","third_down_conv", "opp_third_down_conv", "fourth_down_conv", "opp_fourth_down_conv"], inplace = True, errors = 'ignore')

def process_posession(dataframe : pd.DataFrame):
    possession_cols = defaultdict(list)

    for i, row in dataframe.iterrows():
        if "time_of_possession" in dataframe.columns:
            possession = row['time_of_possession']
            possession_cols['possession'].append(int(possession.split(":")[0]) * 60 + int(possession.split(":")[1]))

    for key, item in possession_cols.items():
        dataframe[key] = item

    dataframe.drop(columns = ["time_of_possession", "opp_time_of_possession"], inplace = True, errors = 'ignore')







