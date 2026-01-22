import pandas as pd

from bs4 import BeautifulSoup,Tag, ResultSet

#Scoring Data
def parse_scoring_data(parser : BeautifulSoup) -> pd.DataFrame:
    scoring_data : list[dict[str]] = []
    scoring_table : Tag = parser.find('div', id="div_scoring", class_="table_container")
    scoring_info : ResultSet[Tag] = scoring_table.tbody.select("tr:not(.thead)")
    for row in scoring_info:
        score_dict = {}
        for stat in row:
            data_stat : str = stat.attrs['data-stat']
            if data_stat == "quarter" and not stat.text:
                score_dict[data_stat] = scoring_data[-1][data_stat]
            else:
                score_dict[data_stat] = stat.text
        scoring_data.append(score_dict)
    return pd.DataFrame(scoring_data)