from bs4 import BeautifulSoup, ResultSet, Tag
import pandas as pd
import re

from ..Parser import Parser
from ....util.regexUtil import regexUtil

class PbpParser(Parser):
    """Parser for play-by-play data from boxscore pages"""

    def parse(self, comment_parsers : list[BeautifulSoup], boxscore : str, **args) -> pd.DataFrame | None:
        """Parse play-by-play data from HTML comments.
        
        Args:
            comment_parsers: List of parsers for HTML comments.
            boxscore: Boxscore ID string.
        
        Returns:
            DataFrame with processed play-by-play data or None if unavailable.
        """

        pbp_data : list[dict[str]] = []
        pbp_table = self.find_comment(comment_parsers, 'div', 'div_pbp', 'table_container')
        pbp_info : ResultSet[Tag] = pbp_table.tbody.select("tr:not(.thead)") if pbp_table != None else None

        if pbp_info == None:
            return None

        play_count : int = 0
        for play in list(pbp_info)[1:]:
            play_count += 1
            play_id : str = boxscore + str(play_count)
            play_data = {"play_id" : play_id, "game_id" : boxscore}
            play_data.update({stat.attrs['data-stat'] : stat.text for stat in play})
            raw = list(play)[7].find_all("a")
            play_data['players'] = " ".join([self.parse_player_id(i['href']) for i in raw[1:]])
            play_data['detail'] = play_data['detail'].replace(',', '')
            play_data['detail'] = play_data['detail'].replace('.', '')
            if play_data['quarter'] != '':
                pbp_data.append(play_data)

        dataframe : pd.DataFrame = pd.DataFrame(pbp_data)
        dataframe.rename(columns={
            'qtr_time_remain': 'time', 
            'pbp_score_hm': 'home_score', 
            'pbp_score_aw': 'away_score', 
            'detail': 'description',
            'exp_pts_before': 'epb', 
            'exp_pts_after': 'epa'
        }, inplace=True)
        dataframe.replace('', None, inplace=True)

        return dataframe
    
# def process_pbp_data(data : list[dict[str]]) -> pd.DataFrame:
#    dataframe : pd.DataFrame = pd.DataFrame(data)

#    maps = get_maps()
#    for i, row in dataframe.iterrows():
#          text = clean_text(row['detail'])
#          for key, value in maps.items():
#             res = check_map(value, text)
#             if res != None:
#                break
#          if "Timeout" in text or "coin toss" in text or "lateral" in text or text.count("fumbles") > 1 or "-128" in text or "sacked by." in text or res != None:
#            continue
#          else:
#             print(text)

# def clean_text(text:str) -> str:
#    text = text.replace(", touchdown, touchdown", ", touchdown")
#    text = text.replace("sacked by and", "sacked by")
#    text = text.strip(".")
#    return text

# def check_map(map: dict[list[re.Pattern]], text: str) -> str | None:
#    for key, value in map.items():
#       for re in value:
#          if re.search(text):
#             return key
#    return None

# def get_maps() -> dict[dict[list[re.Pattern]]]:
#    return {
#             "pass" : get_pass_map(),
#             "rush" : get_run_map(),
#             "punt" : get_punt_map(),
#             "kick" : get_kickoff_map(),
#             "fg" : get_fg_map(),
#             "xp" : get_xp_map(),
#             "2p" : get_2p_map(),
#             "penalty" : get_penalty_map()
#          }

# def get_pass_map() -> dict[list[re.Pattern]]:
#    p = regexUtil.player
#    gain = regexUtil.yard_gain
#    dir = regexUtil.pass_dir
#    pdef = regexUtil.pass_defended
#    fumble = regexUtil.fumble
#    force_fumble = regexUtil.force_fumble
#    tackle = regexUtil.tackle
#    interception = regexUtil.interception
#    returned = regexUtil.returned
#    recover = regexUtil.recover

