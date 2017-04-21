

import os
import re

from player import Player
import search_name 



class RosterException(Exception):
    pass


fantasy_positions = ['QB','WR1','WR2','RB1','RB2','TE','FLEX','K',
                     'DB1','DB2','LB1','LB2','DL1','DL2']



# e.g. if someone is an OLB, then they can be either LB1 or LB2
position_casts = {
                     'QB' :set(['QB']),
                     'WR' :set(['WR1','WR2','FLEX']),
                     'RB' :set(['RB1','RB2','FLEX']),
                     'TE' :set(['TE','FLEX']),
                     'ILB':set(['LB1','LB2']),
                     'OLB':set(['LB1', 'LB2', 'DL1','DL2']),
                     'LB' :set(['LB1','LB2']),
                     'CB' :set(['DB1','DB2']),
                     'DB' :set(['DB1','DB2']),
                     'S'  :set(['DB1','DB2']),
                     'SS' :set(['DB1','DB2']),
                     'FS' :set(['DB1','DB2']),
                     'K'  :set(['K']),
                     'DE' :set(['DL1','DL2']),
                     'DL' :set(['DL1','DL2']),
                     'DT' :set(['DL1','DL2']),
                 }

# reduce set of positions
simple_positions = {
                     'QB' :'QB',
                     'WR' :'WR',
                     'RB' :'RB',
                     'TE' :'TE',
                     'ILB':'LB',
                     'OLB':'LB',
                     'LB' :'LB',
                     'CB' :'DB',
                     'DB' :'DB',
                     'S'  :'DB',
                     'SS' :'DB',
                     'FS' :'DB',
                     'K'  :'K' ,
                     'DE' :'DL',
                     'DL' :'DL',
                     'DT' :'DL',
                 }



class FantasyTeam:

    def __init__(self, year):
        # active roster + bench
        self._size = 20

        # all players you own
        self._players = [] 

        # active players
        self._active = {position:None for position in fantasy_positions}

        # you need to know this for bye week purposes (among other things)
        self._year = year


    def __resolve_id(self, pid):
        for p in self._players:
            if p.id() == pid:
                return p
        raise RosterException('player %s not on team' % pid)
    
    def score(self, week, verbose=False):
        s = 0.0

        for position in fantasy_positions:
            player = self._active[position]

            if player:
                val  = player.score(week)
                name = player.name()
            else:
                val  = 0.0
                name = 'N/A'

            s += val
            if verbose:
                print '%4s: %-20s -- %6.2f' % (position,name,val)

        return s


    def add_player(self, player):
        # years must agree
        if self._year != player._year:
            msg = 'cannot add player from %s to team in %s'%(player._year,self._year)
            raise RosterException(mg)
        
        # cannot exceed roster size
        if len(self._players) >= self._size:
            raise RosterException('team full. cannot add more players')

        # make sure you dont already own this player
        players = [p.id() for p in self._players]
        if player.id() in players:
            raise RosterException('you already own player %s'%player.name())

        self._players.append(player)


    def drop_player(self, player):
        if player in self._players:
            # if active, then deactivate
            active_players = self._active.items()
            for pos,p in active_players:
                if p and (p.id() == player.id()):
                    self._active[pos] = None

            ind = self._players.index(player)
            del self._players[ind]
        else:
            raise RosterException('you do not own player %s'%player.name())


    def set_roster(self, position, player):
        # is this a real position?
        if position not in fantasy_positions:
            raise RosterException('%s is not a valid position'%position)

        # e.g. QB cannot play WR
        ff_positions = position_casts[player.position()]
        if position not in ff_positions:
            if not is_position_exception(player, position):
                pp = player.position()
                raise RosterException('%s player cannot play %s' % (pp,position))

        # player cannot already be active
        actives = [p.id() for p in self._active.values() if p]
        if player.id() in actives:
            raise RosterException('player %s is already active'%player.name())

        # you need to own the player
        if player not in self._players:
            raise RosterException('you do not own this player')

        self._active[position] = player


    def deactivate_player(self, position):
        # is this a real position?
        if position not in fantasy_positions:
            raise RosterException('%s is not a valid position'%position)

        self._active[position] = None


    def load_from_file(self, roster_file):
        with open(roster_file, 'r') as f:
            text = f.read().strip()

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(base_dir, 'data')

        roster = {pos:None for pos in fantasy_positions}
        roster['bench'] = []

        # fill spots by resolving .roster to list of player objects
        regex = '(.+) \((.+)\)'
        for line in text.split('\n'):
            toks = line.split(':')
            if toks[1].strip():
                match = re.search(regex, toks[1].strip())
                name,teams_str = match.groups()
                teams = teams_str.split('/')

                #print name
                #print teams

                pid = search_name.query_name(name, teams=teams, position=None, year=self._year)
                #print pid

                player_file = os.path.join(data_dir, self._year, 'raw', 'players', pid)
                p = Player(player_file)
                #print player_file
                #print p
                #print

                position = toks[0]
                if position == 'bench':
                    roster['bench'].append(p)
                else:
                    roster[position] = p
                

        # add all players & active players to their specified positions
        for pos in fantasy_positions:
            # Taco sometimes forgets to set his lineup
            if roster[pos]:
                self.add_player(roster[pos])
                self.set_roster(pos, roster[pos])
        for player in roster['bench']:
            self.add_player(player)


    def players(self):
        return self._players


    def __str__(self):
        ret = []
        players = list(self._players)
        for pos in fantasy_positions:
            if self._active[pos]:
                p = self._active[pos]
                #print pos
                #print self._active
                players.remove(self._active[pos])
            else:
                p = ''
            ret.append('%5s: %s' % (pos,p))
        for p in players:
            ret.append('bench: %s' % p)
        return '\n'.join(ret)



