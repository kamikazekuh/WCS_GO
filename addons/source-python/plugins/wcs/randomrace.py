from players.entity import Player
from players.helpers import index_from_userid, playerinfo_from_userid, index_from_playerinfo, userid_from_index
import wcs
import random
from commands.say import SayCommand
from commands.client import ClientCommand

@ClientCommand('randomrace')
@SayCommand('randomrace')
def _random_race(command, index, team=None):
	userid = userid_from_index(index)
	doCommand(userid)


def doCommand(userid):
	races = wcs.wcs.racedb.getAll()
	allraces = races.keys()
	for race in allraces:
		v = canUse(userid, race)
		if v == 0:
			allraces.remove(race)
	for race in allraces:
		v = canUse(userid, race)
		if v == 0:
			allraces.remove(race)
	print(allraces)
	change_to = random.choice(allraces)
	player = wcs.wcs.getPlayer(userid)
	player.changeRace(change_to)
	




def canUse(userid, race):
	player_entity = Player(index_from_userid(userid))
	raceinfo = wcs.wcs.racedb.getRace(race)
	totallevel = wcs.wcs.getPlayer(userid).player.totallevel
	if totallevel >= int(raceinfo['required']):
		return 1
	return 0