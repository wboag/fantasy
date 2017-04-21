

import sys
import os
import urllib2
import re
from collections import defaultdict



def main():

    # TODO make this a command line arg
    year = sys.argv[1]

    # where to store data
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    year_dir = os.path.join(parent_dir, year)
    if not os.path.exists(year_dir):
        os.mkdir(year_dir)
    base_dir = os.path.join(year_dir, 'raw')
    if not os.path.exists(base_dir):
        os.mkdir(base_dir)
    base_dir = os.path.join(base_dir, 'weekly')
    if not os.path.exists(base_dir):
        os.mkdir(base_dir)

    # QB
    print 'passing'
    for i in range(17):

        passing_dir = os.path.join(base_dir, 'passing')
        if not os.path.exists(passing_dir):
            os.mkdir(passing_dir)

        week = i + 1
        print '\t', week

        # don't get something we already have
        filename = os.path.join(passing_dir, 'week_%d.htm'%week)
        if os.path.exists(filename):
            continue

        url = 'http://www.pro-football-reference.com/play-index/pgl_finder.cgi?request=1&match=game&year_min=%s&year_max=%s&season_start=1&season_end=-1&age_min=0&age_max=99&game_type=A&league_id=&team_id=&opp_id=&game_num_min=0&game_num_max=99&week_num_min=%d&week_num_max=%d&game_day_of_week=&game_location=&game_result=&handedness=&is_active=&is_hof=&c1stat=pass_att&c1comp=gt&c1val=1&c2stat=&c2comp=gt&c2val=&c3stat=&c3comp=gt&c3val=&c4stat=&c4comp=gt&c4val=&order_by=pass_rating&from_link=1' % (year,year,week,week)

        response = urllib2.urlopen(url)
        r = response.read()

        with open(filename, 'w') as f:
            f.write(r)
    print



    print 'receiving'
    for i in range(17):

        passing_dir = os.path.join(base_dir, 'receiving')
        if not os.path.exists(passing_dir):
            os.mkdir(passing_dir)

        week = i + 1
        print '\t', week

        # don't get something we already have
        filename = os.path.join(passing_dir, 'week_%d.htm'%week)
        if os.path.exists(filename):
            continue

        url = 'http://www.pro-football-reference.com/play-index/pgl_finder.cgi?request=1&match=game&year_min=%s&year_max=%s&season_start=1&season_end=-1&age_min=0&age_max=99&game_type=A&league_id=&team_id=&opp_id=&game_num_min=0&game_num_max=99&week_num_min=%d&week_num_max=%d&game_day_of_week=&game_location=&game_result=&handedness=&is_active=&is_hof=&c1stat=rec&c1comp=gt&c1val=1&c2stat=&c2comp=gt&c2val=&c3stat=&c3comp=gt&c3val=&c4stat=&c4comp=gt&c4val=&order_by=rec_yds&from_link=1' % (year,year,week,week)

        response = urllib2.urlopen(url)
        r = response.read()

        with open(filename, 'w') as f:
            f.write(r)
    print




    print 'rushing'
    for i in range(17):

        passing_dir = os.path.join(base_dir, 'rushing')
        if not os.path.exists(passing_dir):
            os.mkdir(passing_dir)

        week = i + 1
        print '\t', week

        # don't get something we already have
        filename = os.path.join(passing_dir, 'week_%d.htm'%week)
        if os.path.exists(filename):
            continue

        url = 'http://www.pro-football-reference.com/play-index/pgl_finder.cgi?request=1&match=game&year_min=%s&year_max=%s&season_start=1&season_end=-1&age_min=0&age_max=99&game_type=A&league_id=&team_id=&opp_id=&game_num_min=0&game_num_max=99&week_num_min=%d&week_num_max=%d&game_day_of_week=&game_location=&game_result=&handedness=&is_active=&is_hof=&c1stat=rush_att&c1comp=gt&c1val=1&c2stat=&c2comp=gt&c2val=&c3stat=&c3comp=gt&c3val=&c4stat=&c4comp=gt&c4val=&order_by=rush_yds&from_link=1' % (year,year,week,week)

        response = urllib2.urlopen(url)
        r = response.read()

        with open(filename, 'w') as f:
            f.write(r)
    print




    print 'defense'
    for i in range(17):

        passing_dir = os.path.join(base_dir, 'defense')
        if not os.path.exists(passing_dir):
            os.mkdir(passing_dir)

        week = i + 1
        print '\t', week

        # don't get something we already have
        filename = os.path.join(passing_dir, 'week_%d.htm'%week)
        if os.path.exists(filename):
            continue

        url = 'http://www.pro-football-reference.com/play-index/pgl_finder.cgi?request=1&match=game&year_min=%s&year_max=%s&season_start=1&season_end=-1&age_min=0&age_max=99&game_type=A&league_id=&team_id=&opp_id=&game_num_min=0&game_num_max=99&week_num_min=%d&week_num_max=%d&game_day_of_week=&game_location=&game_result=&handedness=&is_active=&is_hof=&c1stat=tackles_solo&c1comp=gt&c1val=1&c2stat=&c2comp=gt&c2val=&c3stat=&c3comp=gt&c3val=&c4stat=&c4comp=gt&c4val=&order_by=sacks&from_link=1' % (year,year,week,week)

        response = urllib2.urlopen(url)
        r = response.read()

        with open(filename, 'w') as f:
            f.write(r)
    print




if __name__ == '__main__':
    main()


