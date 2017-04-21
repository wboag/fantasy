

import os
import sys
import re
from collections import defaultdict

base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
code_dir = os.path.join(base_dir, 'code')
if code_dir not in sys.path:
    sys.path.append(code_dir)

from player import read_name, read_position, read_teams



def main():

    year = sys.argv[1]

    #  List of all IDs and their associated info
    ids = {}

    data_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    year_dir = os.path.join(data_dir, year)
    players_dir = os.path.join(year_dir, 'raw', 'players')

    # examine every player
    for pid in os.listdir(players_dir):
        #if pid != 'abduis00': continue

        try:
            #if pid != "o'shja00":continue
            print '\t', pid
            filename = os.path.join(players_dir, pid)
            with open(filename, 'r') as f:
                text = f.read()

            # extract useful information
            name     = read_name(text)
            position = read_position(text)
            teams    = ','.join(read_teams(text))

            # serialize
            info = '||'.join([name,position,teams])
            #print pid, '\t', info

            # save info
            ids[pid] = info
        except Exception, e:
            print e

    # save to file
    outfile = os.path.join(year_dir, 'meta', 'names_index')
    with open(outfile,'w') as f:
        for pid,info in ids.items():
            print >>f, pid, '\t', info






if __name__ == '__main__':
    main()


