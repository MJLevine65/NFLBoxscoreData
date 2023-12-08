from bs4 import BeautifulSoup, Comment
import pandas as pd
import random,requests,time, warnings
from tqdm import tqdm

t = time.time()

def sleep_fun():
    global t
    g = time.time() - t
    if g > 3:
        return
    else:
        r = random.randint(1,10)/10
        time.sleep((3.1-g)+r)
        t = time.time()

#comment input isn't a file
warnings.filterwarnings('ignore',message =\
"The input looks more like a filename than markup. You may want to open this file and pass the filehandle into Beautiful Soup." )


def get_boxscores(year_start: int, year_end: int, file_name: str):
    data = {'url' : [], 'year' : [], 'week' : []}
# Get boxscore urls
    if year_start < 1920 or year_end > 2023:
        raise Exception.valueError("Invalid Date Range")
    for year in range(year_start,year_end+1):
        year_str = str(year)
        r = requests.get("https://www.pro-football-reference.com/years/" + year_str + "/")
        sleep_fun()
        parser = BeautifulSoup(r.text,"html.parser")
        weeks = []
        for item in parser.find_all("a",href = True):
            if (year_str + "/week_") in item['href']:
                if item['href'] not in weeks:
                    weeks.append(item['href'])
        i = 1
        for week in weeks:
            r = requests.get("https://www.pro-football-reference.com" + week)
            sleep_fun()
            parser = BeautifulSoup(r.text,"html.parser")
            for item in parser.find_all("a",href = True):
                if ("/boxscores/") in item['href']:
                    if item['href'] not in data['url']:
                        data['url'].append(item['href'])
                        data['year'].append(year)
                        data['week'].append(i)
            i += 1
        df = pd.DataFrame(data)
        df.to_csv(file_name)

