

import os
import cPickle as pickle
import numpy as np
import scipy.stats
import sys
import glob

parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent not in sys.path:
    sys.path.append(parent)

from league import League



def main():

    # TODO: analyze what the winning agents did well
    #     - what do their feature vectors look like?
    #     * Cluster the features (look at their rank, points scored, above/below avg)
    #     * Create an ML problem to rank feature vector (binary: is this one better?)
    #     - I want to try putting a prior over the feature vectors & observe success
    #     * compare what feature vectors do well in 1985 vs 2015

    # use feature vector to predict:
    #     1. number of wins
    #     2. total points scored
    #     2. above/below average
    X = []
    wins = []
    points = []
    wins_ranks = []
    breakdown_ranks = []

    low  = 0
    high = low + 200

    results_dir = os.path.join(os.path.dirname(parent), 'results')
    results_files = glob.glob('%s/*.league' % results_dir)
    #results_files = glob.glob('%s/1493349224.league' % results_dir)
    for i,league_pickle in enumerate(results_files):
        if i <  low: continue
        if i > high: break

        with open(league_pickle, 'rb') as f:
            leg = pickle.load(f)

        wins_ranking      = get_ranks(leg._standings)
        breakdown_ranking = get_ranks(leg._breakdown)

        for name,agent in leg._teams.items():
            x = feature_vec(agent._history_weights, agent._position_stat_weights)
            X.append(x)

            num_wins = leg._standings[name][0]
            wins.append(num_wins)

            p = 0.0
            for week in range(1,18):
                p += agent._team.score(week)
            points.append(p)

            wr = wins_ranking[name]
            wins_ranks.append(wr)

            br = breakdown_ranking[name]
            breakdown_ranks.append(br)

    '''
    print wins
    print points
    print wins_ranks
    print breakdown_ranks
    print
    '''

    label = 'points'
    data  = points
    print 
    print 'low    %s: %f' % (label, min(data))
    print 'high   %s: %f' % (label, max(data))
    print 'mean   %s: %f' % (label, sum(data)/len(data))
    print 'median %s: %f' % (label, sorted(data)[len(data)/2])
    mu = sum(data)/len(data)
    variance = sum([(d-mu)**2 for d in data]) / len(data)
    print 'stddev %s: %f' % (label, variance**0.5)
    print 

    print low, high, len(wins)
    print 'wins/points: ', scipy.stats.pearsonr(wins           , points    )
    print 'wins/rank:   ', scipy.stats.pearsonr(wins           , wins_ranks)
    print 'rank/points: ', scipy.stats.pearsonr(wins_ranks     , points    )
    print 'break/points:', scipy.stats.pearsonr(breakdown_ranks, points    )
    print 'break/wins:  ', scipy.stats.pearsonr(breakdown_ranks, wins      )
    print 'break/rank:  ', scipy.stats.pearsonr(breakdown_ranks, wins_ranks)
    exit()



def feature_vec(history_weights, pos_weights):
    ret = []
    ret += history_weights.tolist()
    for pos,weights in sorted(pos_weights.items()):
        ret += weights.tolist()
    return np.array(ret)




def cmp_record(ta,tb):
    a = ta[1]
    b = tb[1]
    # more wins
    if a[0] != b[0]:
        if a[0] < b[0]:
            return -1
        else:
            return 1
    else:
        # fewer losses
        if a[1] != b[1]:
            if a[1] > b[1]:
                return 1
            else:
                return -1
        else:
            # tie
            return 0


def get_ranks(standings):
    ordered = sorted(standings.items(), cmp=cmp_record, reverse=True)

    r = 0
    current = ordered[0][1]

    rank = {}
    for i,name_standing in enumerate(ordered):
        name,standing = name_standing
        if standing != current:
            r = i
            current = standing
        rank[name] = 10-r

    return rank
    #print sorted(rank.items(), key=lambda t:t[1])
    #exit()




if __name__ == '__main__':
    main()


