from commands.say import SayCommand
from commands.client import ClientCommand
from players.helpers import index_from_userid, userid_from_index
from menus import SimpleMenu
from menus import Text
from menus import SimpleOption
from players.entity import Player
from decimal import Decimal
import wcs

race_dict = {}

def myinfo_select(menu, index, choice):
	if choice.choice_index == 8:
		doCommand2(userid_from_index(index))
		
def myinfo2_select(menu, index, choice):
	if choice.choice_index == 7:
		doCommand(userid_from_index(index))
		
def doCommand2(userid):
	player_entity = Player(index_from_userid(userid))
	available = available_races(userid)
	left = left_to_next(userid)
	all_count = all_races()
	perc = float(available)/(float(all_count)/100.0)
	perc = Decimal(perc)
	perc = round(perc,2)
	rank = wcs.wcs.wcsplayers[userid].get_rank()
	myinfo2_menu = SimpleMenu()
	myinfo2_menu.select_callback = myinfo2_select
	myinfo2_menu.append(Text('->1. %s' % player_entity.name))
	myinfo2_menu.append(Text('-'*25))
	myinfo2_menu.append(Text('Total level: %s' % str(wcs.wcs.wcsplayers[userid].totallevel)))
	myinfo2_menu.append(Text('-'*25))
	myinfo2_menu.append(Text('- WCS rank: %s' % rank[0]))
	myinfo2_menu.append(Text('- Levels to next race: %s' % left))
	myinfo2_menu.append(Text('- Races available: %s of %s' % (available, all_count)))
	myinfo2_menu.append(Text('- Percentage of races: %s' % perc))
	myinfo2_menu.append(Text('-'*25))
	myinfo2_menu.append(SimpleOption(7, 'Back',value=8))
	myinfo2_menu.append(Text(' '))
	myinfo2_menu.append(SimpleOption(9, 'Close', highlight=False))
	myinfo2_menu.send(index_from_userid(userid))

def doCommand(userid):
	player_entity = Player(index_from_userid(userid))
	racel = wcs.wcs.wcsplayers[userid].currace
	race = wcs.wcs.racedb.getRace(racel)
	name = race['skillnames'].split('|')
	skills = wcs.wcs.wcsplayers[userid].skills.split('|')
	levels = int(race['numberoflevels'])
	myinfo_menu = SimpleMenu()
	myinfo_menu.select_callback = myinfo_select
	myinfo_menu.append(Text('->1. %s' % player_entity.name))
	myinfo_menu.append(Text('-'*25))
	myinfo_menu.append(Text('o Total level %s' % str(wcs.wcs.wcsplayers[userid].totallevel)))
	myinfo_menu.append(Text('-'*25))
	myinfo_menu.append(Text('o %s: Level %s' % (str(wcs.wcs.wcsplayers[userid].currace), str(wcs.wcs.wcsplayers[userid].level))))
	for skill, level in enumerate(skills):
		myinfo_menu.append(Text(' - %s: [%s/%s]' % (name[skill], str(level), str(levels))))
	myinfo_menu.append(Text('-'*25))
	myinfo_menu.append(Text('Health : %s HP' % player_entity.health))
	myinfo_menu.append(Text('Speed : %s%%' % str(round(player_entity.speed*100))))
	myinfo_menu.append(Text('Gravity : %s%%' % str(round(player_entity.gravity*100))))
	myinfo_menu.append(Text(' '))
	myinfo_menu.append(SimpleOption(8, 'Next',value=7))
	myinfo_menu.append(SimpleOption(9, 'Close', highlight=False))
	myinfo_menu.send(index_from_userid(userid))
	
@ClientCommand('myinfo')
@SayCommand('myinfo')
def wcs_myinfo(command, index, team=None):
	userid = userid_from_index(index)
	doCommand(userid)
	
def all_races():
	races = wcs.wcs.racedb.getAll()
	return len(races)


def available_races(userid):
	x = 0
	races = wcs.wcs.racedb.getAll()
	allraces = races.keys()
	for number, race in enumerate(allraces):
		v = canUse(userid, race)
		if v == 1:
			x += 1
	return x
	
def left_to_next(userid):
	races = wcs.wcs.racedb.getAll()
	allraces = races.keys()
	for number, race in enumerate(allraces):
		raceinfo = wcs.wcs.racedb.getRace(race)
		race_dict[race] = int(raceinfo['required'])
	totallevel = wcs.wcs.wcsplayers[userid].totallevel
	level_list = sorted(race_dict.values())
	last_element = len(level_list)-1
	if totallevel < int(level_list[last_element]):
		while totallevel >= level_list[0]:
			del level_list[0]
		levels_left = int(level_list[0])-totallevel
	else:
		levels_left = 0
	if levels_left < 0:
		levels_left = 0
	return levels_left


def canUse(userid, race):
	player_entity = Player(index_from_userid(userid))
	raceinfo = wcs.wcs.racedb.getRace(race)
	totallevel = wcs.wcs.wcsplayers[userid].totallevel
	admins = raceinfo['allowonly'].split('|')
	if totallevel >= int(raceinfo['required']):
		return 1
	return 0