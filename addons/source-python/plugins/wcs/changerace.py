from players.entity import Player
from players.helpers import index_from_userid, playerinfo_from_userid, index_from_playerinfo, userid_from_index
from menus import SimpleMenu
from menus import SimpleOption
from menus import PagedOption
from menus import Text
from messages import SayText2
import wcs
from wcs.extensions import PagedMenu

listofargs = {}
popups = []
		
def HowChange(userid):
	#if wcs.wcs.racecategories:
		#raceCategories(userid)
	#else:
	doCommand(userid)
		
def changerace_menu_build(menu, index):
	menu.clear()
	races = wcs.wcs.racedb.getAll()
	userid = userid_from_index(index)
	player_entity = Player(index)
	allraces = races.keys()
	for number, race in enumerate(allraces):
		player = wcs.wcs.getPlayer(userid)
		level = wcs.wcs._getRace(player.player.UserID, race, userid).level
		v = canUse(userid, race)
		raceinfo = wcs.wcs.racedb.getRace(race)
		nol = int(raceinfo['numberoflevels'])
		nos = int(raceinfo['numberofskills'])
		max_level = nol * nos
		level_buffer = level
		if level_buffer > max_level:
			level_buffer = max_level
		team = player_entity.team
		if not v:
			if wcs.wcs.showracelevel:
				level = wcs.wcs._getRace(player.player.UserID, race, userid).level
			if level > 0:
				option = PagedOption('%s - [%s/%s]' % (str(race), str(level_buffer),str(max_level)), race)
				menu.append(option)
			else:
				option = PagedOption('%s' % str(race), race)
				menu.append(option)				
		elif v == 2:
			option = PagedOption('%s - Maximum level: %s' % (str(race), str(max_level)), race, highlight=False, selectable=False)
			menu.append(option)
		elif v == 3:
			option = PagedOption('%s - Minimum level: %s' % (str(race), str(raceinfo['required'])), race, highlight=False, selectable=False)
			menu.append(option)
		elif v == 4:
			if team in (2,3):
				option = PagedOption('%s - Restricted team %s' % (str(race), {2:'T',3:'CT'}[team]), race, highlight=False, selectable=False)
				menu.append(option)
			else:
				if wcs.wcs.showracelevel:
					level = wcs.wcs._getRace(player.player.UserID, race, userid).level
				if level > 0:
					option = PagedOption('%s - [%s/%s]' % (str(race), str(level_buffer),str(max_level)), race)
					menu.append(option)
				else:
					option = PagedOption('%s' % str(race), race)
					menu.append(option)	
		elif v == 5:
			option = PagedOption('%s - Private race' % str(race), race, highlight=False, selectable=False)
			menu.append(option)
		elif v == 6:
			option = PagedOption('%s - Restricted map: %s' % (str(race), wcs.wcs.curmap), race, highlight=False, selectable=False)
			menu.append(option)
		else:
			break
	
def changerace_menu_select(menu, index, choice):
	userid = userid_from_index(index)
	player = wcs.wcs.getPlayer(userid)
	player.changeRace(choice.value)
		
def doCommand(userid):
	index = index_from_userid(userid)
	races = wcs.wcs.racedb.getAll()
	allraces = races.keys()
	if len(allraces):
		changerace_menu = PagedMenu(title='Changerace Menu',build_callback=changerace_menu_build, select_callback=changerace_menu_select)
		changerace_menu.send(index)
		
def canUse(userid, race):
	raceinfo = wcs.wcs.racedb.getRace(race)
	player_entity = Player(index_from_userid(userid))
	if not wcs.wcs.curmap in raceinfo['restrictmap'].split('|'):
		admins = raceinfo['allowonly'].split('|')
		if (len(admins) and not admins[0]) or (player_entity.steamid in admins) or ('ADMINS' in admins):
			team = int(player_entity.team)
			if not raceinfo['restrictteam'] or not int(raceinfo['restrictteam']) == team:
				totallevel = wcs.wcs.getPlayer(userid).player.totallevel
				if totallevel >= int(raceinfo['required']):
					if int(raceinfo['maximum']) and totallevel > int(raceinfo['maximum']):
						return 2
					return 0
				return 3
			return 4
		return 5
	return 6
		
