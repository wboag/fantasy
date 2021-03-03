

import os
import sys
import re
from collections import defaultdict
from subprocess import check_output, CalledProcessError, STDOUT

from nfl_team import team_to_real_week
import ff_team



def getstatusoutput(cmd):
    try:
        data = check_output(cmd, shell=True, universal_newlines=True, stderr=STDOUT)
        status = 0
    except CalledProcessError as ex:
        data = ex.output
        status = ex.returncode
    if data[-1:] == '\n':
        data = data[:-1]
    return status, data


def main():

    name = sys.argv[1]
    teams = None
    position = 'LB1'
    #position = 'WR'
    #name = 'Tom Brady'
    #teams = ['NWE']

    pid = query_name(name, teams=teams, position=position)

    print(name)
    print(teams)
    print(pid)




def query_name(name, teams=None, position=None, year='*'):
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(parent_dir, 'data')

    query = 'grep -i "%s" %s/%s/meta/names_index' % (name,data_dir,year)

    # run query
    status,output = getstatusoutput(query)
    assert status==0

    candidates = output.split('\n')
    candidate_players = map(QuickPlayer, candidates)

    if len(candidates) == 1:
        # unambiguous 
        p = candidate_players[0]

        # ensure no funny business
        if position:
            assert p.position == position
        if teams: 
            #print '\t', p.teams
            #print '\t', set(teams)
            assert p.teams == set(teams)
        return p.pid

    elif len(candidates) == 0:
        print('NO MATCHES')
        exit()
    else:

        # does position disambiguate it?
        if position:
            pos_p = [ p for p in candidate_players if same_pos(p.position,position) ]
            if len(pos_p) == 1:
                pid = pos_p[0].pid
                return pid

        # does team disambiguate it?
        if teams:
            teams_p = [ p for p in candidate_players if common(p.teams,teams) ]
            if len(teams_p) == 1:
                pid = teams_p[0].pid
                return pid

        raise Exception('Ambiguous name query')

    return pid



def same_pos(pos1, pos2):
    if pos1 not in ff_team.positions:
        pos1 = ff_team.position_casts[pos1]
    return pos2 in pos1



def common(a,b):
    return len(a&set(b))



class QuickPlayer:
    def __init__(self, info_str):
        pid,info = info_str.split('\t')
        name,position,teams = info.split('||')
        self.pid = pid.strip()
        self.name = name
        self.position = position
        self.teams = set(teams.split(','))




if __name__ == '__main__':
    main()


