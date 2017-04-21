

import os
import sys
import re
from bs4 import BeautifulSoup





def team_to_real_week(year, team, team_week):
    team_bye = bye_table[year][team]
    if team_week < team_bye:
        return team_week
    else:
        return team_week + 1





def build_bye_table(bye_file):

    teams = {}

    with open(bye_file, 'r') as f:
        text = f.read()

    # parse text
    text = text.replace('\n', '\t\t')
    m = re.search('<!-- START PRINTIT -->(.*)<!-- END PRINTIT -->', text)
    content = m.groups()[0].replace('\t\t', '\n')

    soup = BeautifulSoup(content, 'html5lib')
    trs = soup.findAll('tr')
    for tr in trs[1:]:
        pieces = tr.findAll('td')
        week = int(pieces[0].text[5:])
        bye_teams = map(str,pieces[1].text.split(', '))
        for team in bye_teams:
            t = translations[team]
            teams[t] = week

    # don't forget any teams
    assert len(teams) == 32

    return teams





translations = {
                'Arizona':'CRD'        ,    'Cardinals' :'CRD',
                'Atlanta':'ATL'        ,    'Falcons'   :'ATL',
                'Baltimore':'RAV'      ,    'Ravens'    :'RAV',
                'Buffalo':'BUF'        ,    'Bills'     :'BUF',
                'Carolina':'CAR'       ,    'Panthers'  :'CAR',
                'Chicago':'CHI'        ,    'Bears'     :'CHI',
                'Cincinnati':'CIN'     ,    'Bengals'   :'CIN',
                'Cleveland':'CLE'      ,    'Browns'    :'CLE',
                'Dallas':'DAL'         ,    'Cowboys'   :'DAL',
                'Denver':'DEN'         ,    'Broncos'   :'DEN',
                'Detroit':'DET'        ,    'Lions'     :'DET',
                'Green Bay':'GNB'      ,    'Packers'   :'GNB',
                'Houston':'HTX'        ,    'Texans'    :'HTX',
                'Indianapolis':'CLT'   ,    'Colts'     :'CLT',
                'Jacksonville':'JAX'   ,    'Jaguars'   :'JAX',
                'Kansas City':'KAN'    ,    'Chiefs'    :'KAN',
                'Los Angeles':'RAM'    ,    'Rams'      :'RAM',
                'St. Louis':'RAM'      ,
                'Miami':'MIA'          ,    'Dolphins'  :'MIA',
                'Minnesota':'MIN'      ,    'Vikings'   :'MIN',
                'New England':'NWE'    ,    'Patriots'  :'NWE',
                'New Orleans':'NOR'    ,    'Saints'    :'NOR',
                'NY Giants':'NYG'      ,    'Giants'    :'NYG',
                'NY Jets':'NYJ'        ,    'Jets'      :'NYJ',
                'Oakland':'RAI'        ,    'Raiders'   :'RAI',
                'Philadelphia':'PHI'   ,    'Eagles'    :'PHI',
                'Pittsburgh':'PIT'     ,    'Steelers'  :'PIT',
                'San Diego':'SDG'      ,    'Chargers'  :'SDG',
                'San Francisco':'SFO'  ,    '49ers'     :'SFO',
                'Seattle':'SEA'        ,    'Seahawks'  :'SEA',
                'Tampa Bay':'TAM'      ,    'Buccaneers':'TAM',
                'Tennessee':'OTI'      ,    'Titans'    :'OTI',
                'Washington':'WAS'     ,    'Redskins'  :'WAS'
                }



# build list of all bye weeks
bye_table = {}
for year in range(2012,2017):
    bye_file = '/Users/wboag/projects/fantasy/data/%d/meta/nfl-schedule-byes.php' % year
    byes = build_bye_table(bye_file)
    bye_table[str(year)] = byes



def main():

    team = 'NWE'
    team_week = 8

    real_week = team_to_real_week('2016', team, team_week)

    print 'team:      ', team
    print 'team week: ', team_week
    print 'real weel: ', real_week





if __name__ == '__main__':
    main()


