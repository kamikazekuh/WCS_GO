from wcs import shopmenu
from commands.say import SayCommand
from commands.client import ClientCommand
from menus import PagedMenu
from menus import PagedOption
from players.entity import Player
from configobj import ConfigObj
import os
from paths import PLUGIN_PATH
from messages import SayText2

item_path = os.path.join(PLUGIN_PATH+"\wcs", 'items', 'items.ini')
item_ini = ConfigObj(item_path)

def showitems_menu_build(menu, index):
	menu.clear()
	player = Player(index)
	items = shopmenu.items
	for x in items[player.userid]:
		for y in items[player.userid][x]:
			if int(items[player.userid][x][y]) > 0:
				for z in item_ini:
					if y in item_ini[z]:
						name = item_ini[z][y]['name']
						option = PagedOption('%s' % str(name), name)
						menu.append(option)
		
					
def showitems_menu_select(menu, index, choice):
	return


@SayCommand('showitems')
@ClientCommand('showitem')
def _showitems_command(command, index, team=None):
	player = Player(index)
	items = shopmenu.items
	count = 0
	for x in items[player.userid]:
		for y in items[player.userid][x]:
			if items[player.userid][x][y] > 0:
				count += 1
	if count > 0:
		showitem_menu = PagedMenu(title='Inventory', build_callback=showitems_menu_build, select_callback=showitems_menu_select)
		showitem_menu.send(index)
	else:
		SayText2("\x04[WCS] \x05You don't have any items!").send(index)
					
				
				
