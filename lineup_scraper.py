from pyquery import PyQuery as pq
import requests

"""
Scrapes starting lineups from baseballpress
uses mlbID to grab 2015 stats from mlb
    game day data also available, but not used
constructs batter and pitcher objects
constructs game objects
returns the days games (could be any day by adjusting the url)
    as an array of game objects
WARNING - hits mlb with 300 requests for a full slate of games
"""

# ### ---- to do ----  ### #
# improve game class
#   add methods
# add game time
# parse weather
# maybe find if roster exists - then avoid mlb calls?
#   - still have to hit bball press - could be changes


# alternate scrapes
# addy = "http://www.baseballpress.com/lineups/2015-04-18"  # e.g. past w/ rosters out
# addy2 = "http://www.rotowire.com/baseball/daily_lineups.htm"  #alt source


class Game(object):
    """ Game object, game_time not currently working """
    def __init__(self, away_name, home_name, weather, game_time, away_starter, away_lineup, home_starter, home_lineup):
        (Game, self).__init__()
        self.away_name = away_name
        self.home_name = home_name
        self.weather = weather
        self.game_time = game_time
        self.away_starter = away_starter
        self.away_lineup = away_lineup
        self.home_starter = home_starter
        self.home_lineup = home_lineup


class Player(object):
    """ Base player properties """
    def __init__(self, name, mlbID, bbref):
        # super(Player, self).__init__()
        self.name = name
        self.mlbID = mlbID
        self.bbref = bbref

    def get_lahman(self, bbref):  # maybe name too
        pass


class Batter(Player):
    """ year to date stats for Batter"""
    def __init__(self, name, mlbID, bbref, ab, h, h2b, h3b, hr, bb, hbp, r, sb, cs, rbi, k):
        self.ab = ab
        self.h = h
        self.h2b = h2b
        self.h3b = h3b
        self.k = k
        self.hbp = hbp
        self.r = r
        self.hr = hr
        self.bb = bb
        self.sb = sb
        self.cs = cs
        self.rbi = rbi
        super(Batter, self).__init__(name, mlbID, bbref)

    def make_woba(self):
        pass


def make_batter(name, player_dict, stats_dict):
    batter = Batter(name=name,
                    mlbID=player_dict['data-mlb'],
                    bbref=player_dict['data-bref'],
                    ab=stats_dict['s_ab'],
                    h=stats_dict['s_single'],
                    h2b=stats_dict['s_double'],
                    h3b=stats_dict['s_triple'],
                    hr=stats_dict['s_hr'],
                    bb=stats_dict['s_bb'],
                    hbp=stats_dict['s_hbp'],
                    r=stats_dict['s_r'],
                    sb=stats_dict['s_sb'],
                    cs=stats_dict['s_cs'],
                    rbi=stats_dict['s_rbi'],
                    k=stats_dict['s_so'])
    return batter


class Pitcher(Player):
    """ year to date stats for Pitcher"""
    def __init__(self, name, mlbID, bbref, ip, k, bb, hr, hbp, r):
        self.ip = ip
        self.k = k
        self.hbp = hbp
        self.r = r
        self.hr = hr
        self.bb = bb
        super(Pitcher, self).__init__(name, mlbID, bbref)

    def make_xfip(self):
        pass

    def get_old_stats(self):
        pass


def make_pitcher(name, player_dict, stats_dict):
    starter = Pitcher(name=name,
                      mlbID=player_dict['data-mlb'],
                      bbref=player_dict['data-bref'],
                      ip=stats_dict['s_ip'],
                      k=stats_dict['s_k'],
                      hbp=stats_dict['s_hbp'],
                      r=stats_dict['s_er'],
                      hr=stats_dict['s_hra'],
                      bb=stats_dict['s_bb'])
    return starter


def get_2015_stats(mlbID, pitcher=False):
    ''' returns a dictionary of 2015 & daily stats for a given mlbID  '''
    ''' assumes ID represents a batter, if a starter set to True '''
    ''' daily stats have no prefix, season ones: s_ prefix  '''
    ''' e.g. dict["r"] gives today's runs whereas dict["s_r"] gives season runs '''
    if pitcher:
        pos = "pitchers"
    else:
        pos = "batters"
    player_addy = "http://gd2.mlb.com/components/game/mlb/year_2015/{}/{}.xml".format(pos, mlbID)
    # print player_addy
    response = requests.get(player_addy)
    player_doc = pq(response.content)
    st15_dict = dict(zip(player_doc[0].keys(), player_doc[0].values()))
    # print st15_dict
    return st15_dict


def process_data(player_data, pitcher=False):
    ''' grabs the Player data incl mlbID from the lineup '''
    ''' uses mlbID to grab current season data '''
    ''' constructs Pitcher or Batter Object '''
    player_name = pq(player_data).text()
    # print player_name
    player_keys = player_data.keys()
    player_values = player_data.values()
    player_dict = dict(zip(player_keys, player_values))
    mlb_id = player_dict['data-mlb']
    player_stats = get_2015_stats(mlb_id, pitcher)
    if pitcher:
        player_obj = make_pitcher(player_name, player_dict, player_stats)
    else:
        player_obj = make_batter(player_name, player_dict, player_stats)
    return player_obj


def main():
    addy = "http://www.baseballpress.com/lineups"

    response = requests.get(addy)
    doc = pq(response.content)

    games_on_slate = doc('.team-data').length / 2
    print str(games_on_slate) + " games on todays slate"

    games = doc('.main-lineup').children('.game')
    # loop through games

    # truncate games for test to reduce hits on mlb site
    # games = [games[0], games[1]]

    slate = []
    for game in games:
        away_lineup = []
        home_lineup = []
        # game_info = []

        weather = pq(game).find('.weather')
        # print weather  # kinda useless - no wing

        team_names = pq(game).find(".team-name")
        away_name = pq(team_names[0]).text()
        home_name = pq(team_names[1]).text()
        # game_info = [weather, away_name, home_name]  # likely want game time too
        # print game_info

        game_time = "1:07pm"  # filler

        # returns stater array [0] is away, [1] is home
        starter_data = pq(game).find(".text a")

        # make starter objects away/home
        away_starter_obj = process_data(starter_data[0], True)
        # away.append(away_starter_obj)

        home_starter_obj = process_data(starter_data[1], True)
        # home.append(home_starter_obj)

        # add away/home batting orders
        away_batter_array = pq(game).find('.cssDialog .players').eq(0).find('div a')
        if len(away_batter_array) != 9:
            print "No away roster yet!"
        else:
            for batter in away_batter_array:
                batter_obj = process_data(batter)
                away_lineup.append(batter_obj)

        home_batter_array = pq(game).find('.cssDialog .players').eq(1).find('div a')
        if len(home_batter_array) != 9:
            print "No Home roster yet!"
        else:
            for batter in home_batter_array:
                batter_obj = process_data(batter)
                home_lineup.append(batter_obj)

        # construct game object
        game_obj = Game(away_name, home_name, weather, game_time, away_starter_obj, away_lineup, home_starter_obj, home_lineup)
        # append game object to slate
        slate.append(game_obj)

    return slate
