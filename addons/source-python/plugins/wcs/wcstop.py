import wcs
from wcs.database import database
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
	allplayers = list(wcs.wcs.database.ranks)
	if len(allplayers):
		for number, steamid in enumerate(allplayers):
			if number < 5:
				UserID = database.getUserIdFromSteamId(steamid)
				v = database.getInfoPlayer('all',UserID)
				if v:
					name = v[2]
					currace = v[1]
					totallevel = v[3]
					RaceID = database.getRaceIdFromUserIdAndRace(UserID,currace)
					z = database.getInfoRace('all',UserID,RaceID)
					if z:
						level = z[2]

					option = PagedOption('%s | Total level: %s | Playing %s | Level %s' % (str(name),totallevel, currace, level), str(name), highlight=True, selectable=False)
					menu.append(option)
					#menu.append(Text('	 Total level: %s | Playing %s | Level %s' % (totallevel, currace, level)))
					
def doCommand(userid):
	wcstop_menu = PagedMenu(title='WCS Top Menu',build_callback=wcstop_menu_build, select_callback=wcstop_menu_select)
	wcstop_menu.send(index_from_userid(userid))

def wcsRank(userid):
	player = wcs.wcs.getPlayer(userid)

	player.showRank()