#    return {
#       "pass_icmp" : [
#          re.compile(f"^{p} pass incomplete( {dir})?( intended for {p})?( {pdef})?( {pdef})?$")
#       ],
#       "pass_cmp" : [
#          re.compile(f"^{p} pass complete( {dir})? to {p} for {gain}( {tackle})?$"),
#       ],
#       "pass_cmp_td" : [
#          re.compile(f"^{p} pass complete( {dir})? to {p} for {gain}, touchdown$")
#       ],
#       "pass_cmp_fmb" : [
#          re.compile(f"^{p} pass complete( {dir})? to {p} for {gain}( {tackle})?. ({fumble}|{force_fumble})( and {returned})?$")
#       ],
#       "pass_cmp_fmb_td" : [
#          re.compile(f"^{p} pass complete( {dir})? to {p} for {gain}( {tackle})?. ({fumble}|{force_fumble})( and {returned})?, touchdown$")
#       ],
#       "pass_int" : [
#          re.compile(f"^{p} pass( {dir})?( {pdef})?( intended for {p})? {interception}$")
#       ],
#       "pass_int_td" : [
#          re.compile(f"^{p} pass( {dir})?( {pdef})?( intended for {p})? {interception}, touchdown$")
#       ],
#       "pass_int_fmb" : [
#          re.compile(f"^{p} pass( {dir})?( {pdef})?( intended for {p})? {interception}. ({force_fumble}|{fumble})$")
#       ],
#       "spike" : [
#          re.compile(f"^{p} spiked the ball$")
#       ],
#       "sack" : [
#          re.compile(f"^{p} sacked by {p}( and {p})? for {gain}$"),
#          re.compile(f"^{p} sacked by {p} for {gain} and {p} for {gain}$"),
#          re.compile(f"^{p} sacked by$"),

#       ],
#       "sack_fumble": [
#          re.compile(f"^{p} sacked by {p} for {gain}( and {p} for {gain})?. ({force_fumble}|{fumble})( and {returned})?$"),
#       ],
#       "sack_safety": [
#          re.compile(f"^{p} sacked by {p} for {gain}( and {p} for {gain})?, safety$"),
#       ],
#       "sack_fumble_safety": [
#          re.compile(f"^{p} sacked by {p} for {gain}. ({force_fumble}|{fumble})( {tackle}), safety$"),
#       ],
#       "sack_fumble_td" : [
#          re.compile(f"^{p} sacked by {p} for {gain}. ({force_fumble}|{fumble})( and {returned})?, touchdown$")
#       ],
#       "aborted_snap" : [
#          re.compile(f"^{p} aborted snap, {recover}( {tackle})?")
#       ]
#    }

# def get_run_map() -> dict[list[re.Pattern]]:
#    p = regexUtil.player
#    gain = regexUtil.yard_gain
#    dir = regexUtil.rush_dir
#    fumble = regexUtil.fumble
#    force_fumble = regexUtil.force_fumble
#    tackle = regexUtil.tackle
#    returned = regexUtil.returned
#    oob = regexUtil.oob
#    pos = regexUtil.pos

#    return {
#       "rush" : [
#          re.compile(f"^{p}( {dir})? for {gain}( {tackle}|, {oob})?$")
#       ],
#       "rush_td" : [
#          re.compile(f"^{p}( {dir})? for {gain}, touchdown$")
#       ],
#       "rush_fumble" : [
#          re.compile(f"^{p}( {dir})? for {gain}( {tackle})?. ({fumble}|{force_fumble})( and {returned})?$"),
#          re.compile(f"^{p} fumbles( {oob}|, recovered by {p} at {pos})"),
#       ],
#       "rush_fumble_td" : [
#          re.compile(f"^{p}( {dir})? for {gain}( {tackle})?. ({fumble}|{force_fumble})( and {returned})?, touchdown$")
#       ],
#       "rush_safety" : [
#          re.compile(f"^{p}( {dir})? for {gain}( {tackle}), safety$")
#       ],
#       "kneel" : [
#          re.compile(f"^{p} kneels for {gain}$")
#       ],
#  }

