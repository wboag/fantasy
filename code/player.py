

import os
import sys
import re
from collections import defaultdict

from nfl_team import team_to_real_week



def main():

    qb_file = '/Users/wboag/projects/fantasy/data/2016/raw/players/%s' % sys.argv[1]

    qb = Player(qb_file)


    print 
    print '%s (%s)' % (qb.name(), qb.id())
    print qb.position()
    for i in range(1,18):
        score = qb.score(i)
        print '\tweek %2d: %6.2f' % (i,score)
    print 




def read_file_position(player_file):
    with open(player_file, 'r') as f:
        text = f.read()
    regex = '<strong>Position</strong>: (\w+)'
    match = re.search(regex, text)
    return match.groups()[0]



lb_corrections = set(['Melvin Ingram'])
db_corrections = set(['Kurt Coleman'])
dl_corrections = set(['Khalil Mack', 'Cameron Wake'])



class Player:

    def __init__(self, player_file):
        # read player's data file
        with open(player_file, 'r') as f:
            text = f.read()

        # unique identifier for this player
        self._id = os.path.split(player_file)[-1]

        # position determines what kind of stats are measured
        self._name = read_name(text)

        # position determines what kind of stats are measured
        self._position = read_position(text)
        self.__position_correction()

        # year: useful info to store on-hand
        self._year = read_year(text)

        # read other infomration
        self._teams = read_teams(text)
        #assert len(set(teams)) == 1  # would assert single-player teams

        # get stats for each week (indexed by real-week)
        self._stats = read_stats(text)

        # memoize scores
        self._scores = {}


    def id(self):
        return self._id


    def name(self):
        return self._name


    def position(self):
        return self._position


    def stats(self, week):
        ret = defaultdict(float)
        if week in self._stats:
            ret.update(self._stats[week])
        return ret


    def score(self, week):
        ''' http://www.nfl.com/fantasyfootball/help/nfl-scoringsettings '''

        # if memoized
        if week in self._scores:
            return self._scores[week]

        # if player didn't play (e.g. on a bye week)
        if week not in self._stats:
            self._scores[week] = 0.0
            return 0.0

        '''
        Passing Yards: 1 point per 25 yards passing
        Passing Touchdowns: 4 points
        Interceptions: -2 points
        Rushing Yards: 1 point per 10 yards
        Rushing Touchdowns: 6 points
        Receiving Yards: 1 point per 10 yards
        Receiving Touchdowns: 6 points
        Fumble Recovered for a Touchdown: 6 points
        2-Point Conversions: 2 points
        Fumbles Lost: -2 points
        '''

        '''
        Tackle:          1   point
        Assisted Tackle:  .5 points
        Sack:            2   points
        Interception:    2   points
        Forced Fumble:   2   points
        Fumble Recovery: 2   points
        Touchdown (Interception Return): 6 points
        Touchdown (Fumble Return): 6 points
        Touchdown (Blocked Kick, Punt, or Missed FG Return): 6 points
        Blocked Kick (Punt, FG or PAT): 2 points
        Safety: 2 points
        Pass Defended: 1 point
        '''

        score = 0.0
        for k,v in self._stats[week].items():
            score += v * plays[k]

        '''
        covered = set(plays.keys())
        for val in self._stats[week].keys():
            if val not in covered:
                print self._stats[week].keys()
                print 'MISSED: ', val
                #exit(1)
        '''

        # TODO
        'fumble recovered for a touchdown'
        'fumbles lost'

        self._scores[week] = score
        return score


    def __position_correction(self):
        if self.name() in db_corrections:
            self._position = 'DB'
        if self.name() in dl_corrections:
            self._position = 'DL'
        if self.name() in lb_corrections:
            self._position = 'LB'


    def __str__(self):
        #info = '%-20s  |  %-3s  |  %s' % (self._name,self._position,','.join(self._teams))
        #info = '%-20s  (%s)' % (self._name,','.join(self._teams))
        info = '%-20s  (%s)' % (self._name,self._position)
        return info




def read_name(text):
    #regex = "<title>([\.a-zA-Z'\s]+) \d+ Game Log | Pro-Football-Reference.com</title>"
    regex = "<title>([^|]+) \d+ Game Log | Pro-Football-Reference.com</title>"
    match = re.search(regex, text)

    # NOTE - fuck James O'Shaughnessy. we'll throw an exception and exclude him.
    '''
    if not match.groups()[0]:
        regex = "<title>([^|]+) Stats | Pro-Football-Reference.com</title>"
        match = re.search(regex, text)
    '''

    return match.groups()[0].strip()



def read_year(text):
    regex = "<title>[^|]+ (\d+) Game Log | Pro-Football-Reference.com</title>"
    match = re.search(regex, text)
    return match.groups()[0].strip()



def read_position(text):
    regex = '<strong>Position</strong>: (\w+)'
    match = re.search(regex, text)
    if match:
        return match.groups()[0]
    else:
        regex = '<b>Position</b>: (\w+)'
        match = re.search(regex, text)
        if match:
            return match.groups()[0]
        else:
            return 'unkown'


def read_teams(text):
    teams = []
    regex = '<tr.*</tr>'
    matches = re.findall(regex, text)
    for match in matches:
        if not re.search('<tr id="stats\.(\d+)"\s*>', match): continue
        team_m     = re.search('data-stat="team"\s*><a\s*href="/teams/(\w+)/\d+\.htm">\w+</a>',match)
        team = team_m.groups()[0].upper()

        teams.append(team)
    return list(set(teams))




