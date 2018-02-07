from players.helpers import index_from_userid, playerinfo_from_userid, index_from_playerinfo, userid_from_index, edict_from_userid
from menus import SimpleMenu
from menus import SimpleOption
from menus import Text
from players.entity import Player
import wcs
import core

def doCommand(userid):
	index = index_from_userid(userid)
	userid = int(userid)
	race = wcs.wcs.wcsplayers[userid].currace
	skills = wcs.wcs.wcsplayers[userid].all_races[race]['skills'].split('|')
	names = wcs.wcs.racedb.races[race]['skillnames'].split('|')
	n = 0
	showskills = SimpleMenu(select_callback=showskills_select)
	showskills.append(Text('Your %s skills:' % race))
	showskills.append(Text('------------------------------'))
	while n < len(names):
		try:
			level = str(skills[n])
		except IndexError:
			level = 0
		name = str(names[n])
		n += 1
		showskills.append(SimpleOption(n, '%s : %s' % (str(name), str(level)), value=None, highlight=True, selectable=False))
	showskills.append(Text('------------------------------'))
	showskills.append(Text('Unused points: %s' % str(wcs.wcs.wcsplayers[userid].all_races[race]['unused'])))
	showskills.append(Text('------------------------------'))
	showskills.append(SimpleOption(8, 'Back',value='back',highlight=True,selectable=True))
	showskills.append(SimpleOption(9, 'Close', highlight=False))
	showskills.send(index)

	
def showskills_select(menu, index, choice):
	if choice.choice_index == 8:
		player=Player(index)
		player.client_command('wcs',server_side=True)