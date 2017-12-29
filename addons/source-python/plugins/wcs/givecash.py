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
from wcs.extensions import PagedMenu

import wcs



def wcsadmin_givecash_menu_build(menu, index):
	menu.clear()
	for player in PlayerIter():
		if player.steamid != 'BOT':
			option = PagedOption('%s' % player.name, player)
			menu.append(option)
			
def wcs_amount_select(menu, index, choice):
	userid = choice.value.userid
	amount = int(choice.text)
	player = Player(index_from_userid(userid))
	player.cash += amount
	wcs.wcs.tell(userid, '\x04[WCS] \x05You got \x04%s$ \x05from admin \x04%s!' % (amount, player.name))
			
amount_menu = PagedMenu(title='Amount Menu', select_callback=wcs_amount_select)

def wcsadmin_givecash_menu_select(menu, index, choice):
	player_entity = choice.value
	amount_menu.previous_menu = menu
	amount_menu.append(PagedOption('100', player_entity))
	amount_menu.append(PagedOption('1000', player_entity))
	amount_menu.append(PagedOption('3000', player_entity))
	amount_menu.append(PagedOption('6000', player_entity))
	amount_menu.append(PagedOption('10000', player_entity))
	amount_menu.append(PagedOption('16000', player_entity))
	amount_menu.send(index)
		
def doCommand(userid):
	index = index_from_userid(userid)
	wcsadmin_givecash_menu = PagedMenu(title='GiveCash Menu', build_callback=wcsadmin_givecash_menu_build, select_callback=wcsadmin_givecash_menu_select)
	wcsadmin_givecash_menu.send(index)