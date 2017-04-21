
import os
import sys
import re
from collections import namedtuple, defaultdict
import random
import math


base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
code_dir = os.path.join(base_dir, 'code')
if code_dir not in sys.path:
    sys.path.append(code_dir)


from search_name import query_name
from player import Player, plays
from agent import Agent, position_stats
import ff_team



# cuz why not?
random.seed(5)



def main():

    # where to build pre-built league
    league_dir = sys.argv[1]

    # build league
    ps = League('2016')
    ps.load_from_dir(league_dir)

    # simulate season
    ps.run()



class League:

    def __init__(self, year):
        self._year = year

        # things that need to be set before you can begin
        self._teams = {}
        self._schedule = {}
        self._weeks = None

        # things that are updated as the season progresses
        self._week = 0
        self._standings = {}

        # pool of ALL football players for that year
        self._players = {'available':{}, 'taken':{}}
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(base_dir, 'data')
        names_file = os.path.join(data_dir, year, 'meta', 'names_index')
        players_dir = os.path.join(data_dir, year, 'raw', 'players')
        with open(names_file, 'r') as f:
            for line in f.readlines():
                pid = line.split()[0]
                name,position,team = line.strip().split('\t')[1].split('||')
                player_file = os.path.join(players_dir, pid)
                p = Player(player_file)
                #p = (name,position,team)
                if p.position() in ff_team.simple_positions:
                    self._players['available'][pid] = p

        '''
        # determine the most common stats for each position
        position_stats = defaultdict(lambda:defaultdict(int))
        for pid,p in self._players['available'].items():
            position = ff_team.simple_positions[p.position()]

            weekly_stats = p._stats
            for week,stats in weekly_stats.items():
                for stat in stats.keys():
                    position_stats[position][stat] += 1

        for position,stat_types in position_stats.items():
            print position
            big = max(stat_types.values())
            for t,freq in sorted(stat_types.items(), key=lambda t:t[1]):
                print '%4d %s' % (freq,t)
            print 
        '''


    def load_from_dir(self, league_dir):
        # metadata
        meta = load_metadata(league_dir)

        # year
        year = meta['year']
        assert year == self._year

        # number of weeks in the season
        self._weeks = meta['weeks']

        # number of weeks in the season
        if 'schedule' in meta:
            self._schedule = meta['schedule']

        # assemble the collection of teams in the league
        for roster_name in os.listdir(league_dir):
            if not roster_name.endswith('.roster'):
                continue

            # build team
            roster_file = os.path.join(league_dir, roster_name)
            team = ff_team.FantasyTeam(year)
            team.load_from_file(roster_file)

            # all players owned by this agent are now unavailable
            for player in team.players():
                pid = player.id()
                del self._players['available'][pid]
                self._players['taken'][pid] = player

            # build Agent to manage the team
            agent = Agent(team)

            # owner id
            owner = roster_name.split('.')[0]

            assert owner not in self._teams, Exception('two teams with the same owner')
            self._teams[owner] = agent

        # If it didn't come with a schedule, then generate one yourself
        self._schedule = self.generate_schedule(self._teams.keys(), self._weeks)

        # ready to begin season!
        self._week = 1
        self._standings = {owner:[0,0,0] for owner in self._teams.keys()}


    def generate_schedule(self, teams, weeks):
        ''' this is not generated with divisions or fairness/eveness '''
        n = len(teams)/2

        schedule = {}
        #for i in range(weeks-3):   # remember, 3 weeks are for playoffs
        for i in range(weeks):   # remember, 3 weeks are for playoffs
            week = i+1

            # shuffle teams and pair them off
            random.shuffle(teams)
            h1 = teams[:n]
            h2 = teams[n:]
            pairs = zip(h1,h2)
 
            schedule[week] = pairs
        return schedule



    def run(self):

        print '\n'
        print 'week 0'
        print self
        print '\n'

        # keeps track of which players did best each week
        # useful for Agents deciding which pickups to make
        standings = []

        # 16 week season
        for i in range(self._weeks):
            week = i+1

            # update scores
            weekly_standings = self.run_week(week)

            # combine this week into this history of all standings
            standings.append(weekly_standings)

            print '\n'
            print 'week %d' % week
            print self
            print '\n'

            '''
            print 
            for owner in self._teams.keys():
                print self._teams[owner]._team
                print 
            print
            '''
            #print self._teams['willie']._team

            # Note: by going in standings order, we simulate the waiver wire
            # allow agents to update rosters
            env = [self._players, standings]
            active = sorted(self._standings.items(), cmp=record_cmp)
            i = 0
            while len(active) > 0 and (i<5):
                # agents who are not done get re-added to the queue
                new_active = []
                for owner,record in active:
                    done = self._teams[owner].update(week, record, env)
                    if not done:
                        new_active.append((owner,record))
                active = new_active
                i += 1

            # every team must set their lineup with the new players
            owners = self._teams.keys()
            for owner in owners:
                self._teams[owner].set_lineup(week)



    def run_week(self, week):
        ''' how did everyone do this week? '''
        assert self._week > 0

        # Regular Season
        #if self._week < 14:
        if True:
            for pair in self._schedule[week]:
                owner1,owner2 = pair
                comp = self.head_to_head(owner1, owner2)
                if comp < 0:
                    self._standings[owner1][1] += 1 # loss
                    self._standings[owner2][0] += 1 # win
                elif comp > 0:
                    self._standings[owner1][0] += 1 # loss
                    self._standings[owner2][1] += 1 # win
                else:
                    self._standings[owner1][2] += 1 # tie
                    self._standings[owner2][2] += 1 # tie

        '''
        # Wild Card round
        elif self._week == 14:
            # playoff berthds determined by seeding
            top6 = sorted(self._standings.items(), cmp=record_cmp, reverse=True)[:6]
            rem = [owner for owner,record in top6]

            # 1 and 2 seeds get a first round bye
            self._schedule[14] = [(rem[2],rem[5]), (rem[3],rem[4])]

            
            for pair in self._schedule[week]:
                owner1,owner2 = pair
                s1 = self._teams[owner1].score(week)
                s2 = self._teams[owner2].score(week)

                if s1 < s2:
                    self._standings[owner1][1] += 1 # loss
                    self._standings[owner2][0] += 1 # win

            # schedule for next week is determined by winners
            self._schedule[15] = [(rem[0],None),(rem[1],None)]
        '''

        self._week += 1

        # TODO: holds information about which players were best at each position
        weekly_standings = {pos:{} for pos in ff_team.simple_positions.values()}
        for pid,p in self._players['available'].items():
            position = ff_team.simple_positions[p.position()]
            stats = p.stats(week)
            score = p.score(week)
            vals = []
            for stat in position_stats[position]:
                # this at least lets the (dumb) AI understand importance
                #vals.append(stats[stat])
                #vals.append(stats[stat] * math.sign(plays[stat]))
                vals.append(stats[stat] * plays[stat])
            weekly_standings[position][p.id()] = vals

        return weekly_standings


    def head_to_head(self, owner1, owner2):
        s1 = self._teams[owner1].score(self._week)
        s2 = self._teams[owner2].score(self._week)

        if s1 < s2:
            return -1
        elif s1 > s2:
            return 1
        else:
            return 0


    def __str__(self):
        ret = []

        # Regular Season
        #if self._week < 14:
        if True:
            standings = sorted(self._standings.items(),cmp=record_cmp, reverse=True)
            for i,(owner,record) in enumerate(standings):
                record_str = '-'.join(map(str,record))
                ret.append('\t%2d. %-8s (%s)' % (i+1,owner,record_str))

        '''
        # print standings that will lead to Wild Card seeding
        elif self._week == 14:
            standings = sorted(self._standings.items(),cmp=record_cmp, reverse=True)
            for i,(owner,record) in enumerate(standings[:6]):
                record_str = '-'.join(map(str,record))
                ret.append('\t%2d. %-8s (%s)' % (i+1,owner,record_str))
            ret.append('')
            for i,(owner,record) in enumerate(standings[6:]):
                i = i+6
                record_str = '-'.join(map(str,record))
                ret.append('\t%2d. %-8s (%s)' % (i+1,owner,record_str))

        # other
        else:
            print 'PLAYOFF STRING!'
            exit()
        '''

        return '\n'.join(ret)





def record_cmp(tup_a,tup_b):
    a = tup_a[1]
    b = tup_b[1]

    # more wins
    if a[0] > b[0]:
        return 1
    if a[0] < b[1]:
        return -1

    # more losses
    if a[1] < b[1]:
        return 1
    if a[1] > b[1]:
        return -1

    return 0



def load_metadata(league_dir):
    info_file = os.path.join(league_dir, 'info.txt')
    with open(info_file, 'r') as f:
        text = f.read()
    lines = text.split('\n')

    meta = {}

    meta['year'] = lines[0]
    meta['weeks'] = int(lines[1])
    meta['schedule'] = None

    return meta



if __name__ == '__main__':
    main()

