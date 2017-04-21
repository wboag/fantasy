

import sys
import os
import urllib2



def main():

    # TODO make this a command line arg
    year = sys.argv[1]

    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    base_dir = os.path.join(parent_dir, year)

    base_url = 'http://www.pro-football-reference.com/years/%s' % year
    pages = ['passing', 'receiving', 'rushing', 'defense', 'kicking']

    print year

    meta_dir = os.path.join(base_dir, 'meta')
    if not os.path.exists(meta_dir):
        os.mkdir(meta_dir)

    for page in pages:
        url = '%s/%s.htm' % (base_url,page)
        response = urllib2.urlopen(url)
        print '\t', url

        filename = os.path.join(meta_dir, '%s.htm' % page)

        # output reponse to file
        with open(filename, "w") as f:
            f.write(response.read())

    print

    # http://www.pro-football-reference.com/players/J/JackSt00/gamelog/2008/




if __name__ == '__main__':
    main()


