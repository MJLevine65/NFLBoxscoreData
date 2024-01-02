import pandas as pd
import numpy as np
import ast
import time

"""
def fun(hom,awa):
    if hom == "{}" and awa != "{}":
        r = ast.literal_eval(awa)
        a = pd.DataFrame(r)
        tms = list(a['team'].unique())
        if len(tms) == 2:
            away_s = a.loc[a["team"] == tms[0]].to_dict('list')
            home_s = a.loc[a["team"] == tms[1]].to_dict('list')
            return {"Home Adv Def Player Stats" : home_s} | { "Away Adv Def Player Stats" : away_s }
    return {"Home Adv Def Player Stats" : hom } | { "Away Adv Def Player Stats" : awa }
"""
def combine_csvs(datafiles: list, filename: str):
    dfs = []
    for file in datafiles:
        dfs.append(pd.read_csv(file))
    datafile = pd.concat(dfs,axis = 0)
    for index,row in datafile.iterrows():
        try:
            int(row["Year"])
        except:
            datafile.drop(index,axis = 0,inplace = True)
    datafile.to_csv(filename,index = False)
def process_data(data_file: str, file_name: str):
    data = pd.read_csv(data_file)
    def recs(hom,awa):
        return {"Home Record": nodate(hom)} | {"Away Record": nodate(awa)}
    
    def nodate(dstr:str):
        if "-" in dstr:
            dstr = dstr.split("-")
        else:
            dstr = dstr.split("/")
        d = {'Jan':1,'Feb':2,'Mar':3,'Apr':4,'May':5,'Jun':6,'Jul':7,'Aug':8,'Sep':9,'Oct':10,'Nov':11,'Dec':12}
        if dstr[0] in d:
            dstr[0] = d[dstr[0]]
        else:
            dstr[0] = int(dstr[0])
        if dstr[1] in d:
            dstr[1] = d[dstr[1]]
        else:
            dstr[1] = int(dstr[1])
        if len(dstr) == 3 and len(dstr[2]) > 2:
            dstr[2] = int(dstr[2][-2:])
        elif len(dstr) == 3:
            dstr[2] = int(dstr[2])
        return dstr
    

    def parse_weather(weather):
        if type(weather) == str:
            w = {}
            weather = weather.split(",")
            for item in weather:
                if "degrees" in item:
                    w["Temprature"] = int(item.split(" ")[0])
                elif "mph" in item:
                    w["Wind Speed"] = int(item.split(" ")[2])
                elif "humidity" in item:
                    w["Humidity"] = int(item.split(" ")[3][:-1])
                elif "no wind" in item:
                    w["Wind Speed"] = 0
                elif "wind chill" in item:
                    w["Wind Chill"] = int(item.split(" ")[3])
                else:
                    print(item)
            return {"Weather" : w }
        else:
            return


    def get_time(d,t):
        if type(t) == str:
            t = t[:-2]
            t = t.split(":")
            h = int(t[0])
            if h != 2:
                h += 12
            m = int(t[1])
            d = d.split(" ")
            y = int(d[3])
            day = int(d[2][:-1])
            month = {'Jan':1,'Feb':2,'Mar':3,'Apr':4,'May':5,'Jun':6,'Jul':7,'Aug':8,'Sep':9,'Oct':10,'Nov':11,'Dec':12}[d[1]]

            dtdict = {"hour": [h], "minute" : [m], "year" : [y], "day" : [day], "month" : [month]}
            return pd.to_datetime(dtdict)
        return None
    
    def ps_table(home,away,year,week,ht,at):
        game_dict = {"Year": year,"Week" : week, "Home" : ht, "Away" : at}
        if type(home) == str and home != "{}":
            home = ast.literal_eval(home)
            hplayers = home['player']
            for stat in list(home.keys())[2:]:
                stat_dict = {}
                for i in range(len(hplayers)):
                    stat_dict[hplayers[i]] = int(home[stat][i]) if "." not in home[stat][i] else \
                        float(home[stat][i][:-1]) if "%" in home[stat][i] else float(home[stat][i])
                game_dict["Home " + stat] = stat_dict
        
        if type(away) == str and away != "{}":
            away = ast.literal_eval(away)
            aplayers = away['player']
            for stat in list(away.keys())[2:]:
                stat_dict = {}
                for i in range(len(aplayers)):
                    stat_dict[aplayers[i]] = int(away[stat][i]) if "." not in away[stat][i] else \
                        float(away[stat][i][:-1]) if "%" in away[stat][i] else float(away[stat][i])
                game_dict["Away " + stat] = stat_dict
        return game_dict
        
    def starter_table(home,away,year,week,ht,at):
        game_dict = {"Year": year,"Week" : week, "Home" : ht, "Away" : at}
        if type(home) == str:
            home = ast.literal_eval(home)
            for pos in list(home.keys()):
                game_dict["Home " + pos] = home[pos][0] if len(home[pos]) == 1 else home[pos]
        
        if type(away) == str:
            away = ast.literal_eval(away)
            for pos in list(away.keys()):
                game_dict["Away " + pos] = away[pos][0] if len(away[pos]) == 1 else away[pos]
            return game_dict
        
    def ts_table(home,away,year,week,ht,at):
        def parse_teamstat(teamstat:str):
            if "-" in teamstat:
                statstr=teamstat.split("-")
                i = 0
                while i < len(statstr):
                    if statstr[i] == '':
                        statstr[i+1] = '-' + statstr[i+1]
                        statstr.remove('')
                    i += 1    
                if len(statstr) == 1:
                        return int(teamstat)
                return [int(stat) for stat in statstr]
        
            if ":"in teamstat:
                min = teamstat.split(":")
                r_int = int(min[0]) + float(min[1])/60
                return r_int
            
            if teamstat == '':
                return None
        game_dict = {"Year": year,"Week" : week, "Home" : ht, "Away" : at}
        if type(home) == str:
            home = ast.literal_eval(home)
            for stat in list(home.keys()):
                game_dict["Home " + stat] = parse_teamstat(home[stat][0])
        
        if type(away) == str:
            away = ast.literal_eval(away)
            for stat in list(away.keys()):
                game_dict["Away " + stat] = parse_teamstat(away[stat][0])
        return game_dict
            
    def scoring_table(sd:str,year:int,week:int):
        game_dict = {"Year": year,"Week" : week}
        type_dict = {"Safety" : "Safety", "yard field goal" : "Field Goal", "defensive extra point return" : "Def XP Ret",\
        "interception return" : "Int Ret TD", "interception in end zone" : "Int Ret TD", "fumble return" : "Fum Ret TD",\
        "fumble recovery" : "Fum Rec TD", "yard pass from" : "Pass TD", "yard rush" : "Rush TD", "kickoff return" : 'Kickoff Ret TD',\
        "blocked punt return" : "Blocked Punt Ret TD" , "punt return" : "Punt Ret TD" , "blocked punt recovery" : "Blocked Punt Rec TD",\
        "kickoff recovery in end zone" : "Kickoff Rec TD", "yard blocked field goal return" : "Blocked FG Ret TD"}
        type_dict2 = {"kick" : "xp","run" : "2p_run", "pass" : "2p_pass"}
        sd = ast.literal_eval(sd)
        game_dict = {"Scoring Data" : {}}
        for i in range(len(sd["description"])):
            score_dict = {"Quarter": sd['quarter'][i], "Team" : sd["team"][i],\
                           "Away Score" : int(sd["vis_team_score"][i]), "Home Score" : int(sd["home_team_score"][i])}
            if "time" in sd:
                score_dict["Time"] = sd["time"][i]
            score_desc =  sd["description"][i]
            score_dict["Description"] = score_desc
            for score_type in type_dict:
                if score_type in score_desc:
                    score_dict["Type"] = type_dict[score_type]
                    break
            tokens = score_desc.replace(score_type,"").split()
            distance = [t for t in tokens if t.isdigit() or t[1:].isdigit()]
            if len(distance) != 0:
                score_dict["Distance"] = int(distance[0])
            elif "end zone" in score_desc and score_type != "Safety":
                score_dict["Distance"] = 0
            else:
                score_dict["Distance"] = None
            if score_dict["Type"] in ["Int Ret TD","Fum Ret TD","Fum Rec TD","Rush TD",'Kickoff Ret TD',"Blocked Punt Ret TD" , "Punt Ret TD" ,"Blocked Punt Rec TD",\
                 "Kickoff Rec TD","Blocked FG Ret TD","Field Goal"] and "end zone" not in score_desc:
                score_dict["Scorer"] = score_desc.split(distance[0])[0].strip()
                score_dict["Passer"] = None
            elif score_dict["Type"] == "Pass TD":
                score_dict["Scorer"] = score_desc.split(distance[0])[0].strip()
                score_dict["Passer"] = score_desc.replace(score_type,"").split(distance[0])[1].split(" (")[0].strip()
            elif score_dict["Type"] == "Def XP Ret":
                score_dict["Scorer"] = score_desc.split(" defe")[0]
                score_dict["Passer"] = None
            else:
                score_dict["Scorer"] = None
                score_dict["Passer"] = None
            

            if "(" not in score_desc:
                score_dict["xp/2p"] = None
            else:
                end_type = score_desc.split("(")[1][:-1]
                for score_type in type_dict2:
                    if score_type in end_type:
                        if "failed" in end_type:
                            score_dict["xp/2p"] = type_dict2[score_type] + "_fail"
                        else:
                            score_dict["xp/2p"] = type_dict2[score_type]
                        break
                players = end_type.replace(score_type,"").replace("failed","")
                if "from" in players:
                    score_dict["xp/2p_Scorer"] = players.split("from")[0].strip()
                    score_dict["xp/2p_Passer"] = players.split("from")[1].strip()
                else:
                    score_dict["xp/2p_Scorer"] = players.strip()
                    score_dict["xp/2p_Passer"] = None
            for stat in score_dict.keys():
                if stat not in game_dict["Scoring Data"]:
                    game_dict["Scoring Data"][stat] = [score_dict[stat]]
                else:
                    game_dict["Scoring Data"][stat] += [score_dict[stat]]
        return game_dict



    records = data.apply(lambda x : recs(x[18],x[19]),axis = 1, result_type = 'expand')
    data["Home Record"],data["Away Record"] = records["Home Record"],records["Away Record"]

    data["Weather"] = data.apply(lambda x : parse_weather(x["Weather"]),axis = 1, result_type = 'expand')

    data["DateTime"] = data.apply(lambda x : get_time(x["Date"],x["Start time"]),axis = 1,result_type = "expand")

    data.Attendance = data.apply(lambda x : int(x.Attendance.replace(",","")) if type(x.Attendance) == str else None,axis  = 1 )


    data.Year = data.Year.astype(dtype = np.int32)
    data.Week = data.Week.astype(dtype = np.int32)

    stat_tables = {}

    scoring_data_table = data.apply(lambda x : scoring_table(x["Scoring_Data"],x["Year"],x["Week"]), 
                                     axis = 1, result_type = 'expand')

    stat_tables["Team Stats"] = data.apply(lambda x : ts_table(x["Home Team Stats"],x["Away Team Stats"],x["Year"],x["Week"],x["Home"],x["Away"]), 
                                     axis = 1, result_type = 'expand')
    
    stat_tables["Starters"] = data.apply(lambda x : starter_table(x["Home Starters"],x["Away Starters"],x["Year"],x["Week"],x["Home"],x["Away"]), 
                                     axis = 1, result_type = 'expand')
    for ps in ['Off Player Stats', 'Ret Player Stats','Kick Player Stats','Def Player Stats',\
       'Adv Pass Player Stats','Adv Rec Player Stats','Adv Rush Player Stats','Adv Def Player Stats']:
        stat_tables[ps] = data.apply(lambda x : ps_table(x["Home " + ps],x["Away " + ps],x["Year"],x["Week"],x["Home"],x["Away"]), 
                                     axis = 1, result_type = 'expand')
        stat_tables[ps].dropna(how='all',inplace=True)



    git = data.filter(items = ["Year","Week","Home","Home Score","Home Record", "Home Coach", "Home Url",\
                               "Away","Away Score","Away Record", "Away Coach", "Away Url",\
                                "Roof","Surface","DateTime","Stadium","Attendance","Weather",\
                                "Duration","Vegas Line", "Over/Under","Won Toss", "Play-By-Play", "Home Snaps", "Away Snaps"],axis = 1)
    git["Scoring Data"] = scoring_data_table
    git = pd.concat([git,scoring_data_table])

    with pd.ExcelWriter(file_name) as writer:
        git.to_excel(writer,index = False,sheet_name = "Game Info")
        for st in stat_tables:
            stat_tables[st].to_excel(writer, index = False, sheet_name = st)


if __name__ == "__main__":
    process_data("1970_2023_data.csv","1970_2023_boxscore_data.xlsx")

    