# def get_punt_map() -> dict[list[re.Pattern]]:
#    p = regexUtil.player
#    gain = regexUtil.yard_gain
#    pos = regexUtil.pos
#    dir = regexUtil.rush_dir
#    fumble = regexUtil.fumble
#    force_fumble = regexUtil.force_fumble
#    tackle = regexUtil.tackle
#    returned = regexUtil.returned
#    oob = regexUtil.oob
#    muffed = regexUtil.muffed
#    recover = regexUtil.recover
#    kick_yards = regexUtil.kick_yards

#    return {
#       "punt_oob" : [
#          re.compile(f"^{p} punts {kick_yards}( {oob})?$")
#       ],
#       "punt_fair_catch" : [
#          re.compile(f"^{p} punts {kick_yards}, fair catch by {p} at {pos}$")
#       ],
#       "punt_touchback" : [
#          re.compile(f"^{p} punts {kick_yards}, touchback$")
#       ],
#       "punt_downed" : [
#          re.compile(f"^{p} punts {kick_yards} downed by {p}$")
#       ],
#       "punt_ret" : [
#          re.compile(f"^{p} punts {kick_yards}, {returned}( {tackle})?$"),
#       ],
#       "punt_ret_td" : [
#          re.compile(f"^{p} punts {kick_yards}, {returned}, touchdown$")
#       ],
#       "punt_ret_fumble" : [
#          re.compile(f"^{p} punts {kick_yards}, {returned}( {tackle})?. ({force_fumble}|{fumble})(, and {returned})?$")
#       ],
#       "punt_ret_fumble_td" : [
#          re.compile(f"^{p} punts {kick_yards}, {returned}( {tackle})?. ({force_fumble}|{fumble})(, and {returned})?, touchdown$")
#       ],
#       "punt_muffed" : [
#          re.compile(f"^{p} punts {kick_yards}, {muffed}(, {recover})?(, {returned})?$"),
#       ],
#       "punt_blocked" : [
#          re.compile(f"^{p} punts blocked by {p}(, {recover})( {tackle})?$"),
#       ],
#       "punt_blocked_safety" : [
#          re.compile(f"^{p} punts blocked by {p}(, {recover})( {tackle})?$"),
#       ],
#       "punt_blocked_td" : [
#          re.compile(f"^{p} punts blocked by {p}, {recover}, touchdown$"),
#       ]
#    }

# def get_kickoff_map() -> dict[list[re.Pattern]]:
#    p = regexUtil.player
#    gain = regexUtil.yard_gain
#    fumble = regexUtil.fumble
#    force_fumble = regexUtil.force_fumble
#    tackle = regexUtil.tackle
#    returned = regexUtil.returned
#    oob = regexUtil.oob
#    muffed = regexUtil.muffed
#    recover = regexUtil.recover
#    kick_yards = regexUtil.kick_yards
#    kick_type = regexUtil.kick_type

#    return {
#       "kickoff_touchback" : [
#          re.compile(f"^{p} kicks {kick_type} {kick_yards}, touchback$"),
#          re.compile(f"^{p} kicks {kick_type} no gain, touchback$")
#       ],
#       "kickoff_ret" : [
#          re.compile(f"^{p} kicks {kick_type} {kick_yards}(, {returned})?$"),
#          re.compile(f"^{p} kicks {kick_type} {kick_yards}, {recover}$"),

