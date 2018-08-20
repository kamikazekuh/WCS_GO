from players.entity import Player
from players.helpers import index_from_userid, playerinfo_from_userid, index_from_playerinfo, userid_from_index
from menus import SimpleMenu
from menus import SimpleOption
from menus import PagedOption
from menus import Text
import wcs
from menus import PagedMenu
from filters.players import PlayerIter

def playerinfo_player_build(menu, index):
	menu.clear()
	for player in PlayerIter():
		option = PagedOption('%s' % player.name, player)
		menu.append(option)

def playerinfo_select(menu, index, choice):
	if choice.choice_index == 8:
		doCommand(userid_from_index(index))

def playerinfo_player_select(menu, index, choice):
	userid = userid_from_index(index)
	player_entity = choice.value
	race = wcs.wcs.racedb.getRace(wcs.wcs.wcsplayers[player_entity.userid].currace)
	name = race['skillnames'].split('|')
	skills = wcs.wcs.wcsplayers[player_entity.userid].skills.split('|')
	nol = race['numberoflevels']
	if ('|') in nol:
		levels = nol.split('|')
	else:
		levels = []
		levels += int(race['numberofskills']) * [int(nol)]
	playerinfo_menu = SimpleMenu()
	playerinfo_menu.select_callback = playerinfo_select
	playerinfo_menu.append(Text('->1. %s' % player_entity.name))
	playerinfo_menu.append(Text('-'*25))
	playerinfo_menu.append(Text('o Total level %s' % str(wcs.wcs.wcsplayers[player_entity.userid].totallevel)))
	playerinfo_menu.append(Text('-'*25))
	playerinfo_menu.append(Text('o %s: Level %s' % (str(wcs.wcs.wcsplayers[player_entity.userid].currace), str(wcs.wcs.wcsplayers[player_entity.userid].level))))
	for skill, level in enumerate(skills):
		playerinfo_menu.append(Text(' - %s: [%s/%s]' % (name[skill], str(level), str(levels[skill]))))
	playerinfo_menu.append(Text('-'*25))
	playerinfo_menu.append(Text('Health : %s HP' % player_entity.health))
	playerinfo_menu.append(Text('Speed : %s%%' % str(round(player_entity.speed*100))))
	playerinfo_menu.append(Text('Gravity : %s%%' % str(round(player_entity.gravity*100))))
	playerinfo_menu.append(Text('Invisiblity: %s%%' % (100-round(player_entity.color[3]/2.55))))
	playerinfo_menu.append(SimpleOption(8, 'Back',value=8))
	playerinfo_menu.append(Text(' '))
	playerinfo_menu.append(SimpleOption(9, 'Close', highlight=False))
	playerinfo_menu.send(index)

playerinfo_player_menu = PagedMenu(title='Playerinfo Menu', build_callback=playerinfo_player_build, select_callback=playerinfo_player_select)	

	
def doCommand(userid):
	index = index_from_userid(userid)
	#playerinfo_player_menu = PagedMenu(title='Playerinfo Menu', build_callback=playerinfo_player_build, select_callback=playerinfo_player_select)
	playerinfo_player_menu.send(index)
