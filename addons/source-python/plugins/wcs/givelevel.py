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

import wcs



def wcsadmin_givelevel_menu_build(menu, index):
	menu.clear()
	for player in PlayerIter():
		if player.steamid != 'BOT':
			option = PagedOption('%s' % player.name, player)
			menu.append(option)
			
def wcs_amount_select(menu, index, choice):
	userid = choice.value.userid
	amount = int(choice.text)
	player = Player(index)
	wcs.wcs.wcsplayers[userid].give_level(amount)
	wcs.wcs.tell(userid, '\x04[WCS] \x05You got \x04%s Levels \x05from admin \x04%s!' % (amount, player.name))
			
amount_menu = PagedMenu(title='Amount Menu', select_callback=wcs_amount_select)

def wcsadmin_givelevel_menu_select(menu, index, choice):
	player_entity = choice.value
	amount_menu.clear()
	amount_menu.parent_menu = menu
	amount_menu.append(PagedOption('1', player_entity))
	amount_menu.append(PagedOption('10', player_entity))
	amount_menu.append(PagedOption('50', player_entity))
	amount_menu.append(PagedOption('100', player_entity))
	amount_menu.append(PagedOption('300', player_entity))
	amount_menu.append(PagedOption('500', player_entity))
	amount_menu.send(index)
		
def doCommand(userid):
	index = index_from_userid(userid)
	wcsadmin_givelevel_menu.send(index)

wcsadmin_givelevel_menu = PagedMenu(title='GiveLevel Menu', build_callback=wcsadmin_givelevel_menu_build, select_callback=wcsadmin_givelevel_menu_select)