import pandas as pd
from bs4 import BeautifulSoup, Tag, ResultSet
from ..Parser import Parser


class WeekParser(Parser):
    """Parser for week information"""

    def parse_potw(self, parser : BeautifulSoup, year : int, week : int, **args) -> pd.DataFrame | None:
        """Parse snap counts and starter information for both teams.
        
        Args:
            comment_parsers: List of parsers for HTML comments.
            boxscore: Boxscore ID string.
            home: Home team abbreviation.
            away: Away team abbreviation.
        
        Returns:
            DataFrame with processed snap data or None if unavailable.
        """
        potw_data : list[dict[str]] = []

        potw_table = parser.find('div', id='div_potw', class_='table_container')
        potw_info : ResultSet[Tag] = potw_table.tbody.select("tr:not(.thead)")

        if potw_table == None:
            return None
        
        for row in potw_info:
            items = list(row)
            for item in items[1:]:
                potw_data.append({
                    "id" : f"{year}_{week}_{item.attrs['data-stat'][0]}",
                    "year" : year,
                    "week" : week,
                    "conference" : items[0].text,
                    "type" : item.attrs['data-stat'],
                    "player" : self.parse_player_id(item.find_all("a")[0].attrs['href'])
                })

        potw_table : pd.DataFrame = pd.DataFrame(potw_data)
        return potw_table