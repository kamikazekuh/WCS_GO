import os
from path import path as Path
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
import wcs.admin
from listeners import OnLevelInit
from sqlite3 import dbapi2 as sqlite
import wcs
from listeners.tick import Delay

@Event('player_activate')
def _player_activate(event):
	userid = event.get_int('userid')
	steamid = Player(index_from_userid(userid)).steamid
	UserID = database.getUserIdFromSteamId(steamid)
	if UserID is None:
		UserID = database.addPlayer(steamid)
		getPlayer(userid).levels += 6
		getPlayer(userid).save()
		Delay(6, wcs.wcs.tell, (userid, '\x04[WCS] \x05You got \x046 Levels \x05in your \x04Levelbank!'))
		database.save()

def get_addon_path():
    path = os.path.dirname(os.path.abspath(__file__))
    return path


#SQL Database
class SQLiteManager(object):
	def __init__(self, pathFile):
		if isinstance(pathFile, Path):
			self.pathFile = pathFile
		else:
			self.pathFile = Path(pathFile)

		self.connection   = sqlite.connect(self.pathFile.joinpath('levelbank.sqlite'))
		self.cursor       = self.connection.cursor()

		self.connection.text_factory = str
		#self.execute("PRAGMA synchronous=NORMAL")
		#self.execute("PRAGMA journal_mode=OFF")
		#self.execute("PRAGMA locking_mode=EXCLUSIVE")
		self.execute("PRAGMA auto_vacuum=FULL")

		self.execute("""\
			CREATE TABLE IF NOT EXISTS Players (
				UserID        INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
				steamid       VARCHAR(30) NOT NULL,
				levels        INTEGER DEFAULT 0
			)""")

		self.execute("CREATE INDEX IF NOT EXISTS playersIndex ON Players(steamid)")

	def __len__(self):
		self.execute("SELECT COUNT(*) FROM Players")
		return int(self.cursor.fetchone()[0])

	def __contains__(self, user):
		if not isinstance(user, str): #Tha Pwned
			self.execute("SELECT steamid FROM Players WHERE UserID = ?", (user, ))
		else:
			self.execute("SELECT steamid FROM Players WHERE steamid = ?", (user, ))
		return bool(self.cursor.fetchone())


	def execute(self, statement, args=None):
		if args is None:
			self.cursor.execute(statement)
		else:
			self.cursor.execute(statement, args)
			
	def fetchone(self):
		result = self.cursor.fetchone()
		if hasattr(result, '__iter__'):
			if len(result) == 1:
				return result[0]
		return result   

	def save(self):
		self.connection.commit()

	def close(self):
		self.cursor.close()
		self.connection.close()

	def getUserIdFromSteamId(self, steamid):
		self.execute("SELECT UserID FROM Players WHERE steamid = ?", (steamid, ))
		v = self.fetchone()
		if v is None:
			return None

		return v
		
	def addPlayer(self, steamid):
		self.execute("INSERT OR IGNORE INTO Players (steamid, levels) VALUES (?, 0)", (steamid, ))
		return self.cursor.lastrowid

	def removeWarnings(self, value):
		return str(value).replace("'", "").replace('"', '')
ini_path = get_addon_path()
database = SQLiteManager(Path(ini_path).joinpath('data'))


tmp = {}
def getPlayer(userid):
	userid = int(userid)
	if not userid in tmp:
		tmp[userid] = PlayerObject(userid)

	return tmp[userid]

class PlayerObject(object):
	def __init__(self, userid):
		self.userid = userid
		self.index = index_from_userid(userid)
		self.player_entity = Player(self.index)
		self.steamid = self.player_entity.steamid
		self.UserID = database.getUserIdFromSteamId(self.steamid)
		
		if self.UserID is None:
			self.UserID = database.addPlayer(self.steamid)

		self.update()
		database.save()


	def update(self):
		self.levels = self._getInfo('levels')

	def save(self):
		self._setInfo(self.levels)
		database.save()

	def _getInfo(self, what):
		database.execute("SELECT "+what+" FROM Players WHERE UserID = ?", (self.UserID, ))

		v = database.fetchone()
		if v is None:
			return 0
		return v

	def _setInfo(self, options):
		database.execute("UPDATE Players SET levels=%s WHERE UserID = ?" % options, (self.UserID, ))

	def addLevel(self, amount):
		amount = int(amount)
		if not amount:
			return

		self.levels += amount

		return self.levels
		
def wcsadmin_bank_menu_build(menu, index):
	menu.clear()
	for player in PlayerIter():
		if player.steamid != 'BOT':
			option = PagedOption('%s' % player.name, player)
			menu.append(option)
			
