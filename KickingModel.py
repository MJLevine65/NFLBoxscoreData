import pandas as pd
import os,ast
from tqdm import tqdm
import xgboost as xgb
from sklearn.preprocessing import LabelEncoder
import numpy as np
from sklearn.model_selection import train_test_split
def open_file(filename):

    path = os.getcwd() + "//BoxscoreData//" + filename
    return pd.read_excel(path,sheet_name = ["Game Info", "Kick Player Stats"])


def kick_logging(df:pd.DataFrame, file_name: str):
    counter = 0
    year = None
    kick_log = {"Year" : [], "Week" : [],"Quarter" : [], "Duration" : [], "Stadium" : [], "Made" : [], "Distance" : [], "Roof" : [] , "Surface" : [], "Kicker" : [],"Clutch Time" : [],\
                "game_FGA" : [],"game_FGM" : [],"season_FGA" : [],"season_FGM" : [],"career_FGA" : [],"career_FGM" : []}
    season_kickers_log = {}
    career_kickers_log = {}
    for _, row in df.iterrows():
        game_kickers_log = {}
        season_kickers_log = season_kickers_log if row["Year"] == year else {}
        year = row["Year"]
        week = row["Week"]
        if type(row["Weather"]) == str :
            weather = ast.literal_eval(row["Weather"])
        else:
            weather = None
        

        try:
            game_plays = pd.DataFrame(ast.literal_eval(row["Play-By-Play"]))
        except:
            counter += 1
            print(year)
            print(week)
            print(row["Home"])
            continue


        for _, play in game_plays.iterrows():
            if "field goal" not in play["detail"] or "no play" in play["detail"]:
                continue

            if "Penalty" in play["detail"]:
                continue

            kick_log["Year"].append(year)
            kick_log["Week"].append(week)
            kick_log["Stadium"].append(row["Stadium"])
            kick_log["Roof"].append(row["Roof"])
            kick_log["Surface"].append(row["Surface"])
            for weather_stat in ["Temprature","Wind Speed", "Humidity", "Wind Chill"]:
                if weather == None or weather_stat not in weather:
                    if weather_stat not in kick_log:
                        kick_log[weather_stat] = [None]
                    else:
                        kick_log[weather_stat].append(None)
                else:
                    if weather_stat not in kick_log:
                        kick_log[weather_stat] = [int(weather[weather_stat])]
                    else:
                        kick_log[weather_stat].append(int(weather[weather_stat]))

            distance = play["detail"].split("yard field goal")[0].split(" ")[-2].strip()
            distance = int(distance)
            kick_log["Distance"].append(distance)

            team = play["location"].split(" ")[0]


            kicker = " ".join(play["detail"].split("yard field goal")[0].split(" ")[:-2]).strip()
            kick_log["Kicker"].append(kicker)

            #Update Game Log
            if kicker not in game_kickers_log:
                game_kickers_log[kicker] = {"FGA" : 1, "FGM" : 0}
                kick_log["game_FGA"].append(0)
                kick_log["game_FGM"].append(0)
            else:
                kick_log["game_FGA"].append(game_kickers_log[kicker]["FGA"])
                kick_log["game_FGM"].append(game_kickers_log[kicker]["FGM"])
                game_kickers_log[kicker]["FGA"] += 1

            #Update Season Log
            if kicker not in season_kickers_log:
                season_kickers_log[kicker] = {"FGA" : 1, "FGM" : 0}
                kick_log["season_FGA"].append(0)
                kick_log["season_FGM"].append(0)
            else:
                kick_log["season_FGA"].append(season_kickers_log[kicker]["FGA"])
                kick_log["season_FGM"].append(season_kickers_log[kicker]["FGM"])
                season_kickers_log[kicker]["FGA"] += 1

            #Update Career Log
            if kicker not in career_kickers_log:
                career_kickers_log[kicker] = {"FGA" : 1, "FGM" : 0}
                kick_log["career_FGA"].append(0)
                kick_log["career_FGM"].append(0)
            else:
                kick_log["career_FGA"].append(career_kickers_log[kicker]["FGA"])
                kick_log["career_FGM"].append(career_kickers_log[kicker]["FGM"])
                career_kickers_log[kicker]["FGA"] += 1
            
            if "no good" in play["detail"]:
                kick_log["Made"].append(False)
            else:
                kick_log["Made"].append(True)
                game_kickers_log[kicker]["FGM"] += 1
                season_kickers_log[kicker]["FGM"] += 1
                career_kickers_log[kicker]["FGM"] += 1
            
            if (play["quarter"] == "2" or play["quarter"] == '4') and (len(play['qtr_time_remain']) == 0 or int(play['qtr_time_remain'][0]) < 2):
                kick_log["Clutch Time"].append(True)
            else:
                kick_log["Clutch Time"].append(False)

            kick_log["Quarter"].append({"1":1,"2":2,"3":3,"4":4,"OT":5}[play["quarter"]])
            kick_log["Duration"].append(play["qtr_time_remain"])
            

            


    kick_log = pd.DataFrame(kick_log)
    print(kick_log)
    path = os.getcwd() + "//KicksData"
    if not os.path.exists(path):
        os.mkdir(path)
    with pd.ExcelWriter(path + "//" + file_name) as writer:
        kick_log.to_excel(writer,index = False,sheet_name = "Kick Log")


