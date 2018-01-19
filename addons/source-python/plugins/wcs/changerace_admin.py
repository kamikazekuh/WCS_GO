import os
from players.helpers import index_from_userid, playerinfo_from_userid, index_from_playerinfo, userid_from_index, edict_from_userid
from players.entity import Player
from configobj import ConfigObj
from commands.server import ServerCommand
from commands.say import SayCommand
from commands.client import ClientCommand
from players.helpers import index_from_userid, playerinfo_from_userid, index_from_playerinfo, userid_from_index, edict_from_userid
from players.entity import Player
from events import Event
from menus import SimpleMenu
from menus import SimpleOption
from menus import PagedOption
from menus import Text
from filters.players import PlayerIter
from menus import PagedMenu
from cvars import ConVar
from configobj import ConfigObj
from listeners import OnConVarChanged
from paths import PLUGIN_PATH
import wcs
from wcs import changerace
import core

global chosen_player
chosen_player = 0
global cats
global cat_to_change_to
cats = 0
categories_on = ConVar('wcs_activate_categories')
if categories_on.get_string() == "1":
	cats = os.path.join(PLUGIN_PATH+'/wcs', 'categories', 'categories.ini')
	cats = ConfigObj(cats)
	
unassigned_cat = ConVar('wcs_unassigned_category')

@OnConVarChanged
def on_convar_changed(convar, old_value):
	if categories_on.get_int() == 1:
		global cats
		cats = os.path.join(PLUGIN_PATH+'/wcs', 'categories', 'categories.ini')
		cats = ConfigObj(cats)


def wcsadmin_changerace_menu_build(menu, index):
	menu.clear()
	for player in PlayerIter():
		option = PagedOption('%s' % player.name, player)
		menu.append(option)
			
def wcsadmin_changerace_menu_select(menu, index, choice):
	player_entity = choice.value
	global chosen_player
	chosen_player = player_entity.userid
	userid = userid_from_index(index)
	if categories_on.get_int() == 1:
		doCommand_cats(userid)
	if categories_on.get_int() == 0:
		doCommandChangerace(userid)
	
	
def changerace_menu_cats_build(menu, index):
	menu.clear()
	allcats = get_cats()
	for cat in allcats:
		option = PagedOption('%s' % str(cats[cat]['name']), cat)
		menu.append(option)
	if unassigned_cat.get_int() == 1:
		option = PagedOption('Unassigned Races', 'unassigned')
		menu.append(option)
		
def changerace_menu_build(menu, index):
	global cat_to_change_to
	races = wcs.wcs.racedb.getAll()
	menu.clear()
	player_entity = Player(index)
	userid = chosen_player
	allraces = races.keys()
	for number, race in enumerate(allraces):
		if cat_to_change_to == 0:
			player = wcs.wcs.getPlayer(userid)
			level = wcs.wcs._getRace(player.player.UserID, race, userid).level
			raceinfo = wcs.wcs.racedb.getRace(race)
			nol = int(raceinfo['numberoflevels'])
			nos = int(raceinfo['numberofskills'])
			max_level = nol * nos
			level_buffer = level
			if level_buffer > max_level:
				level_buffer = max_level
			team = player_entity.team
			if wcs.wcs.showracelevel:
				level = wcs.wcs._getRace(player.player.UserID, race, userid).level
			if level > 0:
				option = PagedOption('%s - [%s/%s]' % (str(race), str(level_buffer),str(max_level)), race)
				menu.append(option)
			else:
				option = PagedOption('%s' % str(race), race)
				menu.append(option)				
		else:
			if not 'category' in races[race]:
				races[race]['category'] = 'unassigned'
			if 'category' in races[race]:
				if races[race]['category'] == "0" or races[race]['category'] == "":
					races[race]['category'] = 'unassigned'
			if cat_to_change_to in str(races[race]['category']):
				player = wcs.wcs.getPlayer(userid)
				level = wcs.wcs._getRace(player.player.UserID, race, userid).level
				raceinfo = wcs.wcs.racedb.getRace(race)
				nol = int(raceinfo['numberoflevels'])
				nos = int(raceinfo['numberofskills'])
				max_level = nol * nos
				level_buffer = level
				if level_buffer > max_level:
					level_buffer = max_level
				team = player_entity.team
				if wcs.wcs.showracelevel:
					level = wcs.wcs._getRace(player.player.UserID, race, userid).level
				if level > 0:
					option = PagedOption('%s - [%s/%s]' % (str(race), str(level_buffer),str(max_level)), race)
					menu.append(option)
				else:
					option = PagedOption('%s' % str(race), race)
					menu.append(option)				
	
	
def changerace_menu_select(menu, index, choice):
	userid = chosen_player
	player = wcs.wcs.getPlayer(userid)
	player.changeRace(choice.value,True,'admin')

def changerace_menu_cats_select(menu, index, choice):
	userid = userid_from_index(index)
	doCommandChangerace(userid, choice.value)
	
def doCommandChangerace(userid,value=0):
	global cat_to_change_to
	if value == 0:
		cat_to_change_to = 0
		index = index_from_userid(userid)
		races = wcs.wcs.racedb.getAll()
		allraces = races.keys()
		if len(allraces):
			changerace_menu = PagedMenu(title='Choose a race',build_callback=changerace_menu_build, select_callback=changerace_menu_select)
			if categories_on.get_int() == 1:
				changerace_menu.parent_menu = changerace_menu_cats
			changerace_menu.send(index)
	else:
		cat_to_change_to = value
		index = index_from_userid(userid)
		races = wcs.wcs.racedb.getAll()
		allraces = races.keys()
		if len(allraces):
			changerace_menu = PagedMenu(title='Choose a race',build_callback=changerace_menu_build, select_callback=changerace_menu_select,parent_menu=changerace_menu_cats)
			changerace_menu.send(index)	


changerace_menu_cats = PagedMenu(title='Choose a category', build_callback=changerace_menu_cats_build, select_callback=changerace_menu_cats_select)
	
def doCommand_cats(userid):
	index = index_from_userid(userid)
	allcats = get_cats()
	races = wcs.wcs.racedb.getAll()
	if len(allcats):
		changerace_menu_cats.send(index)
		
def get_cats():
	cat_list = []
	for category in cats:
		cat_list.append(category)
	return cat_list
		
def doCommand(userid):
	index = index_from_userid(userid)
	wcsadmin_changerace_menu = PagedMenu(title='Choose a player', build_callback=wcsadmin_changerace_menu_build, select_callback=wcsadmin_changerace_menu_select)
	wcsadmin_changerace_menu.send(index)