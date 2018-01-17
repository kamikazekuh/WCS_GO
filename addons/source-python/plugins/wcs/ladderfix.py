from listeners import OnTick
from players.entity import Player
from filters.players import PlayerIter
from events import Event
from wcs import wcsgroup


ladder = {}


@Event('player_activate')
def player_activate(ev):
	ladder[ev['userid']] = 2

@OnTick
def tick_listener():
	for player in PlayerIter('all'):
		newval = player.move_type
		if player.userid in ladder:
			oldval = ladder[player.userid]
		else:
			ladder[player.userid] = {}
			oldval = 2		
		if oldval != newval:
			if newval == 2:
				if oldval == 9:
					if wcsgroup.getUser(player.userid,'gravity') != None:
						gravity = wcsgroup.getUser(player.userid, 'gravity')
					else:
						gravity = 1.0
					player.gravity = float(gravity)
					if wcsgroup.getUser(player.userid,'jetpack') != None:
						jetpack = int(wcsgroup.getUser(player.userid, 'jetpack'))
					else:
						jetpack = 0
					if jetpack == 1:
						player.set_jetpack(1)
		ladder[player.userid] = newval
		
