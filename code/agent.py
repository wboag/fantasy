
import os
import numpy as np
from collections import defaultdict
import re

import ff_team



def build_position_stats():
    ''' using the frequencies of position stats from 2016 '''
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'data')
    position_stats_file = os.path.join(data_dir, 'ai', 'position_values.txt')

    # load 
    with open(position_stats_file, 'rb') as f:
        text = f.read()

    # for each position
    pos_stats = {}
    sections = text.split('\n\n')
    for section in sections:
        #print section
        lines = section.strip().split('\n')
        pos = lines[0]
        freq = {}
        for entry in lines[1:]:
            toks = entry.split()
            freq[toks[1]] = int(toks[0])

        # keep all stats that occur in at least 25% of the entries
        big = max(freq.values())
        useful = [ stat for stat,f in freq.items() if (4*f > big) ]

        pos_stats[pos] = useful

    return pos_stats

# e.g. determine QBs tend to all have passing yards but not receiving yards
position_stats = build_position_stats()



def build_roster_spots():
    # positions of need
    need = defaultdict(int)
    for pos in ff_team.fantasy_positions:
        pos = re.sub('\d','', pos)

        # TODO - fix simplifying assumption
        if pos == 'FLEX':
            pos = 'WR'

        #if pos == 'FLEX':
        #    flex= [p for p,legal in ff_team.position_casts.items() if ('FLEX'in legal)]
        #    for p in flex:
        #        need[p] += 1
        #else:
        need[pos] += 1
    return need

roster_spots = build_roster_spots()



class Agent:

    def __init__(self, team):
        self._team = team

        # generate parameters that govern how it behaves in update() and manages itself

        # how much weight to give to previous weeks when deciding player's value
        self._history = np.random.randint(6) + 1
        self._history_weights = np.random.rand(self._history)
        self._history_weights /= self._history_weights.sum()

        # for each position, how much weight to give to each stat
        self._position_stat_weights = {}
        for position,stats in position_stats.items():
            weights = np.random.rand(len(stats) + 1)  # the extra 1 is for the 'score'
            weights /= weights.sum()
            self._position_stat_weights[position] = weights

        # TODO - trades


    def score(self, week):
        return self._team.score(week)


    def update(self, week, record, env):

        # TODO - release IR people

        # TODO - use multiple previous weeks of history
        # what FA players are the best for each position?
        available = env[0]['available']
        week_perf = env[1][week-1]
        week_scores=week_standings(week_perf,week,available,self._position_stat_weights)

        upgrades = {}
        for pos,need in roster_spots.items():
            best = top_available(week_scores[pos], 2)
            upgrades[pos] = best

        # how good are your own players?
        current_scores = {pos:{} for pos in set(ff_team.simple_positions.values())}
        for p in self._team.players():
            pos = ff_team.simple_positions[p.position()]

            # each of the previous self._history number of weeks
            u = utility(p, week, self._history, self._position_stat_weights, 
                        self._history_weights)

            current_scores[pos][p.id()] = u
        current = {}
        for pos,scores in current_scores.items():
            current[pos] = sorted(scores.items(), key=lambda t:t[1])

        '''
        for pos in current.keys():
            print pos
            for pid,u in sorted(current[pos], key=lambda t:t[1]):
                print '\t%5.3f %s' % (u,pid)
            print
        print 
        print '---'
        print

        for pos in upgrades.keys():
            print pos
            for pid,u in sorted(upgrades[pos], key=lambda t:t[1]):
                print '\t%5.3f %s' % (u,pid)
            print
        print 
        print '---'
        print
        '''

        # which acquisitions would really help?
        improvements = []
        for pos in upgrades.keys():
            # who is the current worst player at that position?
            left = [(p,s) for (p,s) in current[pos]]
            worst_pid,worst_owned = sorted(left, key=lambda t:t[1])[0]

            # how much upgrade value does the new position add?
            for candidate,score in upgrades[pos]:
                advantage_over_current = score - worst_owned
                if advantage_over_current > 0.0:
                    improvements.append((pos,candidate,worst_pid,advantage_over_current))

                    # get the new worst player
                    left = [(p,s) for (p,s) in current[pos]]
                    worst_pid,worst_owned = sorted(left, key=lambda t:t[1])[0]

        improvements = sorted(improvements, key=lambda t:-t[-1])

        # will any additions help?
        if not improvements:
            done = True
            return done

        # do the most helpful improvement
        pos,new_pid,old_pid,up = improvements[0]

        # release old player
        old_p = env[0]['taken'][old_pid]
        self._team.drop_player(old_p)
        del env[0]['taken'][old_pid]
        env[0]['available'][old_pid] = old_p

        # add new player
        new_p = env[0]['available'][new_pid]
        self._team.add_player(new_p)
        del env[0]['available'][new_pid]
        env[0]['taken'][new_pid] = new_p

        done = False
        return done



    def set_lineup(self, week):
        #print self._team

        # its easiest to start with just deactivating everyone & let them all earn it
        for pos,p in self._team._active.items():
            self._team.deactivate_player(pos)

        # determine how much you like each player
        def eval_player(pp):
            return utility(pp, week, self._history, 
                           self._position_stat_weights, self._history_weights)

        # set lineup
        active = set()
        for pos in ff_team.fantasy_positions:
            # find all players who could fill that spot
            candidates = []
            for p in self._team._players:
                player_pos = ff_team.position_casts[p.position()]
                if (pos in player_pos) and (p.id() not in active):
                    if p.id() not in active:
                        candidates.append(p)
                else:
                    if ff_team.is_position_exception(p, pos):
                        if p.id() not in active:
                            candidates.append(p)

            #print pos, candidates
            #if len(candidates) == 0: continue

            # pick the best player of the available ones
            scores = map(eval_player, candidates)
            inds = np.argsort(scores)
            best = candidates[inds[-1]]

            # add that player to the active roster
            self._team.set_roster(pos, best)
            active.add(best.id())




def week_standings(stats, week, available, position_stat_weights):
    best = {pos:{} for pos in stats.keys()}
    for pos in stats.keys():
        for pid,player_week_stats in stats[pos].items():
            # why bother ranking people you dont care about?
            if pid not in available:
                continue

            fantasy_score = available[pid].score(week)
            feats = player_week_stats + [fantasy_score]
            week_utility = np.dot(feats, position_stat_weights[pos])
            best[pos][pid] = week_utility
    return best



def top_available(week_scores, N):
    top = sorted(week_scores.items(), key=lambda t:t[1])
    return top[-N:]



def utility(p, week, history, position_stat_weights, history_weights):
    # TODO - compute utility with multiple weeks back as well
    pos = ff_team.simple_positions[p.position()]
    score = 0.0
    for i,w in enumerate([week]):
        stats = p.stats(week)
        fantasy_score = p.score(week)

        # compute how highly this agent rates that player
        feats = [stats[s] for s in position_stats[pos]] + [fantasy_score]
        week_utility = np.dot(feats, position_stat_weights[pos])
        score += week_utility * history_weights[i]
    return score


