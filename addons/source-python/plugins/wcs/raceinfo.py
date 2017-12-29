from players.entity import Player
from players.helpers import index_from_userid, playerinfo_from_userid, index_from_playerinfo, userid_from_index
from menus import SimpleMenu
from menus import SimpleOption
from menus import PagedOption

from menus import Text
from messages import SayText2
import wcs
from wcs.extensions import PagedMenu


def raceinfo_menu_build(menu, index):
	menu.clear()
	races = wcs.wcs.racedb.getAll()
	userid = userid_from_index(index)
	player_entity = Player(index)
	allraces = races.keys()
	for number, race in enumerate(allraces):
		player = wcs.wcs.getPlayer(userid)
		level = wcs.wcs._getRace(player.player.UserID, race, userid).level
		raceinfo = wcs.wcs.racedb.getRace(race)
		option = PagedOption('%s' % str(race), race)
		menu.append(option)
		

	
def raceinfo_menu_select(menu, index, choice):
	race = choice.value
	raceinfo = wcs.wcs.racedb.getRace(race)
	required = raceinfo['required']
	maximum = raceinfo['maximum']
	allowonly = raceinfo['allowonly']
	desc = raceinfo['desc']
	skillnames = raceinfo['skillnames'].split('|')
	skilldesc = raceinfo['skilldescr'].split('|')
	numberofskills = int(raceinfo['numberofskills'])-1
	
	raceinfo_race_menu = PagedMenu(title='Raceinfo - %s' % race,previous_menu=menu)
	raceinfo_race_menu.append(Text('Required level: %s' % required))
	raceinfo_race_menu.append(Text('Maximum level: %s' % maximum))
	if allowonly:
		raceinfo_race_menu.append(Text('<Private Race>'))
	if desc:
		raceinfo_race_menu.append(Text('Description: %s' % desc))
	raceinfo_race_menu.append(Text('Skills:'))
	x = 0
	while x <= numberofskills:
		raceinfo_race_menu.append(PagedOption('%s' % skillnames[x], value=None, highlight=True, selectable=False))
		#raceinfo_race_menu.append(Text('o %s' % skillnames[x]))
		print(skilldesc[x])
		v = str(skilldesc[x]).split('+')
		print(v)
		raceinfo_race_menu.append(Text('%s' % v[0]))
		for y in v[1:]:
			raceinfo_race_menu.append(Text('%s' % y))
		x +=1
	raceinfo_race_menu.send(index)

def doCommand(userid):
	index = index_from_userid(userid)
	races = wcs.wcs.racedb.getAll()
	allraces = races.keys()
	if len(allraces):
		raceinfo_menu = PagedMenu(title='Raceinfo Menu',build_callback=raceinfo_menu_build, select_callback=raceinfo_menu_select)
		raceinfo_menu.send(index)