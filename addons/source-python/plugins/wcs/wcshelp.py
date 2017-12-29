from players.entity import Player
from players.helpers import index_from_userid, playerinfo_from_userid, index_from_playerinfo, userid_from_index
from menus import SimpleMenu
from menus import SimpleOption
from menus import Text
import wcs

	
def wcshelp_select(menu, index, choice):
    return

wcshelp = SimpleMenu(
    [
        Text('Chat Commands:'),
		Text('wcshelp - This help'),
		Text('changerace - Choose your race'),
		Text('raceinfo - Show info about skills'),
		Text('shopmenu - Buy shopitems'),
		Text('shopinfo - Show item info'),
		Text('showxp - Race, level and XP'),
		Text('showskills - Show all skills levels'),
		Text('resetskills - Reset your skills'),
		Text('spendskills - Spend skill points'),
		Text('playerinfo - Shows info about a player'),
		Text('wcsadmin - Admin menu'),
		Text('wcstop - WCS top'),
		Text('wcsrank - WCS rank'),
		SimpleOption(9, 'Close', highlight=False)
    ],
    select_callback=wcshelp_select)
	
	
def doCommand(userid):
	index = index_from_userid(userid)
	wcshelp.send(index)
