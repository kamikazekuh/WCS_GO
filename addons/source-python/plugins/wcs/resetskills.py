import wcs
from listeners.tick import Delay
from players.helpers import index_from_userid, playerinfo_from_userid, index_from_playerinfo, userid_from_index, edict_from_userid
from players.entity import Player

resetskills = {}

def resetskills_dict(userid):
	resetskills[userid] = 0

def doCommand(userid):
	player = wcs.wcs.getPlayer(userid)
	player_entity = Player(index_from_userid(userid))
	if userid not in resetskills:
		resetskills[userid] = 0
	if resetskills[userid] == 1 or player_entity.dead:
		if filter(lambda x: int(x), player.race.skills.split('|')):
			player_entity.client_command("kill", True)
			'''skills = player.race.skills.split('|')'''
			race = player.player.currace
			raceinfo = wcs.wcs.racedb.getRace(race)
			skills = int(raceinfo['numberofskills'])
			levels = int(raceinfo['numberoflevels'])

			level = player.race.level
			unused = player.race.unused

			maxunused = skills*levels
			v = 0
			for x in player.race.skills.split('|'):
				v += int(x)
			unused += v

			if maxunused <= unused:
				playerunused = maxunused
			else:
				playerunused = unused

			'''for x in skills:
				levels += int(x)'''

			player.race.unused = playerunused
			player.race.skills = ''
			player.race.save()

			player.race.refresh()

			wcs.wcs.tell(userid, "\x04[WCS] \x05Your skills has been reset. Type \x04'spendskills' \x05to spend your \x04%s \x05unused skill points." % player.race.unused)
	else:
		resetskills[userid] = 1
		wcs.wcs.tell(userid, '\x04[WCS] \x05Type \x04resetskills \x05again to continue. You will \x04die!')
		Delay(3.0, resetskills_dict, (userid,))
	