def parse_boxscores(data_file: str, file_name: str):
    data = pd.read_csv(data_file)
    bad_urls = {"boxscore" : [], "errors" : []}
    def process_url(url:str,year: int, week: int):

        def find_comment(comment_parsers,tag:str,idstr:str,classstr:str):
            for c in comment_parsers:
                sc = c.find(tag, id=idstr, class_=classstr)
                if sc != None:
                    return sc
            return None
        
        try:
            url = "https://www.pro-football-reference.com" + url
            print(url)
            r = requests.get(url)
            sleep_fun()
            parser = BeautifulSoup(r.text,"html.parser")
            comments = parser.find_all(string = lambda text : isinstance(text, Comment))
            comments = list(set(comments))
            
            #Only want the comments that contain tables
            for c in comments:
                try:
                    pd.read_html(c)
                except:
                    comments.remove(c)


            comment_parsers = [BeautifulSoup(comment,"html.parser") for comment in comments]

        except Exception as ex:
            e = "Url Parsing Error"
            print(url, e)
            print(ex)
            if len(bad_urls["boxscore"]) == 0 or bad_urls["boxscore"][-1] != url:
                bad_urls["boxscore"].append(url)
                bad_urls["errors"].append([e])
            else:
                bad_urls["errors"][-1].append(e)
            return {}

        # Get Data from Game Info Table
        game_info_dict = {}
        try:
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
        except Exception as ex:
            e = "Game Info Error"
            print(url, e)
            print(ex)
            if len(bad_urls["boxscore"]) == 0 or bad_urls["boxscore"][-1] != url:
                bad_urls["boxscore"].append(url)
                bad_urls["errors"].append([e])
            else:
                bad_urls["errors"][-1].append(e)
            return {}



        #Scoring Data
        scoring_data = {"Scoring_Data" : {}}
        try:
            scoring_info = parser.find('div', id="div_scoring", class_="table_container").tbody.select("tr:not(.thead)")
            for row in scoring_info:
                for stat in row:
                    if stat.attrs['data-stat'] not in scoring_data["Scoring_Data"]:
                        scoring_data["Scoring_Data"][stat.attrs['data-stat']] = [stat.text]
                    else:
                        scoring_data["Scoring_Data"][stat.attrs['data-stat']] += [scoring_data["Scoring_Data"][stat.attrs['data-stat']][-1]] \
                            if stat.text == "" else [stat.text]
        except Exception as ex:
            e = "Scoring Data Error"
            print(url, e)
            print(ex)
            if len(bad_urls["boxscore"]) == 0 or bad_urls["boxscore"][-1] != url:
                bad_urls["boxscore"].append(url)
                bad_urls["errors"].append([e])
            else:
                bad_urls["errors"][-1].append(e)

        # Get Data from Teams Stats Table
        team_stats_dict = {"Home Team Stats" : {}, "Away Team Stats" : {}}
        try:
            team_stats_info  = find_comment(comment_parsers,'div','div_team_stats','table_container').tbody.select("tr:not(.thead)")
            for stat in team_stats_info: #stat variable in this case applies to the whole row since each row is a stat
                stat = list(stat)
                if stat[0].text not in team_stats_dict["Home Team Stats"]:
                    team_stats_dict["Home Team Stats"][stat[0].text] = [stat[2].text]
                    team_stats_dict["Away Team Stats"][stat[0].text] = [stat[1].text]
                else:
                    team_stats_dict["Home Team Stats"][stat[0].text] += [stat[2].text]
                    team_stats_dict["Away Team Stats"][stat[0].text] += [stat[1].text]
        except Exception as ex:
            e = "Team Stats Error"
            print(url, e)
            print(ex)
            if len(bad_urls["boxscore"]) == 0 or bad_urls["boxscore"][-1] != url:
                bad_urls["boxscore"].append(url)
                bad_urls["errors"].append([e])
            else:
                bad_urls["errors"][-1].append(e)
            
        #player stats
        def get_player_stats(home:str,away:str,info):
            home_player_data = {}
            away_player_data = {}
            for item in info:
                item = list(item)
                if item[1].text == home:
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

        player_stats = {}
        try:
            #Get offensive player stats
            offense_info = parser.find('div', id="div_player_offense", class_="table_container").tbody.select("tr:not(.thead)")
            player_stats["Home Offensive Player Stats"], player_stats["Away Offensive Player Stats"] = get_player_stats(home,vis,offense_info)

            #Get defensive player stats
            defense_info = find_comment(comment_parsers,'div','div_player_defense','table_container').tbody.select("tr:not(.thead)")
            player_stats["Home Defense Player Stats"], player_stats["Away Defense Player Stats"] = get_player_stats(home,vis,defense_info)

            #Get return player stats
            returns_info = find_comment(comment_parsers,'div','div_returns','table_container').tbody.select("tr:not(.thead)")
            player_stats["Home Return Player Stats"], player_stats["Away Return Player Stats"] = get_player_stats(home,vis,returns_info)

            #Get kicking player stats
            kicking_info = find_comment(comment_parsers,'div','div_kicking','table_container').tbody.select("tr:not(.thead)")
            player_stats["Home Kicking Player Stats"], player_stats["Away Kicking Player Stats"] = get_player_stats(home,vis,kicking_info)

            ax = (lambda x: get_player_stats(home,vis,x.tbody.select("tr:not(.thead)")) if x != None else ({}, {}))
            #Advanced passing
            ap_info = find_comment(comment_parsers,'div','div_passing_advanced','table_container')
            player_stats["Home Advance Passing Player Stats"], player_stats["Away Advanced Passing Player Stats"] = ax(ap_info)

            #Advanced recieving
            ar_info = find_comment(comment_parsers,'div','div_receiving_advanced','table_container')
            player_stats["Home Advance Receving Player Stats"], player_stats["Away Advanced Receiving Player Stats"] = ax(ar_info)
            
            #Advanced rushing
            aru_info = find_comment(comment_parsers,'div','div_rushing_advanced','table_container')
            player_stats["Home Advance Rushing Player Stats"], player_stats["Away Advanced Rushing Player Stats"] = ax(aru_info)
            
            #Advanced defense
            ad_info = find_comment(comment_parsers,'div','div_defense_advanced','table_container')
            player_stats["Home Advance Defense Player Stats"], player_stats["Away Advanced Defense Player Stats"] = ax(ad_info)
        except Exception as ex:
            e = "Player Stats Error"
            print(url, e)
            print(ex)
            if len(bad_urls["boxscore"]) == 0 or bad_urls["boxscore"][-1] != url:
                bad_urls["boxscore"].append(url)
                bad_urls["errors"].append([e])
            else:
                bad_urls["errors"][-1].append(e)

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
            e = "Starters Error"
            print(url, e)
            print(ex)
            if len(bad_urls["boxscore"]) == 0 or bad_urls["boxscore"][-1] != url:
                bad_urls["boxscore"].append(url)
                bad_urls["errors"].append([e])
            else:
                bad_urls["errors"][-1].append(e)

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
            e = "Drives Error"
            print(url, e)
            print(ex)
            if len(bad_urls["boxscore"]) == 0 or bad_urls["boxscore"][-1] != url:
                bad_urls["boxscore"].append(url)
                bad_urls["errors"].append([e])
            else:
                bad_urls["errors"][-1].append(e)

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
            e = "Play-By-Play Error"
            print(url, e)
            print(ex)
            if len(bad_urls["boxscore"]) == 0 or bad_urls["boxscore"][-1] != url:
                bad_urls["boxscore"].append(url)
                bad_urls["errors"].append([e])
            else:
                bad_urls["errors"][-1].append(e)

        return {"Year" : year, "Week" : week, "Home" : home, "Away" : vis} | scoring_data | game_info_dict | team_stats_dict | player_stats | starters_dict | snaps | pbp   
    tqdm.pandas(desc='Progress')
    data.url = data.url.astype(str)
    new_data = data.progress_apply(lambda x: process_url(x.url, x.year,x.week), axis=1,result_type = 'expand')
    while True:
        try:
            new_data.to_csv(file_name,index = False)
            break
        except:
            print("close",file_name)
            input()
    while True:
        try:
            pd.DataFrame(bad_urls).to_csv(file_name[:-4] + "_bad_urls.csv",index = False)
            break
        except:
            print("close error file")
            input()











