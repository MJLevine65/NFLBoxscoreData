from bs4 import BeautifulSoup, Comment
import pandas as pd
import random,requests,time, warnings,os
from tqdm import tqdm


def sleep_fun(current_time : float) -> float:
    # PFR Website only accepts 20 requests a minute
    # This function delays requests to 1 every 3 seconds
    difference = time.time() - current_time
    if difference > 3:
        return time.time()
    else:
        r = random.randint(1,10)/10
        time.sleep((3.1-difference)+r)
        return time.time()

def get_boxscores(year_start: int, year_end: int, file_name: str):
    """
    Gets the boxscore url for each game in the range year_start to year_end
    Saves boxscores to file_name.csv
    """
    boxscores = pd.DataFrame(columns = ['url','year','week']) 
    if year_start < 1920 or year_end > 2023:
        raise Exception.valueError("Invalid Date Range")
    current_time = time.time()

    #Iterate over years, get week urls for each week in each year
    for year in range(year_start,year_end+1):
        r = requests.get("https://www.pro-football-reference.com/years/" + str(year) + "/")
        current_time = sleep_fun(current_time)
        parser = BeautifulSoup(r.text,"html.parser")
        weeks = []
        for item in parser.find_all("a",href = True):
            if ((str(year) + "/week_") in item['href']) and (item['href'] not in weeks):
                weeks.append("https://www.pro-football-reference.com" + item['href'])
        
        #Iterate over weeks, get boxscore url for each game in each week
        for week,week_url in enumerate(weeks):
            r = requests.get(week_url)
            current_time = sleep_fun(current_time)
            parser = BeautifulSoup(r.text,"html.parser")
            for item in parser.find_all("a",href = True):
                if (("/boxscores/") in item['href']) and (item['href'] not in boxscores['url']):
                    boxscores = \
                    boxscores._append({'url':item['href'],'year':year, 'week': week+1},ignore_index = True)
        boxscores.to_csv("BoxscoreData/" + file_name + ".csv", index = False )

