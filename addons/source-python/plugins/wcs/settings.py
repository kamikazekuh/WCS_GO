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



def wcsadmin_givexp_menu_build(menu, index):
	menu.clear()
	option = PagedOption('Give all XP', 'xp')
	menu.append(option)
	option = PagedOption('Give all Levels', 'level')
	menu.append(option)
	option = PagedOption('Give all Cash', 'cash')
	menu.append(option)

			
def wcs_amount_select(menu, index, choice):
	amount = int(choice.text)
	player_entity = Player(index)
	if choice.value == 'xp':
		for player in PlayerIter():
			wcs.wcs.wcsplayers[player.userid].give_xp(amount)
			wcs.wcs.tell(player.userid, '\x04[WCS] \x05You got \x04%s XP \x05from admin \x04%s!' % (amount, player_entity.name))
	if choice.value == 'level':
		for player in PlayerIter():
			wcs.wcs.wcsplayers[player.userid].give_level(amount)
			wcs.wcs.tell(player.userid, '\x04[WCS] \x05You got \x04%s Levels \x05from admin \x04%s!' % (amount, player_entity.name))
	if choice.value == 'cash':
		for player in PlayerIter():
			player.cash += amount
			wcs.wcs.tell(player.userid, '\x04[WCS] \x05You got \x04%s$ \x05from admin \x04%s!' % (amount, player_entity.name))
	menu.clear()
			
amount_menu = PagedMenu(title='Amount Menu', select_callback=wcs_amount_select)

def wcsadmin_givexp_menu_select(menu, index, choice):
	if choice.value == 'xp' or choice.value == 'level':
		amount_menu.parent_menu = menu
		amount_menu.append(PagedOption('1', choice.value))
		amount_menu.append(PagedOption('10', choice.value))
		amount_menu.append(PagedOption('50', choice.value))
		amount_menu.append(PagedOption('100', choice.value))
		amount_menu.append(PagedOption('300', choice.value))
		amount_menu.append(PagedOption('500', choice.value))
		amount_menu.send(index)
	if choice.value == 'cash':
		amount_menu.parent_menu = menu
		amount_menu.append(PagedOption('100', choice.value))
		amount_menu.append(PagedOption('1000', choice.value))
		amount_menu.append(PagedOption('3000', choice.value))
		amount_menu.append(PagedOption('6000', choice.value))
		amount_menu.append(PagedOption('10000', choice.value))
		amount_menu.append(PagedOption('16000', choice.value))
		amount_menu.send(index)		
		
def doCommand(userid):
	index = index_from_userid(userid)
	wcsadmin_givexp_menu.send(index)

wcsadmin_givexp_menu = PagedMenu(title='Settings Menu', build_callback=wcsadmin_givexp_menu_build, select_callback=wcsadmin_givexp_menu_select)