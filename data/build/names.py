

import sys
import os
import urllib2
import re
from collections import defaultdict



def main():

    # TODO make this a command line arg
    year = sys.argv[1]

    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    base_dir = os.path.join(parent_dir, year)

    base_url = 'http://www.pro-football-reference.com/years/%s' % year
    pages = ['passing', 'receiving', 'rushing', 'defense', 'kicking']

    print year
    urls = set()

    # keep track of the occasional instances of two players with same name
    pids = defaultdict(set)

    # ensure there is a place to output stats
    stat_dir = os.path.join(base_dir, 'raw')
    if not os.path.exists(stat_dir):
        os.mkdir(stat_dir)
    stat_dir = os.path.join(stat_dir, 'players')
    if not os.path.exists(stat_dir):
        os.mkdir(stat_dir)

    for page in pages:

        # read data
        filename = os.path.join(base_dir, 'meta', '%s.htm' % page)
        with open(filename, 'r') as f:
            text = f.read()

        regex = 'data-append-csv="([^"]+)" data-stat="player" csk="([^"]+)" ><a href="/([^>]+).htm">'
        matches = re.findall(regex, text)

        for match in matches:
            #print match
            pid,name_str,path = match
            toks = name_str.split(',')
            name = '%s %s' % (toks[1], toks[0])

            pids[name].add(pid)

            #filename = os.path.join(base_dir,'raw', '%s' % name.replace(' ','_').lower())
            filename = os.path.join(stat_dir, '%s' % pid.lower())
            if os.path.exists(filename): continue

            url = 'http://www.pro-football-reference.com/%s/gamelog/%s' % (path,year)
            urls.add( (pid,name,url,filename) )

    '''
    for pid,names in sorted(pids.items(), key=lambda t:len(t[1])):
        print pid, names
    exit()
    '''

    # request data
    for pid,name,url,filename in sorted(urls):
        print '\t%-20s (%-8s)' % (name,pid)

        if os.path.exists(filename):
            continue

        response = urllib2.urlopen(url)
        r = response.read()

        check='We apologize, but we could not find the page requested by your device.'
        if check in r:
            print '\t\tFAIL'
            continue

        # output reponse to file
        with open(filename, "w") as f:
            f.write(r)

    print


    # Get list of all players for that year
    # Retrieve that player's game log for that year


    # http://www.pro-football-reference.com/players/J/JackSt00/gamelog/2008/

    # save translations
    pids = dict(pids)





if __name__ == '__main__':
    main()