def is_position_exception(player, position):
    # FML
    # fuck you, honey badger >:(
    name = player.name()
    if name == 'Kurt Coleman' and position.startswith('DB'): return True
    if name == 'Cameron Wake' and position.startswith('DL'): return True
    if name == 'Melvin Ingram' and position.startswith('LB'): return True
    return False




def manual_create():

    p1 = FantasyTeam('2016')


    #####
    tom_brady_f = '/Users/wboag/projects/fantasy/data/2016/raw/players/bradto00'
    tom_brady = Player(tom_brady_f)

    p1.add_player(tom_brady)
    p1.set_roster('QB', tom_brady)


    #####
    julian_edelman_f = '/Users/wboag/projects/fantasy/data/2016/raw/players/edelju00'
    julian_edelman = Player(julian_edelman_f)

    p1.add_player(julian_edelman)
    p1.set_roster('WR1', julian_edelman)


    #####
    danny_amendola_f = '/Users/wboag/projects/fantasy/data/2016/raw/players/amenda00'
    danny_amendola = Player(danny_amendola_f)

    p1.add_player(danny_amendola)
    p1.set_roster('WR2', danny_amendola)


    #####
    james_white_f = '/Users/wboag/projects/fantasy/data/2016/raw/players/whitja02'
    james_white = Player(james_white_f)

    p1.add_player(james_white)
    p1.set_roster('RB2', james_white)


    #####
    develin_f = '/Users/wboag/projects/fantasy/data/2016/raw/players/deveja00'
    develin = Player(develin_f)

    p1.add_player(develin)
    #p1.set_roster('RB2', develin)


    #####
    blount_f = '/Users/wboag/projects/fantasy/data/2016/raw/players/bloule00'
    blount = Player(blount_f)

    p1.add_player(blount)
    p1.set_roster('RB1', blount)


    #####
    marty_f = '/Users/wboag/projects/fantasy/data/2016/raw/players/bennma00'
    marty = Player(marty_f)

    p1.add_player(marty)
    p1.set_roster('TE', marty)


    #####
    hightower_f = '/Users/wboag/projects/fantasy/data/2016/raw/players/highdo01'
    hightower = Player(hightower_f)

    p1.add_player(hightower)
    p1.set_roster('LB1', hightower)


    #####
    roberts_f = '/Users/wboag/projects/fantasy/data/2016/raw/players/robeel00'
    roberts = Player(roberts_f)

    p1.add_player(roberts)
    p1.set_roster('LB2', roberts)


    #####
    dmac_f = '/Users/wboag/projects/fantasy/data/2016/raw/players/mccode99'
    dmac = Player(dmac_f)

    p1.add_player(dmac)
    p1.set_roster('DB1', dmac)


    #####
    logan_ryan_f = '/Users/wboag/projects/fantasy/data/2016/raw/players/ryanlo00'
    logan_ryan = Player(logan_ryan_f)

    p1.add_player(logan_ryan)
    p1.set_roster('DB2', logan_ryan)


    #####
    butler_f = '/Users/wboag/projects/fantasy/data/2016/raw/players/butlma01'
    butler = Player(butler_f)

    p1.add_player(butler)
    p1.set_roster('DB2', butler)


    #####
    hogan_f = '/Users/wboag/projects/fantasy/data/2016/raw/players/hogach00'
    hogan = Player(hogan_f)

    p1.add_player(hogan)
    p1.set_roster('FLEX', hogan)


    #####
    ghost_f = '/Users/wboag/projects/fantasy/data/2016/raw/players/gostst20'
    ghost = Player(ghost_f)

    p1.add_player(ghost)
    p1.set_roster('K', ghost)


    #####
    nink_f = '/Users/wboag/projects/fantasy/data/2016/raw/players/ninkro20'
    nink = Player(nink_f)

    p1.add_player(nink)
    p1.set_roster('DL1', nink)


    #####
    sheard_f = '/Users/wboag/projects/fantasy/data/2016/raw/players/sheaja00'
    sheard = Player(sheard_f)

    p1.add_player(sheard)
    p1.set_roster('DL2', sheard)


    print p1.score(6, verbose=True)



def file_create():

    p1 = FantasyTeam('2016')

    team_file = '/Users/wboag/projects/fantasy/leagues/pink-stripes/willie.roster'
    p1.load_from_file(team_file)

    #print p1
    print p1.score(6, verbose=True)



def main():

    file_create()
    #manual_create()



if __name__ == '__main__':
    main()

