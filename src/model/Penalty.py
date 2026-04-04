from enum import Enum

class Penalty(Enum):
    chop_block = "Chop Block"
    clipping = "Clipping"

    defensive_delay = "Defensive Delay of Game"
    defensive_holding = "Defensive Holding"
    defensive_offside = "Defensive Offside"
    defensive_pi = "Defensive Pass Interference"
    def_too_may_men = "Defensive Too Many Men on Field"
    disqualification = "Disqualification"
    double_team_block = "Illegal Double-Team Block"

    encroachment = "Encroachment"

    face_mask = rf"Face Mask \(15 Yards\)"
    false_start = "False Start"

    horse_collar = "Horse Collar Tackle"

    illegal_blindside_block = "Illegal Blindside Block"
    illegal_block_waist = "Illegal Block Above the Waist"
    illegal_contact = "Illegal Contact"
    illegal_crackback = "Illegal Crackback"
    illegal_formation = "Illegal Formation"
    illegal_forward_pass = "Illegal Forward Pass"
    illegal_motion = "Illegal Motion"
    illegal_shift = "Illegal Shift"
    illegal_substitution = "Illegal Substitution"
    illegal_touch_kick = "Illegal Touch Kick"
    illegal_touch_pass = "Illegal Touch Pass"
    illegal_use_of_hands = "Illegal Use of Hands"
    illegal_wedge = "Illegal Wedge"
    ineligible_downfield = "Ineligible Downfield Pass"
    ineligible_downfield_kick = "Ineligible Downfield on Kick"
    ineligible_downfield_pass = "Ineligible Downfield Pass"
    intentional_grounding = "Intentional Grounding"

    kick_catch_interference = "Kick Catch Interference"

    leverage = "Leverage"
    lower_head = "Lowering the Head to Initiate Contact"

    neutral_zone_infraction = "Neutral Zone Infraction"

    offensive_holding = "Offensive Holding"
    offensive_offside = "Offensive Offside"
    offensive_pi = "Offensive Pass Interference"
    off_too_may_men = "Offensive Too Many Men on Field"
    offside_free_kick = "Offside on Free Kick"

    player_oob_kick = "Player Out of Bounds on Kick"

    roughing_thekicker = "Roughing the Kicker"
    roughing_the_passer = "Roughing the Passer"
    running_into_the_kicker = "Running Into the Kicker"

    taunting = "Taunting"
    tripping = "Tripping"

    unnecessary_roughness = "Unnecessary Roughness"
    unsportsmanlike_conduct = "Unsportsmanlike Conduct"