def read_stats(text):
    # indexed by real-week values
    stats = defaultdict(lambda:defaultdict(float))

    # might as well get the year automatically, since its sitting there (for free)
    date_regex = '<title>.* (\d+) Game Log | Pro-Football-Reference.com</title>'
    year = re.search(date_regex, text).groups()[0]

    regex = '<tr id="stats\.\d+.+?</td></tr>'
    matches = re.findall(regex, text)
    for match in matches:
        if not re.search('<tr id="stats\.(\d+)"\s*>', match): continue

        # getting team matters for converting team week into real week 
        team_m = re.search('data-stat="team"\s*><a href="/teams/([^/]+)/\d+.htm">',match)
        team = team_m.groups()[0].upper()

        # NOTE - only gets integers stats (e.g. excludes %s and ratings)
        # get the player stats
        stats_regex = '<td class="right " data-stat="(\w+)"\s*>(-?\d+)</td>'
        week_stats_str = re.findall(stats_regex, match)
        week_stats = defaultdict(float)
        for key,val in week_stats_str:
            week_stats[key] = int(val)

        # convert team week to real week
        team_week = int(week_stats['game_num'])
        real_week = team_to_real_week(year, team, team_week)
        del week_stats['game_num']

        # store stats
        stats[real_week] = week_stats

        '''
        print real_week
        for key,val in sorted(week_stats.items()):
            print '\t', key, val
        print
        '''

    '''
    <td class="right " data-stat="pass_cmp" >12</td>
    <td class="right " data-stat="pass_att" >21</td>
    <td class="right " data-stat="pass_cmp_perc" >57.14</td>
    <td class="right " data-stat="pass_yds" >134</td>
    <td class="right " data-stat="pass_td" >0</td>
    <td class="right " data-stat="pass_int" >0</td>
    <td class="right " data-stat="pass_rating" >76.3</td>
    <td class="right " data-stat="pass_sacked" >2</td>
    <td class="right " data-stat="pass_sacked_yds" >14</td>
    <td class="right " data-stat="pass_yds_per_att" >6.38</td>
    <td class="right " data-stat="pass_adj_yds_per_att" >6.38</td>
    <td class="right " data-stat="rush_att" >1</td>
    <td class="right " data-stat="rush_yds" >-1</td>
    <td class="right " data-stat="rush_yds_per_att" >-1.00</td>
    <td class="right " data-stat="rush_td" >0</td>
    <td class="right " data-stat="targets" >0</td>
    <td class="right " data-stat="rec" >0</td>
    <td class="right " data-stat="rec_yds" >0</td>
    <td class="right " data-stat="rec_yds_per_rec" ></td>
    <td class="right " data-stat="rec_td" >0</td>
    <td class="right " data-stat="catch_pct" >0.0%</td>
    <td class="right " data-stat="rec_yds_per_tgt" ></td>
    <td class="right " data-stat="all_td" >0</td>
    <td class="right " data-stat="scoring" >0</td>
    '''

    return { k:dict(v) for k,v in stats.items() }




plays = {'pass_yds'       :(1/25.0),      # 1  point  per 25 passing yards
         'pass_td'        :4.0     ,      # 4  points per    passing touchdown
         'pass_int'       :-2.0    ,      # -2 points per    interception
         'pass_att'       :0.0     ,      #
         'pass_cmp'       :0.0     ,      #
         'pass_sacked'    :0.0     ,      # times sacked
         'pass_sacked_yds':0.0     ,      # yards lost due to sack

         'rec'     :0.0     ,      # not PPR
         'targets' :0.0     ,      # 
         'rec_yds' :0.1     ,      # 1  point  per 10 receiving yards
         'rec_td'  :6.0     ,      # 6  points per    receiving touchdown

         'rush_att':0.0     ,      #    attempts dont matter
         'rush_yds':0.1     ,      # 1  point  per 10 rushing yards
         'rush_td' :6.0     ,      # 6  points per    rushing touchdown

         'two_pt_md'   :2.0 ,      # successful 2pt conversion
         'kick_ret'    :0.0 ,      # 
         'kick_ret_yds':0.0 ,      # 
         'kick_ret_td' :6.0 ,      # 
         'punt_ret'    :0.0 ,      # 
         'punt_ret_yds':0.0 ,      # 
         'punt_ret_td' :6.0 ,      # 

         'safety_md'      :2.0,
         'punt_blocked'   :2.0,    # all blocked kicks are worth 2

         'def_int'        :2.0,
         'def_int_yds'    :0.0,
         'def_int_td'     :6.0,
         'tackles_assists':0.5,
         'tackles_solo'   :1.0,

         'scoring':0.0,
         'all_td' :0.0,

         'xpm'    :1.0,            # PAT
         'xpa'    :0.0,            # PAT attempt
         'fgm'    :1.0,            # FG 
         'fga'    :0.0,            # FG attempt

         'punt_yds':0.0,           # this will be useful for my punter league
         'punt'    :0.0,           # this will be useful for my punter league

         'age'     :0.0,           # dunno why this was listed for kender00
}





if __name__ == '__main__':
    main()


