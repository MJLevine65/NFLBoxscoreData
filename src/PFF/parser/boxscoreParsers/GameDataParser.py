from bs4 import BeautifulSoup, Tag
import pandas as pd
from ..Parser import Parser


class GameDataParser(Parser):
    """Parser for game data from boxscore pages"""


    def parse(self, parser : BeautifulSoup, comment_parsers : list[BeautifulSoup], boxscore : str, week : int , year : int, **args) -> pd.DataFrame:
        """Parse game data (teams, date, time, stadium, stats) from boxscore HTML.
        
        Args:
            parser: BeautifulSoup parser of boxscore page.
            comment_parsers: List of parsers for HTML comments.
            boxscore: Boxscore ID string.
            week: Game week number.
            year: Game year.
        
        Returns:
            DataFrame with processed game data.
        """
        game_data = { 'game_id' : self.parse_boxscore_id(boxscore), "year" : year, "week" : week }

        scorebox : Tag = parser.find("div", class_="scorebox")

        scorebox_teams : list[Tag] = [ tag for tag in scorebox.find_all("a", href=True) if "/teams/" in tag['href']]
        game_data["home"] = self.parse_team(list(scorebox_teams)[0]['href'])
        game_data["away"] = self.parse_team(list(scorebox_teams)[1]['href'])

        # Parse Date, Start Time, Stadium
        scorebox_meta : list[Tag] = list(list(scorebox.find_all("div", class_="scorebox_meta"))[0])
        game_data["date"] = scorebox_meta[1].text
        game_data["start_time"] = scorebox_meta[2].text.replace("Start Time: ", "")
        game_data["stadium"] = scorebox_meta[3].text.replace("Stadium: ", "")

        game_info : list[Tag] = self.find_comment(comment_parsers, tag='div', id_str='div_game_info', class_str='table_container').find_all("tr")
        for row in game_info[1:]:
            row = list(row)
            game_data[self.parse_stat(row[0].text)] = row[1].text

        dataframe : pd.DataFrame = self.process_boxscore_data(pd.DataFrame([game_data])) 

        return dataframe

    def process_boxscore_data(self, dataframe : pd.DataFrame) -> pd.DataFrame:
        """Process and clean game data DataFrame.
        
        Args:
            dataframe: Raw game data DataFrame.
        
        Returns:
            Processed DataFrame with normalized data types and formats.
        """
        if "weather" in dataframe.columns:
            weather_data : dict[str] = self.process_weather(dataframe["weather"].iloc[0]) 
            dataframe.drop(columns=["weather"], inplace=True)
        else:
            weather_data = {}

        dataframe["temprature"] = weather_data.get("temprature", None)
        dataframe["wind_speed"] = weather_data.get("wind_speed", None)
        dataframe["humidity"] = weather_data.get("humidity", None)
        dataframe["wind_chill"] = weather_data.get("wind_chill", None)

        dataframe["date"] = pd.to_datetime(dataframe["date"]).dt.date

        dataframe["duration"] = dataframe["duration"].apply(lambda x : int(x.split(":")[0]) * 60 + int(x.split(":")[1]) if type(x) == str else None)
        dataframe["attendance"] = dataframe["attendance"].apply(lambda x : int(x.replace(",", ""))) if 'attendance' in dataframe else pd.Series([None])

        return dataframe

    def process_weather(self, weather: str) -> dict[str]:
        """Parse weather string into structured weather data"""
        
        weather_data: dict[str] = {}
        for item in weather.split(','):
            if "degrees" in item:
                weather_data["temprature"] = int(item.split(" ")[0])
            elif "mph" in item:
                weather_data["wind_speed"] = int(item.split(" ")[2])
            elif "humidity" in item:
                weather_data["humidity"] = int(item.split(" ")[3][:-1])
            elif "no wind" in item:
                weather_data["wind_speed"] = 0
            elif "wind chill" in item:
                weather_data["wind_chill"] = int(item.split(" ")[3])
            else:
                raise ValueError(f"Unrecognized weather item: {item}")
            
        return weather_data