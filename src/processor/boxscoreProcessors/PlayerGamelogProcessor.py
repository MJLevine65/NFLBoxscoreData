import pandas as pd


def process_player_offense_gamelogs(player_data : dict[pd.DataFrame]):

    if player_data['adv_passing'].empty:
        return player_data['offense']
    
    # Process regular and advanced data
    dataframe : pd.DataFrame = player_data.pop('offense')
    for _, item in player_data.items():
        dataframe = pd.merge(dataframe, item, how = 'left', on = ['player','game_id','team'])
    return dataframe

def process_passing_gamelogs(player_data : dict[pd.DataFrame]):

    if player_data['adv_passing'].empty:
        return select_stats(player_data['offense'], 'pass')
    
    # Process regular and advanced data
    dataframe : pd.DataFrame = player_data.pop('offense')
    dataframe = pd.merge(player_data['adv_passing'], select_stats(dataframe, 'pass'), how = 'left', on = ['player','game_id','team'], suffixes = ['','DROP']) 
    clean_columns(dataframe)
    dataframe.rename(columns =\
                    { "cmp" : "completions", "att" : "attempts", "yds" : "yards", "td" : "touchdowns", "int" : "interceptions", "yac" : "yds_after_catch",
                        "first_down" : "first_downs", "target_yds" : "int_air_yds", "sacked_yds" : "sack_yds", "air_yds" : "air_yds",
                     "sacked" : "sacks", "blitzed" : "blitzes", "hurried" : "hurries", "pressured" : "pressures",
                    }, inplace = True)
    dataframe['first_downs'] = dataframe['first_downs'].fillna(0)
    dataframe = dataframe.astype({'first_downs' : int} )
    dataframe.drop(columns = ['pressures'],inplace = True, errors = 'ignore')
    int_cols = [col for col in dataframe.columns if col not in ['player','team','game_id','rating']]
    dataframe = clean_int_columns(dataframe, int_cols)
    return dataframe

def process_receiving_gamelogs(player_data : dict[pd.DataFrame]):

    if player_data['adv_receiving'].empty:
        return select_stats(player_data['offense'], 'rec')
    
    # Process regular and advanced data
    dataframe : pd.DataFrame = player_data.pop('offense')
    dataframe = pd.merge(player_data['adv_receiving'], select_stats(dataframe, 'rec'), how = 'left', on = ['player','game_id','team'], suffixes = ['','DROP']) 
    clean_columns(dataframe)
    dataframe.rename(columns =\
                    {"rec" : "receptions", "yds" : "yards", "td" : "touchdowns", "first_down" : "first_downs",
                     "air_yds" :  "air_yds", "target_int" : "interceptions", "yac" : "yds_after_catch"}, inplace = True)
    int_cols = [col for col in dataframe.columns if col not in ['player','team','game_id', 'adot','rating']]
    dataframe = clean_int_columns(dataframe, int_cols)
    return dataframe

def process_rushing_gamelogs(player_data : dict[pd.DataFrame]):

    if player_data['adv_rushing'].empty:
        return select_stats(player_data['offense'], 'rush')
    
    # Process regular and advanced data
    dataframe : pd.DataFrame = player_data.pop('offense')
    dataframe = pd.merge(player_data['adv_rushing'], select_stats(dataframe, 'rush'), how = 'left', on = ['player','game_id','team'], suffixes = ['','DROP']) 
    clean_columns(dataframe)
    dataframe.rename(columns =\
                    {"att" : "attempts", "yds" : "yards", "td" : "touchdowns", "yac" : "yds_after_contact",
                     "first_down" : "first_downs", "yds_before_contact" : "yds_before_contact"}, inplace = True)
    int_cols = [col for col in dataframe.columns if col not in ['player','team','game_id',]]
    dataframe = clean_int_columns(dataframe, int_cols)
    
    return dataframe

