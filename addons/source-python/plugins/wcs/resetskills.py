import wcs
from listeners.tick import Delay
from players.helpers import index_from_userid, playerinfo_from_userid, index_from_playerinfo, userid_from_index, edict_from_userid
from players.entity import Player

resetskills = {}

def resetskills_dict(userid):
	resetskills[userid] = 0

def doCommand(userid):
	player_entity = Player(index_from_userid(userid))
	if userid not in resetskills:
		resetskills[userid] = 0
	if resetskills[userid] == 1 or player_entity.dead:
		player_entity.client_command("kill", True)
		race = wcs.wcs.wcsplayers[userid].currace
		raceinfo = wcs.wcs.racedb.getRace(race)
		level = wcs.wcs.wcsplayers[userid].all_races[race]['level']
		unused = wcs.wcs.wcsplayers[userid].all_races[race]['unused']
		nol = raceinfo['numberoflevels']
		nos = int(raceinfo['numberofskills'])
		if ('|') in nol:
			nol = nol.split('|')
		if len(nol) == 1:
			maxunused = int(nol) * nos
		else:
			maxunused = 0
			for x in nol:
				maxunused += int(x)

		v = 0
		for x in wcs.wcs.wcsplayers[userid].all_races[race]['skills'].split('|'):
			v += int(x)
		unused += v
		if unused > maxunused:
			unused = maxunused
		print(unused)
			
		skills = []
		for x in range(1,10):
			skill = 'skill'+str(x)
			if skill in wcs.wcs.racedb.races[race]:
				skills.append('0')
		skillst = '|'.join(skills)
		
		wcs.wcs.wcsplayers[userid].all_races[race]['unused'] = unused
		wcs.wcs.wcsplayers[userid].skills = skillst
		wcs.wcs.wcsplayers[userid].all_races[race]['skills'] = skillst
		wcs.wcs.wcsplayers[userid].save()

		wcs.wcs.tell(userid, "\x04[WCS] \x05Your skills has been reset. Type \x04'spendskills' \x05to spend your \x04%s \x05unused skill points." % wcs.wcs.wcsplayers[userid].all_races[race]['unused'])
	else:
		resetskills[userid] = 1
		wcs.wcs.tell(userid, '\x04[WCS] \x05Type \x04resetskills \x05again to continue. You will \x04die!')
		Delay(3.0, resetskills_dict, (userid,))
