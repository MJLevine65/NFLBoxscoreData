import pandas as pd
from bs4 import BeautifulSoup, Tag, ResultSet
from ..Parser import Parser


class ScoringDataParser(Parser):
    """Parser for scoring data from boxscore pages"""

    def parse(self, parser : BeautifulSoup, boxscore :str, **args) -> pd.DataFrame:
        """Parse scoring breakdown data from boxscore HTML.
        
        Args:
            parser: BeautifulSoup parser of boxscore page.
        
        Returns:
            DataFrame with scoring data.
        """
        scoring_data : list[dict[str]] = []
        scoring_table : Tag = parser.find('div', id="div_scoring", class_="table_container")
        scoring_info : ResultSet[Tag] = scoring_table.tbody.select("tr:not(.thead)")
        
        for row in scoring_info:
            score_dict = {'game_id' : boxscore}
            raw = list(row)[3].find_all("a")
            score_dict['players'] = " ".join([self.parse_player_id(i['href']) for i in raw])
            for stat in row:
                data_stat : str = stat.attrs['data-stat']
                if data_stat == "quarter" and not stat.text:
                    score_dict[data_stat] = scoring_data[-1][data_stat]
                else:
                    score_dict[data_stat] = stat.text
            scoring_data.append(score_dict)
        
        return pd.DataFrame(scoring_data)