def wcs_amount_select(menu, index, choice):
	if choice.value == 'spendlevels':
		player = getPlayer(userid_from_index(index))
		amount = int(choice.text)
		if player.levels >= amount:
			wcs.wcs.getPlayer(userid_from_index(index)).race.addLevel(amount)
			player.levels -= amount
			wcs.wcs.tell(userid_from_index(index), '\x04[WCS] \x05You got \x04%s Levels \x05left in your \x04Bank!' % player.levels)
			getPlayer(userid_from_index(index)).save()
		else:
			wcs.wcs.tell(userid_from_index(index), "\x04[WCS] \x05You don't have enough \x04levels \x05in your \x04bank!")
			menu.send(index)
	else:		
		userid = choice.value.userid
		amount = int(choice.text)
		player = Player(index)
		getPlayer(userid).levels += amount
		wcs.wcs.tell(userid, '\x04[WCS] \x05You got \x04%s Bank-Levels \x05from admin \x04%s!' % (amount, player.name))
		getPlayer(userid).save()
			
amount_menu = PagedMenu(title='Amount Menu', select_callback=wcs_amount_select)

def wcsadmin_bank_menu_select(menu, index, choice):
	player_entity = choice.value
	amount_menu.clear()
	amount_menu.parent_menu = menu
	amount_menu.append(PagedOption('1', player_entity))
	amount_menu.append(PagedOption('5', player_entity))
	amount_menu.append(PagedOption('10', player_entity))
	amount_menu.append(PagedOption('25', player_entity))
	amount_menu.append(PagedOption('100', player_entity))
	amount_menu.append(PagedOption('250', player_entity))
	amount_menu.append(PagedOption('1000', player_entity))
	amount_menu.append(PagedOption('2500', player_entity))
	amount_menu.send(index)

@ClientCommand('wcsbank')
@SayCommand('wcsbank')
def wcs_bank_command(command, index, team=None):
	player = getPlayer(userid_from_index(index))
	player_entity = Player(index)
	if player.levels:
		amount_menu.clear()
		amount_menu.append(Text('You have %s Levels in your bank' % player.levels))
		amount_menu.append(PagedOption('1', 'spendlevels'))
		amount_menu.append(PagedOption('5', 'spendlevels'))
		amount_menu.append(PagedOption('10', 'spendlevels'))
		amount_menu.append(PagedOption('25', 'spendlevels'))
		amount_menu.append(PagedOption('100', 'spendlevels'))
		amount_menu.append(PagedOption('250', 'spendlevels'))
		amount_menu.append(PagedOption('1000', 'spendlevels'))
		amount_menu.append(PagedOption('2500', 'spendlevels'))
		amount_menu.send(index)
		
def doCommand(userid):
	index = index_from_userid(userid)
	if wcs.admin.is_admin(userid):
		if wcs.admin.has_flag(userid, 'wcsadmin_bank'):
			wcsadmin_bank_menu = PagedMenu(title='WCSBank Menu', build_callback=wcsadmin_bank_menu_build, select_callback=wcsadmin_bank_menu_select)
			wcsadmin_bank_menu.send(index)
	else:
		wcs.wcs.tell(userid, '\x04[WCS] \x05You\'re \x04not \x05an WCS-Bank admin')		
	
@ClientCommand('wcsbankadmin')
@SayCommand('wcsbankadmin')
def wcs_bank_admin_command(command, index, team=None):
	userid = userid_from_index(index)
	if wcs.admin.is_admin(userid):
		if wcs.admin.has_flag(userid, 'wcsadmin_bank'):
			wcsadmin_bank_menu = PagedMenu(title='WCSBank Menu', build_callback=wcsadmin_bank_menu_build, select_callback=wcsadmin_bank_menu_select)
			wcsadmin_bank_menu.send(index)
	else:
		wcs.wcs.tell(userid, '\x04[WCS] \x05You\'re \x04not \x05an WCS-Bank admin')
		
DATABASE_STORAGE_METHOD = SQLiteManager
databasePath = Path(ini_path).joinpath('data')

def load():
	global database
	database = DATABASE_STORAGE_METHOD(databasePath)

def unload():
	tmp.clear()

	database.save()
	database.close()

@OnLevelInit
def level_init_listener(mapname):
	global database
	database = DATABASE_STORAGE_METHOD(databasePath)
	database.save()


@Event('player_disconnect')
def player_disconnect(event):
	global tmp
	userid = event.get_int('userid')
	if userid in tmp:
		tmp[userid].save()
		del tmp[userid]