#       ],
#       "kickoff_ret_td" : [
#          re.compile(f"^{p} kicks {kick_type} {kick_yards}, {returned}, touchdown$")
#       ],
#       "kickoff_oob" : [
#          re.compile(f"^{p} kicks {kick_type} {kick_yards},( {oob})?$")
#       ],
#       "kickoff_ret_fumble" : [
#          re.compile(f"^{p} kicks {kick_type} {kick_yards}, {returned}. ({force_fumble}|{fumble})( and {returned})?$")
#       ],
#       "kickoff_ret_fumble_td" : [
#          re.compile(f"^{p} kicks {kick_type} {kick_yards}, {returned}. {force_fumble}(, and {returned}), touchdown$"),
#       ],
#       "kickoff_muffed" : [
#          re.compile(f"^{p} kicks {kick_type} {kick_yards}, {muffed}(, {recover})?( {returned})?$")
#       ],
#       "kickoff_muffed_td" : [
#          re.compile(f"^{p} kicks {kick_type} {kick_yards}, {muffed}(, {recover})?( {returned})?, touchdown$")
#       ]
#    }

# def get_fg_map() -> dict[list[re.Pattern]]:
#    p = regexUtil.player
#    kick_yards = regexUtil.kick_yards
#    kick_miss = regexUtil.kick_miss
#    blocked = regexUtil.blocked
#    returned = regexUtil.returned

#    return {
#       "fg_good" : [
#          re.compile(f"^{p} {kick_yards} field goal good$")
#       ],
#       "fg_miss" : [
#          re.compile(f"^{p} {kick_yards} field goal no good( {kick_miss})?$")
#       ],
#       "fg_blocked" : [
#          re.compile(f"^{p} {kick_yards} field goal no good {blocked}$")
#       ],
#       "fg_blocked_td" : [
#          re.compile(f"^{p} {kick_yards} field goal no good {blocked}, {returned}, touchdown$")
#       ],
#       "fg_returned": [
#          re.compile(f"^{p} {kick_yards} field goal no good {returned}$")
#       ],
#       "fg_returned_td" : [
#          re.compile(f"^{p} {kick_yards} field goal no good {returned}, touchdown$")
#       ],
# }

# def get_xp_map() -> dict[list[re.Pattern]]:
#    p = regexUtil.player
#    kick_miss = regexUtil.kick_miss
#    blocked = regexUtil.blocked
#    returned = regexUtil.returned

#    return {
#       "xp_good" : [
#          re.compile(f"^{p} kicks extra point (good)?$")
#       ],
#       "xp_miss" : [
#          re.compile(f"^{p} kicks extra point no good( {kick_miss})?$")
#       ],
#       "xp_blocked" : [
#          re.compile(f"^{p} kicks extra point {blocked}$")
#       ],
#       "xp_blocked_conv" : [
#          re.compile(f"^{p} kicks extra point {blocked}, {returned} for defensive conversion$")
#       ]
# }

# def get_penalty_map() -> dict[list[re.Pattern]]:
#    penalty = regexUtil.penalty
#    gain = regexUtil.yard_gain
#    p = regexUtil.player
#    t = regexUtil.team
#    return {
#       "penalty" : [
#         re.compile(rf"Penalty on ({p}|{t}): {penalty}(, {gain})?( \(no play\))?$"),
#         re.compile(rf"Penalty on ({p}|{t}): {penalty} \(Declined\) $"),
#         re.compile(rf"Penalty on ({p}|{t}): {penalty} \(Offsetting\)( .)? Penalty on ({p}|{t}): {penalty} \(Offsetting\) (\(no play\))?$"),
#         re.compile(rf"Penalty on ({p}|{t}): {penalty} \(Declined\)( .)? Penalty on ({p}|{t}): {penalty} (\(no play\))?$"),
#         re.compile(rf"Penalty on ({p}|{t}): {penalty} ( .)? Penalty on ({p}|{t}): {penalty} \(Declined\)( \(no play\))?$")
#       ]
#    }

# def get_2p_map() -> dict[list[re.Pattern]]:
#    return {
#       "2p_conv" : [
#          re.compile(rf"Two Point Attempt: .+ conversion succeeds$")
#       ],
#       "2p_fail" : [
#          re.compile(rf"Two Point Attempt: .+ conversion fails.+$"),
#          re.compile(rf"Two Point Attempt: .+$")

#       ]
#    }