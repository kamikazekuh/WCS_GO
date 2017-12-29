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
from menus import Text
from wcs.extensions import PagedMenu

import wcs
from wcs import givexp
from wcs import givelevel
from wcs import givecash
from wcs import resetrace
from wcs import resetplayer
from wcs import settings
from wcs import levelbank

value_1 = 'test1'
value_2 = 'test2'

def _wcs_admin_menu_select(menu, index, choice):
	userid = userid_from_index(index)
	if choice.choice_index == 1:
		if has_flag(userid, 'wcsadmin_settings'):
			settings.doCommand(userid)
		else:
			wcs.wcs.tell(userid, '\x04[WCS] \x05You \x04access \x05this menu!')
			wcs_admin_menu.send(index)
	if choice.choice_index == 2:
		if has_flag(userid, 'wcsadmin_givexp'):
			givexp.doCommand(userid)
		else:
			wcs.wcs.tell(userid, '\x04[WCS] \x05You \x04access \x05this menu!')
			wcs_admin_menu.send(index)
	if choice.choice_index == 3:
		if has_flag(userid, 'wcsadmin_givelevels'):
			givelevel.doCommand(userid)
		else:
			wcs.wcs.tell(userid, '\x04[WCS] \x05You \x04access \x05this menu!')
			wcs_admin_menu.send(index)
	if choice.choice_index == 4:
		if has_flag(userid, 'wcsadmin_givecash'):
			givecash.doCommand(userid)
		else:
			wcs.wcs.tell(userid, '\x04[WCS] \x05You \x04access \x05this menu!')
			wcs_admin_menu.send(index)
	if choice.choice_index == 5:
		if has_flag(userid, 'wcsadmin_resetrace'):
			resetrace.doCommand(userid)
		else:
			wcs.wcs.tell(userid, '\x04[WCS] \x05You \x04access \x05this menu!')
			wcs_admin_menu.send(index)
	if choice.choice_index == 6:
		if has_flag(userid, 'wcsadmin_resetplayer'):
			resetplayer.doCommand(userid)
		else:
			wcs.wcs.tell(userid, '\x04[WCS] \x05You \x04access \x05this menu!')
			wcs_admin_menu.send(index)
	if choice.choice_index == 7:
		if has_flag(userid, 'wcsadmin_bank'):
			levelbank.doCommand(userid)
		else:
			wcs.wcs.tell(userid, '\x04[WCS] \x05You \x04access \x05this menu!')
			wcs_admin_menu.send(index)
	if choice.choice_index == 9:
		menu.close(index)

wcs_admin_menu = SimpleMenu(
    [
        Text('WCS Admin Menu'),
        Text('-------------------'),
        SimpleOption(1, 'Settings', value_1),
        SimpleOption(2, 'Give XP', value_2),
        SimpleOption(3, 'Give Levels', value_1),
        SimpleOption(4, 'Give Cash', value_2),
		SimpleOption(5, 'Reset Race', value_2),
        SimpleOption(6, 'Reset Player', value_1),
        SimpleOption(7, 'Level Bank', value_2),
		Text('-------------------'),
        SimpleOption(9, 'Close', highlight=False),
    ],
    select_callback=_wcs_admin_menu_select)
	
	
	

def get_addon_path():
    path = os.path.dirname(os.path.abspath(__file__))
    return path
	

@SayCommand('wcsadmin')
@ClientCommand('wcsadmin')
def _wcs_admin_command(command, index, team=None):
	userid = userid_from_index(index)
	if is_admin(userid):
		wcs_admin_menu.send(index)
	
def is_admin(userid):
	admins = ini.getAdmins
	index = index_from_userid(userid)
	player = Player(index)
	if player.steamid in admins:
		return True
	else:
		return False
		
def has_flag(userid, flag):
	index = index_from_userid(userid)
	player = Player(index)
	if is_admin(userid):
		all_flags = admins.getAdmin(player.steamid)
		for x in all_flags:
			if x == flag:
				if all_flags[x] == '1':
					return True
				else:
					return False
	else:
		return False

	
#Ini Manager	
class InI(object):
	def __init__(self):
		self.path = get_addon_path()

		self.admins = os.path.join(self.path, 'admins', 'admins.ini')

	@property
	def getAdmins(self):
		return ConfigObj(self.admins)
		
ini = InI()

class Admins(object):
	def __init__(self):
		self.admins = ini.getAdmins
		
	def getAdmin(self, steamid):
		return self.admins[steamid]
admins = Admins()
