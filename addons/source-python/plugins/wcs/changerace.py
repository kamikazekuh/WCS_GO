from players.entity import Player
from players.helpers import index_from_userid, playerinfo_from_userid, index_from_playerinfo, userid_from_index
from menus import SimpleMenu
from menus import SimpleOption
from menus import PagedOption
from menus import Text
import wcs
from wcs import config
from menus import PagedMenu
from cvars import ConVar
from configobj import ConfigObj
from listeners import OnConVarChanged
import os
from paths import PLUGIN_PATH
import core
listofargs = {}
popups = []

global cats
global cat_to_change_to
global race_arg
race_arg = ""
cats = 0
if config.coredata['categories'] == "1":
	cats = os.path.join(PLUGIN_PATH+'/wcs', 'categories', 'categories.ini')
	cats = ConfigObj(cats)

unassigned_cat = ConVar('wcs_unassigned_category')
	
@OnConVarChanged
def on_convar_changed(convar, old_value):
	if config.coredata['categories'] == 1:
		global cats
		cats = os.path.join(PLUGIN_PATH+'/wcs', 'categories', 'categories.ini')
		cats = ConfigObj(cats)
		
	
def HowChange(userid,args=0):
	if args:
		if config.coredata['changerace_racename'] == 1:
			doRacename(userid,args)
		else:
			if config.coredata['categories'] == 1:
				doCommand_cats(userid)
			elif config.coredata['categories'] == 0:
				doCommand(userid)			
	else:
		if config.coredata['categories'] == 1:
			doCommand_cats(userid)
		elif config.coredata['categories'] == 0:
			doCommand(userid)
		
def changerace_menu_build(menu, index):
	global cat_to_change_to
	races = wcs.wcs.racedb.getAll()
	menu.clear()
	userid = userid_from_index(index)
	player_entity = Player(index)
	allraces = races.keys()
	for number, race in enumerate(allraces):
		if cat_to_change_to == 0:
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
				if config.coredata['showracelevel']:
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
		else:
			if not 'category' in races[race]:
				races[race]['category'] = 'unassigned'
			if 'category' in races[race]:
				if races[race]['category'] == "0" or races[race]['category'] == "":
					races[race]['category'] = 'unassigned'
			if cat_to_change_to in str(races[race]['category']):
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
					if config.coredata['showracelevel']:
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
						if config.coredata['showracelevel']:
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
		
def doCommand(userid,value=0):
	global cat_to_change_to
	if value == 0:
		cat_to_change_to = 0
		index = index_from_userid(userid)
		races = wcs.wcs.racedb.getAll()
		allraces = races.keys()
		if len(allraces):
			changerace_menu = PagedMenu(title='Changerace Menu',build_callback=changerace_menu_build, select_callback=changerace_menu_select)
			if config.coredata['categories'] == 1:
				changerace_menu.parent_menu = changerace_menu_cats
			changerace_menu.send(index)
	else:
		cat_to_change_to = value
		index = index_from_userid(userid)
		index = index_from_userid(userid)
		races = wcs.wcs.racedb.getAll()
		allraces = races.keys()
		if len(allraces):
			changerace_menu = PagedMenu(title='Changerace Menu',build_callback=changerace_menu_build, select_callback=changerace_menu_select,parent_menu=changerace_menu_cats)
			changerace_menu.send(index)		
		
		
		
def changerace_menu_cats_build(menu, index):
	menu.clear()
	allcats = get_cats()
	for cat in allcats:
		option = PagedOption('%s' % str(cats[cat]['name']), cat)
		menu.append(option)
	if unassigned_cat.get_int() == 1:
		option = PagedOption('Unassigned Races', 'unassigned')
		menu.append(option)

def changerace_menu_cats_select(menu, index, choice):
	userid = userid_from_index(index)
	doCommand(userid, choice.value)	
		
changerace_menu_cats = PagedMenu(title='Race Categories', build_callback=changerace_menu_cats_build, select_callback=changerace_menu_cats_select)

def get_cats():
	cat_list = []
	for category in cats:
		cat_list.append(category)
	return cat_list
		
def doCommand_cats(userid):
	index = index_from_userid(userid)
	allcats = get_cats()
	races = wcs.wcs.racedb.getAll()
	if len(allcats):
		changerace_menu_cats.send(index)
		
def changerace_racename_select(menu, index, choice):
	userid = userid_from_index(index)
	player = wcs.wcs.getPlayer(userid)
	player.changeRace(choice.value)		
		
def changerace_racename_build(menu, index):
	races = wcs.wcs.racedb.getAll()
	menu.clear()
	userid = userid_from_index(index)
	player_entity = Player(index)
	allraces = races.keys()
	for number, race in enumerate(allraces):
		if race_arg.lower() in race.lower():
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
				if config.coredata['showracelevel']:
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
					if config.coredata['showracelevel']:
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

		
		
changerace_racename_menu = PagedMenu(title='Changerace Menu',build_callback=changerace_racename_build,select_callback=changerace_racename_select)

def find_races(args):
	found_list = []
	races = wcs.wcs.racedb.getAll()
	allraces = races.keys()	
	for number, race in enumerate(allraces):
		if args.lower() in race.lower():
			found_list.append(race)
	if len(found_list) != 0:
		return found_list
	else:
		return -1
		
		
		
def doRacename(userid,args):
	index = index_from_userid(userid)
	races_found = find_races(args)
	if races_found != -1:
		global race_arg
		race_arg = args
		changerace_racename_menu.send(index)
	
	
		
def canUse(userid, race):
	raceinfo = wcs.wcs.racedb.getRace(race)
	player_entity = Player(index_from_userid(userid))
	if not wcs.wcs.curmap in raceinfo['restrictmap'].split('|'):
		admins = raceinfo['allowonly'].split('|')
		if (len(admins) and not admins[0]) or (player_entity.steamid in admins) or ('ADMINS' in admins):
			team = int(player_entity.team)
			if not raceinfo['restrictteam'] or not raceinfo['restrictteam'] == 0 or not int(raceinfo['restrictteam']) == team:
				totallevel = wcs.wcs.getPlayer(userid).player.totallevel
				if totallevel >= int(raceinfo['required']):
					if int(raceinfo['maximum']) and totallevel > int(raceinfo['maximum']):
						return 2
					return 0
				return 3
			return 4
		return 5
	return 6		

		

