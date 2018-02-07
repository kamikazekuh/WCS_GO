import wcs
from menus import PagedMenu
from players.entity import Player
from players.helpers import index_from_userid, playerinfo_from_userid, index_from_playerinfo, userid_from_index
from menus import SimpleMenu
from menus import SimpleOption
from menus import PagedOption
from menus import Text

def wcstop_menu_select(menu, index, choice):
	menu.close()

def wcstop_menu_build(menu, index):
	menu.clear()
	allplayers = sorted(wcs.wcs.wcs_rank, key=lambda x: wcs.wcs.wcs_rank[x]['totallevel'],reverse=True)
	if len(allplayers):
		for number, steamid in enumerate(allplayers):
			if number < 5:
				name = wcs.wcs.wcs_rank[steamid]['name']
				currace = wcs.wcs.wcs_rank[steamid]['currace']
				totallevel = wcs.wcs.wcs_rank[steamid]['totallevel']
				level = wcs.wcs.wcs_rank[steamid]['level']
				option = PagedOption('%s | Total level: %s | Playing %s | Level %s' % (str(name),totallevel, currace, level), str(name), highlight=True, selectable=False)
				menu.append(option)
					
def doCommand(userid):
	wcstop_menu = PagedMenu(title='WCS Top Menu',build_callback=wcstop_menu_build, select_callback=wcstop_menu_select)
	wcstop_menu.send(index_from_userid(userid))

def wcsRank(userid):
	wcs.wcs.wcsplayers[userid].show_rank()
