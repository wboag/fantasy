

import sys
import urllib2
import os
import re



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
                #'Houston':'HTX'
                                            'Texans'    :'HTX',
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
                                            'Oilers'    :'OTI',
                'Washington':'WAS'     ,    'Redskins'  :'WAS'
                }



def main():

    year = sys.argv[1]

    # where to store data
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    year_dir = os.path.join(parent_dir, year)
    if not os.path.exists(year_dir):
        os.mkdir(year_dir)
    meta_dir = os.path.join(year_dir, 'meta')
    if not os.path.exists(meta_dir):
        os.mkdir(meta_dir)

    # store all byes
    byes = {}

    # Get week 1 URL to get all weeks present from the season
    week1_url = 'http://www.nfl.com/schedules/%s/REG1' % year
    #'''
    response = urllib2.urlopen(week1_url)
    r = response.read()
    #'''
    '''
    with open('REG1','r') as f:
        r = f.read()
    '''

    byes[1] = get_byes(week1_url)

    # week numbers (because 1993 had 18 weeks & 2 byes)
    week_regex = '<li  role="listitem" class="page-nav-listitem " data-value=""><a href="http://www.nfl.com/schedules/%s/REG\d+" target="">(\d+)</a></li>' % year
    matches = re.findall(week_regex, r)
    for week_s in matches:
        print week_s

        # build query url
        week = int(week_s)
        url = 'http://www.nfl.com/schedules/%s/REG%d' % (year,week)

        # get all teams on bye this week
        teams = get_byes(url)

        # store answer
        byes[week] = teams

    # write byes out to file
    outfile = os.path.join(meta_dir, '%s.byes'%year)
    with open(outfile, 'w') as f:
        for week,teams in sorted(byes.items()):
            print >>f, week, ' '.join(teams)
        



def get_byes(url):
    section_regex = 'BYE WEEK:(.*)</span>\s+<span class="schedules-header-flexible-schedule">'

    '''
    filename = url.split('/')[-1]
    with open(filename,'r') as f:
        r = f.read()
    '''
    response = urllib2.urlopen(url)
    r = response.read()

    section_match = re.search(section_regex, r, flags=re.DOTALL)
    byes_s = section_match.groups()[0]

    byes_regex = '<a target="_top" href="/teams/profile\?team=(\w+)">([a-zA-Z].+)</a>'
    bye_teams = re.findall(byes_regex, byes_s)

    # handles the weird shit like ('HOU','Oilers') -> 'OTI'
    teams = map(resolve_team, bye_teams)

    return teams



def resolve_team(team_info):
    area,name = team_info
    if name in translations:
        return translations[name]
    print team_info






if __name__ == '__main__':
    main()


