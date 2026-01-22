import re
from ..model.Penalty import Penalty

class regexUtil:
    player: str = "(([A-z.\-']+) ([A-z.\-']+)( [A-z.\-']+)?)"
    yards: str = rf"(-?\d+)"
    yard_gain : str = rf"(({yards}) (yards?)|no gain)"
    rush_dir: str = "((right|left) (guard|end|tackle)|up the middle)"
    pass_dir: str = "((deep|short) (right|left|middle)|(right|left|middle))"
    tackle: str = rf"(\((tackle by {player}|tackle by {player} and {player})\)|and {player} and {player}\))"
    team: str = "([A-Z]{2,3})"

    pos: str = rf"({team}--?(\d\d?)|50)"
    oob: str = rf"((ball )?out of bounds( at {pos})?)"

    recover: str = rf"(recovered by {player}( at {pos})?( {tackle})?)"
    returned: str = rf"(returned( by {player})? for {yard_gain}( {tackle})?)"

    penalty = rf"(" + "|".join([penalty.value for penalty in Penalty]) + ")"

    fumble = rf"({player} fumbles(, {recover})?( {oob})?)"
    force_fumble =  rf"({player} fumbles(, {oob})? \(forced by {player}\)(, {recover})?)"

    interception: str = rf"(is intercepted by {player} at {pos}( and {returned})?)"
    pass_defended: str = rf"(\(defended by {player}\))"  

    kick_miss: str = "(wide right|wide left|hit right upright|hit left upright)"
    blocked: str = rf"(blocked by {player}|blocked by {player}(, {returned})?(, {recover})?)"
    muffed: str = rf"(muffed catch by {player})"
    kick_yards: str = rf"(({yards}) yards?)"
    kick_type: str = "(off|onside)"