def process_defense_gamelogs(player_data : dict[pd.DataFrame]):

    if not player_data['adv_defense'].empty:
    
        # Process regular and advanced data
        dataframe = pd.merge(player_data['adv_defense'], player_data['defense'], how = 'left', on = ['player','game_id','team'], suffixes = ['','DROP']) 
    else:
        dataframe = player_data['defense']

    clean_columns(dataframe)
    dataframe.rename(columns =\
                    { "int" : "interceptions", "cmp" : "rec_allowed", "cmp_yds" : "rec_yds_allowed",
                     "rating" : "rating_allowed", "air_yds" : "air_yds", "yac" : "yac_allowed",
                     "qb_hurry" : "hurries", "tackles_missed" : "missed_tackles", "cmp_td" : "rec_tds_allowed",
                     "int_yds" : "interception_yds", "int_td" : "pick_sixes", "int_long" : "interception_long", "qb_knockdown" : "knockdowns",
                     "defended" : "passes_defended", "tackles_solo" : "solo_tackles", "tackles_assists" : "assisted_tackles",
                     "tackles_loss" : "tackles_for_loss", "fumbles_rec" : "fumble_rec", "fumbles_td" : "fumble_rec_tds",
                     "fumbles_forced" : "forced_fumbles", "fumbles_yds" : "fumble_yds"}, inplace = True)
    int_cols = [col for col in dataframe.columns if col not in ['player','team','game_id', 'rating_allowed','sacks']]
    dataframe = clean_int_columns(dataframe, int_cols)
    dataframe.drop(columns = ['pressures', 'tackles_combined'],inplace = True, errors = 'ignore')
    return dataframe

def process_return_gamelogs(player_data : dict[pd.DataFrame]):
    
    dataframe : pd.DataFrame = player_data['returns']
    clean_columns(dataframe)
    dataframe.rename(columns =\
                    {"kick_ret" : "kick_returns", "kick_ret_td" : "kick_ret_tds", "punt_ret" : "punt_returns",
                      "punt_ret_td" : "punt_ret_tds", "punt_ret_long" : "punt_ret_long"}, inplace = True)
    int_cols = [col for col in dataframe.columns if col not in ['player','team','game_id']]
    dataframe = clean_int_columns(dataframe, int_cols)
    return dataframe

def process_kicking_gamelogs(player_data : dict[pd.DataFrame]):
    
    dataframe : pd.DataFrame = player_data['kicking']
    clean_columns(dataframe)
    dataframe.rename(columns =\
                    {"xpm" : "xp_made", "xpa" : "xp_attempts", "fgm" : "fg_made","fga" : "fg_attempts",
                     "punt" : "punts", "punts_yds" : "punt_yds"}, inplace = True)
    int_cols = [col for col in dataframe.columns if col not in ['player','team','game_id']]
    dataframe = clean_int_columns(dataframe, int_cols)
    return dataframe

def process_fumble_gamelogs(player_data : dict[pd.DataFrame]):
    
    dataframe : pd.DataFrame = player_data['fumble']
    clean_columns(dataframe)
    dataframe = dataframe[['game_id','player','team','fumbles','fumbles_lost']]
    int_cols = [col for col in dataframe.columns if col not in ['player','team','game_id']]
    dataframe = clean_int_columns(dataframe, int_cols)
    return dataframe

def select_stats(dataframe : pd.DataFrame, selector : str) -> pd.DataFrame:
    pass_cols = [col for col in dataframe.columns if selector in col]
    return dataframe[["player","team","game_id"] + pass_cols]

def clean_columns(dataframe : pd.DataFrame):
    dataframe.drop(columns = [col for col in dataframe if "DROP" in col], inplace = True)
    dataframe.drop(columns = [col for col in dataframe if "per" in col], inplace = True)
    dataframe.drop(columns = [col for col in dataframe if "pct" in col], inplace = True)

    dataframe.rename(columns = {col : col.replace("pass_","") for col in dataframe.columns}, inplace = True)
    dataframe.rename(columns = {col : col.replace("rush_","") for col in dataframe.columns}, inplace = True)
    dataframe.rename(columns = {col : col.replace("rec_","") for col in dataframe.columns}, inplace = True)
    dataframe.rename(columns = {col : col.replace("def_","") for col in dataframe.columns}, inplace = True)

def clean_int_columns(dataframe : pd.DataFrame, int_cols : list[str]) -> pd.DataFrame:
    for col in int_cols:
        dataframe[col].fillna(0, inplace=True)
        dataframe = dataframe.astype({col : int} )
    return dataframe