def encode_data(file_path:str):
    def get_features(game_FGA,game_FGM,season_FGA,season_FGM,career_FGA,career_FGM):
        feature_dict = {}

        feature_dict["game_missed_fg"] = False if game_FGA == game_FGM else True

        if season_FGA < 10:
            feature_dict["season_FG%"] = None
        else:
            feature_dict["season_FG%"] = season_FGM/season_FGA

        if career_FGA < 10:
            feature_dict["career_FG%"] = None
        else:
            feature_dict["career_FG%"] = career_FGM/career_FGA
        
        return feature_dict


    df = pd.read_excel(file_path,sheet_name = "Kick Log")
    feature_frame = df.filter(items = ["Stadium","Made","Distance","Roof","Surface","Clutch Time","Temprature","Humidity","Wind Speed","Wind Chill"])

    #Add extra % features
    extra_feature_frame = df.apply(lambda x : get_features(x["game_FGA"],x["game_FGM"],x["season_FGA"],x["season_FGM"],\
                                                           x["career_FGA"],x["career_FGM"]),axis = 1,result_type = "expand")
    feature_frame = pd.concat([feature_frame,extra_feature_frame],axis = 1)
    
    #Set categorical types
    feature_frame.Stadium = feature_frame.Stadium.astype(dtype="category")
    feature_frame.Roof = feature_frame.Roof.astype(dtype="category")
    feature_frame.Surface = feature_frame.Surface.astype(dtype="category")

    #encode categorical types
    encoder = LabelEncoder()
    feature_frame.Stadium = encoder.fit_transform(feature_frame.Stadium)
    feature_frame.Roof = encoder.fit_transform(feature_frame.Roof)
    feature_frame.Surface = encoder.fit_transform(feature_frame.Surface)
    return feature_frame


def create_model_xgb(train_path:str,test_path:str,model_path:str):
    
    train = xgb.DMatrix(train_path)
    test = xgb.DMatrix(test_path)

    params = {}
    booster = xgb.train(params,dtrain = train)
    booster.save_model(model_path)

def test_model_xgb(test_path:str,model_path:str):
    from sklearn.metrics import confusion_matrix
    test = xgb.DMatrix(test_path)
    booster = xgb.Booster(model_file = model_path)
    predictions = booster.predict(test)
    cat_preds = np.array(predictions)
    cat_preds = np.where(cat_preds >= .5,1,0)
    cf = confusion_matrix(test.get_label(),cat_preds)
    print(cf)






        





if __name__ == "__main__":