def parse_boxscores(data_file: str, file_name: str):
    def find_comment(comment_parsers,tag:str,idstr:str,classstr:str):
        """
        comment_parsers: List of BS4 parsers of each commented part of the html
          file to find the one that matches the criteria defined by the rest of the inputs
        tag: HTML tag of comment parser that is being searched for
        idstr: id of comment pareser that is being searched for
        classstr: class of comment parser that is being searched for
        """
        for comment in comment_parsers:
            sc = comment.find(tag, id=idstr, class_=classstr)
            if sc != None:
                return sc
        return None
    
    def error_fun(err:str,url:str,ex:Exception):
            #Whenever an error occurs record the url and error
            print(url, err)
            print(ex)
            bad_urls = bad_urls._append({'boxscore':url,'errors':ex},ignore_index = True)

    def get_game_info(parser, comment_parsers):
        game_info_dict = {}
        game_info = find_comment(comment_parsers,'div','div_game_info','table_container').find_all("tr")
        for row in game_info[1:]:
            row = list(row)
            game_info_dict[row[0].text.replace("*","")] = row[1].text

        score_box = parser.find("div",class_="scorebox")

        coaches = score_box.find_all("div",class_="datapoint")
        game_info_dict["Home Coach"] = list(list(coaches)[0])[2].text
        game_info_dict["Away Coach"] = list(list(coaches)[1])[2].text

        sc = list(list(score_box.find_all("div",class_="scorebox_meta"))[0])
        
        game_info_dict["Date"] = sc[1].text
        game_info_dict["Start time"] = sc[2].text.replace("Start Time: ","")
        game_info_dict["Stadium"] = sc[3].text.replace("Stadium: ","")

        team_urls = [item['href'] for item in score_box.find_all(href=True) if item['href'][:7] == "/teams/"]
        home,vis = team_urls[1][7:10].upper(),team_urls[0][7:10].upper()
        game_info_dict["Away Url"], game_info_dict["Home Url"] = team_urls[:2]

        scores = list(score_box.find_all("div",class_ = "score"))
        game_info_dict["Away Score"], game_info_dict["Home Score"] = scores[0].text,scores[1].text

        records = score_box.find_all("div",class_ = "scores")
        game_info_dict["Away Record"], game_info_dict["Home Record"] = [item.nextSibling.text for item in records][:2]
        return game_info_dict, home, vis
    
    def get_scoring_data(parser):
        scoring_data = {"Scoring_Data" : {}}
        scoring_info = parser.find('div', id="div_scoring", class_="table_container").tbody.select("tr:not(.thead)")
        for row in scoring_info:
            for stat in row:
                if stat.attrs['data-stat'] not in scoring_data["Scoring_Data"]:
                    scoring_data["Scoring_Data"][stat.attrs['data-stat']] = [stat.text]
                else:
                    scoring_data["Scoring_Data"][stat.attrs['data-stat']] += [scoring_data["Scoring_Data"][stat.attrs['data-stat']][-1]] \
                        if stat.text == "" else [stat.text]
        return scoring_data

    def get_team_stats(comment_parsers):
        team_stats_dict = {"Home Team Stats" : {}, "Away Team Stats" : {}}
        team_stats_info  = find_comment(comment_parsers,'div','div_team_stats','table_container').tbody.select("tr:not(.thead)")
        for stat in team_stats_info: #stat variable in this case applies to the whole row since each row is a stat
            stat = list(stat)
            if stat[0].text not in team_stats_dict["Home Team Stats"]:
                team_stats_dict["Home Team Stats"][stat[0].text] = [stat[2].text]
                team_stats_dict["Away Team Stats"][stat[0].text] = [stat[1].text]
            else:
                team_stats_dict["Home Team Stats"][stat[0].text] += [stat[2].text]
                team_stats_dict["Away Team Stats"][stat[0].text] += [stat[1].text]

    def get_player_stats(home:str,away:str,info):
            home_player_data = {}
            away_player_data = {}
            a = list(list(info)[0])[1].text
            for item in info:
                item = list(item)
                if item[1].text != a:
                    for stat in item:
                        if stat.attrs['data-stat'] not in home_player_data:
                            home_player_data[stat.attrs['data-stat']] = ["0"] if stat.text == "" else [stat.text]
                        else:
                            home_player_data[stat.attrs['data-stat']] += ["0"] if stat.text == "" else [stat.text]
                else:
                    for stat in item:
                        if stat.attrs['data-stat'] not in away_player_data:
                            away_player_data[stat.attrs['data-stat']] = ["0"] if stat.text == "" else [stat.text]
                        else:
                            away_player_data[stat.attrs['data-stat']] += ["0"] if stat.text == "" else [stat.text]
            return home_player_data,away_player_data

    def process_url(url:str,year: int, week: int):


        r = requests.get("https://www.pro-football-reference.com" + url)
        current_time = sleep_fun(current_time)
        parser = BeautifulSoup(r.text,"html.parser")

        #Gather all html comments
        comments = parser.find_all(string = lambda text : isinstance(text, Comment))
        comments = list(set(comments))

        #Only want the comments that contain tables
        for c in comments:
            try:
                pd.read_html(c)
            except:
                comments.remove(c)
        
        #Convert all the commented tables into parsers
        comment_parsers = [BeautifulSoup(comment,"html.parser") for comment in comments]

        # Get Data from Game Info Table
        try:
            game_info_dict, home, vis = get_game_info(parser, comment_parsers)

        except Exception as ex:
            error_fun("Game Info Error",url,ex)
            return {}

        #Scoring Data 
        try:
            scoring_data = get_scoring_data(parser)
        except Exception as ex:
            error_fun("Scoring Data Error",url,ex)

        # Get Data from Teams Stats Table
        try:
            team_stats_dict = get_team_stats(comment_parsers)
        except Exception as ex:
            error_fun("Team Stats Error",url,ex)
            
        #player stats
        player_stats = {}
        try:
            ax = (lambda x: get_player_stats(home,vis,x.tbody.select("tr:not(.thead)")) if x != None else ({}, {}))
            #Get offensive player stats
            offense_info = parser.find('div', id="div_player_offense", class_="table_container")
            player_stats["Home Off Player Stats"], player_stats["Away Off Player Stats"] = ax(offense_info)

            for id,name in [["player_defnese","Def"],["returns","Ret"],["kicking","Kick"],["passing_advanced","Adv Pass"],\
            ["receiving_advanced","Adv Rec"],["rushing_advanced","Adv Rush"],["defense_advanced","Adv Def"]]:
                info = find_comment(comment_parsers,'div','div_' + id,'table_container')
                player_stats["Home " + name + " Player Stats"], player_stats["Away " + name " Player Stats"] = ax(info)

            # #Get defensive player stats
            # defense_info = find_comment(comment_parsers,'div','div_player_defense','table_container')
            # player_stats["Home Def Player Stats"], player_stats["Away Def Player Stats"] = ax(defense_info)

            # #Get return player stats
            # returns_info = find_comment(comment_parsers,'div','div_returns','table_container')
            # player_stats["Home Ret Player Stats"], player_stats["Away Ret Player Stats"] = ax(returns_info)

            # #Get kicking player stats
            # kicking_info = find_comment(comment_parsers,'div','div_kicking','table_container')
            # player_stats["Home Kick Player Stats"], player_stats["Away Kick Player Stats"] = ax(kicking_info)
            # #Advanced passing
            # ap_info = find_comment(comment_parsers,'div','div_passing_advanced','table_container')
            # player_stats["Home Adv Pass Player Stats"], player_stats["Away Adv Pass Player Stats"] = ax(ap_info)

            # #Advanced recieving
            # ar_info = find_comment(comment_parsers,'div','div_receiving_advanced','table_container')
            # player_stats["Home Adv Rec Player Stats"], player_stats["Away Adv Rec Player Stats"] = ax(ar_info)
            
            # #Advanced rushing
            # aru_info = find_comment(comment_parsers,'div','div_rushing_advanced','table_container')
            # player_stats["Home Adv Rush Player Stats"], player_stats["Away Adv Rush Player Stats"] = ax(aru_info)
            
            # #Advanced defense
            # ad_info = find_comment(comment_parsers,'div','div_defense_advanced','table_container')
            # player_stats["Home Adv Def Player Stats"], player_stats["Away Adv Def Player Stats"] = ax(ad_info)
        except Exception as ex:
            error_fun("Player Stats Error",url,ex)

        starters_dict = {"Home Starters" : {}, "Away Starters" : {}}
        #Starters
        try:
            home_starter_info = find_comment(comment_parsers,'div','div_home_starters','table_container').tbody.select("tr:not(.thead)")
            for item in home_starter_info:
                item = list(item)
                starters_dict["Home Starters"][item[1].text] = [item[0].text] if item[1].text not in starters_dict["Home Starters"] else \
                                                                starters_dict["Home Starters"][item[1].text] + [item[0].text]
            away_starter_info = find_comment(comment_parsers,'div','div_vis_starters','table_container').tbody.select("tr:not(.thead)")
            for item in away_starter_info:
                item = list(item)
                starters_dict["Away Starters"][item[1].text] = [item[0].text] if item[1].text not in starters_dict["Away Starters"] else \
                                                                starters_dict["Away Starters"][item[1].text] + [item[0].text]
        except Exception as ex:
            error_fun("Starters Error",url,ex)

        snaps = {"Home Snaps" : {}, "Away Snaps" : {}}
        try:
            #Get Snaps Data
            home_snap_info = find_comment(comment_parsers, 'div', 'div_home_snap_counts','table_container')
            away_snap_info = find_comment(comment_parsers, 'div', 'div_vis_snap_counts','table_container')
            if home_snap_info != None and away_snap_info != None:
                home_snap_info,away_snap_info = home_snap_info.tbody.select("tr:not(.thead)"), away_snap_info.tbody.select("tr:not(.thead)")
                for item in home_snap_info:
                    item = list(item)
                    snaps["Home Snaps"][item[0].text] = {"Off" : (item[2].text,item[3].text), "Def" : (item[4].text,item[5].text), "ST" : (item[6].text,item[7].text)}
                for item in away_snap_info:
                    item = list(item)
                    snaps["Away Snaps"][item[0].text] = {"Off" : (item[2].text,item[3].text), "Def" : (item[4].text,item[5].text), "ST" : (item[6].text,item[7].text)}
        except Exception as ex:
            e = "Snaps Error"
            print(url, e)
            print(ex)
            if len(bad_urls["boxscore"]) == 0 or bad_urls["boxscore"][-1] != url:
                bad_urls["boxscore"].append(url)
                bad_urls["errors"].append([e])
            else:
                bad_urls["errors"][-1].append(e)
        #Get drives data
        drives = {"Home Drives" : {}, "Away Drives" : {}}
        try:
            home_drives_info = find_comment(comment_parsers, 'div','div_home_drives','table_container')
            away_drives_info = find_comment(comment_parsers, 'div','div_vis_drives','table_container')
            
            if home_drives_info != None and away_drives_info != None:
                home_drives_info,away_drives_info = home_drives_info.tbody.select("tr:not(.thead)"), away_drives_info.tbody.select("tr:not(.thead)")
                for row in home_drives_info:
                    row = list(row)
                    for stat in row:
                        drives["Home Drives"][stat.attrs['data-stat']] = [stat.text] if stat.attrs['data-stat'] not in drives["Home Drives"] else \
                            drives["Home Drives"][stat.attrs['data-stat']] + [stat.text]
                for row in away_drives_info:
                    row = list(row)
                    for stat in row:
                        drives["Away Drives"][stat.attrs['data-stat']] = [stat.text] if stat.attrs['data-stat'] not in drives["Away Drives"] else \
                            drives["Away Drives"][stat.attrs['data-stat']] + [stat.text]
        except Exception as ex:
            error_fun("Drives Error",url,ex)

        #Get Play-By-Play Data
        pbp = {"Play-By-Play" : {}}
        try:
            pbp_info = find_comment(comment_parsers, 'div','div_pbp','table_container')
            if pbp_info != None:
                pbp_info = pbp_info.tbody.select("tr:not(.thead)")
                for row in pbp_info:
                    row = list(row)
                    for stat in row:
                        pbp["Play-By-Play"][stat.attrs['data-stat']] = [stat.text] if stat.attrs['data-stat'] not in pbp["Play-By-Play"] else \
                            pbp["Play-By-Play"][stat.attrs['data-stat']] + [stat.text]
        except Exception as ex:
            error_fun("Play-By-Play Error",url,ex)

        return {"Year" : year, "Week" : week, "Home" : home, "Away" : vis} | scoring_data | game_info_dict | team_stats_dict | player_stats | starters_dict | snaps | pbp   
    
    boxscores = pd.read_csv(data_file)
    bad_urls = pd.DataFrame(columns = ["boxscore","errors"])
    tqdm.pandas(desc='Progress')
    boxscore_data = boxscores.progress_apply(lambda x: process_url(x.url, x.year,x.week), axis=1,result_type = 'expand')

    while True:
        try:
            boxscore_data.to_csv(file_name,index = False)
            break
        except Exception as ex:
            print(ex,file_name)
            input()
    while True:
        try:
            pd.DataFrame(bad_urls).to_csv(file_name[:-4] + "_bad_urls.csv",index = False)
            break
        except Exception as ex:
            print(ex)
            input()

if __name__ == "__main__":
    warnings.filterwarnings('ignore',message =\
"The input looks more like a filename than markup. You may want to open this file\
      and pass the filehandle into Beautiful Soup." )
    #get_boxscores(2023,2023,"2023_boxscores")
    parse_boxscores













