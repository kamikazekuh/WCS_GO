from menus import SimpleMenu
from menus import SimpleOption
from menus import Text
from players.helpers import index_from_userid, userid_from_index
from wcs import shopmenu
from wcs import shopinfo
from wcs import showskills
from wcs import resetskills
from wcs import spendskills
from wcs import changerace
from wcs import raceinfo
from wcs import playerinfo
from wcs import config


def doCommand(userid):
	main_menu.clear()
	index = index_from_userid(userid)
	main_menu.send(index)

def _main_menu_select(menu, index, choice):
	menu.clear()
	userid = int(userid_from_index(index))
	if choice.choice_index == 1:
		shopmenu.shopmenu_menu_cats.parent_menu=menu
		shopmenu.doCommand(userid)
		menu.close(index)
	elif choice.choice_index == 2:
		shopinfo.doCommand(userid)
		menu.close(index)
	elif choice.choice_index == 3:
		showskills.doCommand(userid)
		menu.close(index)
	elif choice.choice_index == 4:
		resetskills.doCommand(userid)
		menu.close(index)
	elif choice.choice_index == 5:
		spendskills.doCommand(userid)
		menu.close(index)
	elif choice.choice_index == 6:
		if config.coredata['categories'] == "1":
			changerace.changerace_menu_cats.parent_menu=menu
		else:
			changerace.changerace_menu.parent_menu=menu
		changerace.HowChange(userid)
		menu.close(index)
	elif choice.choice_index == 7:
		raceinfo.raceinfo_menu.parent_menu = menu
		raceinfo.doCommand(userid)
		menu.close(index)
	elif choice.choice_index == 8:
		playerinfo.playerinfo_player_menu.parent_menu=menu
		playerinfo.doCommand(userid)
		menu.close(index)
	elif choice.choice_index == 9:
		menu.close(index)
		
def _main_menu_build(menu, index):
	menu.clear()
	menu.append(Text('WCS Menu'))
	menu.append(SimpleOption(1, 'shopmenu - buy shop items', 'shopmenu'))
	menu.append(SimpleOption(2, 'shopinfo - show item info', 'shopinfo'))
	menu.append(Text('-------------------'))
	menu.append(SimpleOption(3, 'showskills - show all skills levels', 'showskills'))
	menu.append(SimpleOption(4, 'resetskills - reset your skills', 'resetskills'))
	menu.append(SimpleOption(5, 'spendskills - spend skill points', 'spendskills'))
	menu.append(Text('-------------------'))
	menu.append(SimpleOption(6, 'changerace - choose your race', 'changerace'))
	menu.append(SimpleOption(7, 'raceinfo - show info about skills', 'raceinfo'))
	menu.append(Text('-------------------'))
	menu.append(SimpleOption(8, 'playerinfo - shows info about a player', 'playerinfo'))
	menu.append(Text('-------------------'))
	menu.append(SimpleOption(9, 'Close', highlight=False))
	
main_menu = SimpleMenu(select_callback=_main_menu_select, build_callback=_main_menu_build)