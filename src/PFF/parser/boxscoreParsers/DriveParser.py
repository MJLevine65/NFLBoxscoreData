import pandas as pd
from bs4 import BeautifulSoup
from ..Parser import Parser


class DriveParser(Parser):
    """Parser for drive data from boxscore pages"""

    def parse(self, comment_parsers : list[BeautifulSoup], boxscore : str, home : str, away : str, **args) -> pd.DataFrame:
        """Parse drive data for home and away teams from boxscore HTML comments.
        
        Args:
            comment_parsers: List of parsers for HTML comments.
            boxscore: Boxscore ID string.
            home: Home team abbreviation.
            away: Away team abbreviation.
        
        Returns:
            DataFrame with processed drive data or None if data unavailable.
        """
        drives_data : list[dict[str]] = []

        home_drives_table = self.find_comment(comment_parsers, 'div', 'div_home_drives', 'table_container')
        home_drives_info = home_drives_table.tbody.select("tr:not(.thead)") if home_drives_table != None else None

        away_drives_table = self.find_comment(comment_parsers, 'div', 'div_vis_drives', 'table_container')
        away_drives_info = away_drives_table.tbody.select("tr:not(.thead)") if away_drives_table != None else None

        if home_drives_info == None:
            return None

        for drive in home_drives_info:
            drive_data = {"game_id" : boxscore, "team" : home}
            drive_data.update({stat.attrs['data-stat'] : stat.text for stat in drive})
            drives_data.append(drive_data)

        for drive in away_drives_info:
            drive_data = {"game_id" : boxscore, "team" : away}
            drive_data.update({stat.attrs['data-stat'] : stat.text for stat in drive})
            drives_data.append(drive_data)

        return self.process_drives_data(pd.DataFrame(drives_data))
    
    def process_drives_data(self, dataframe : pd.DataFrame) -> pd.DataFrame:
        """Process and normalize drive data.
        
        Args:
            dataframe: Raw drive data DataFrame.
        
        Returns:
            Processed DataFrame with normalized column names and data formats.
        """
        dataframe.rename(columns={
            "time_start": "start_time", 
            "start_at": "start_loc",
            "play_count_tip": "plays", 
            "time_total": "time", 
            "end_event": "result"
        }, inplace=True)
        
        for i, row in dataframe.iterrows():
            dataframe.at[i, "start_time"] = "00:" + row['start_time']
            dataframe.at[i, "time"] = "00:" + row['time']
            dataframe.at[i, "result"] = row['result'].replace(",", "")

        return dataframe