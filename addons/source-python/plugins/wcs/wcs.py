import os
import random
from random import choice
import time
import sys

from core import SOURCE_ENGINE_BRANCH

from path import path as Path
from sqlite3 import dbapi2 as sqlite
from base64 import encodestring as estr, decodestring as dstr
from configobj import ConfigObj
import string
import re
from messages import HudMsg
from menus import PagedMenu
from listeners import OnTick
import core

from translations.strings import LangStrings

#Source Python
from commands.say import SayCommand
from commands.client import ClientCommand
from commands.server import ServerCommand
from players.helpers import index_from_userid, userid_from_index
from players.entity import Player
from events import Event
from engines.server import execute_server_command, queue_command_string
from filters.players import PlayerIter

from menus import SimpleMenu
from menus import SimpleOption
from menus import Text

from messages import SayText2, HintText
from listeners import OnLevelInit, OnLevelShutdown
from listeners.tick import Delay
import es
from colors import Color
#WCS Imports
from wcs import admin
from wcs import changerace
from wcs import commands
from wcs import downloader
from wcs import effects
import wcs.events
from wcs import firefix
from wcs import ladderfix
from wcs import levelbank
from wcs import longjump
from wcs import myinfo
from wcs import playerinfo
from wcs import raceinfo
from wcs import randomrace
from wcs import resetskills
from wcs import restrictions
from wcs import savexp
from wcs import saycommands
from wcs import setfx
from wcs import shopinfo
from wcs import shopmenu
from wcs import showitems
from wcs import showskills
from wcs import spendskills
from wcs import svar
from wcs import teamrestrictions
from wcs import wcs_commands
from wcs import wcsgroup
from wcs import wcshelp
from wcs import wcsmenu
from wcs import wcstop
from wcs import xtell




#   Config
from config.manager import ConfigManager
#   Cvars
from cvars.flags import ConVarFlags
from cvars import ConVar

color_codes = ['\x03', '\x04', '\x05', '\x06', '\x07']


#Config Part
addon_config = ConfigManager('wcs')
interval = addon_config.cvar('wcs_cfg_interval', '80')
bonusxp = addon_config.cvar('wcs_cfg_bonusxp', '80')
killxp = addon_config.cvar('wcs_cfg_killxp', '80')
knifexp = addon_config.cvar('wcs_cfg_knifexp', '80')
headshotxp = addon_config.cvar('wcs_cfg_headshotxp', '80')
xpsaver = addon_config.cvar('wcs_cfg_savexponround', '5')
racecategories = addon_config.cvar('wcs_racecats', '0')
defaultcategory	= addon_config.cvar('wcs_racecats_defaultcategory',	'Default category')
showracelevel = addon_config.cvar('wcs_cfg_showracelevel', '1')
keymenu = addon_config.cvar('wcs_activate_keymenu', '0')
categories = addon_config.cvar('wcs_activate_categories', '0')
unassigned_cat = addon_config.cvar('wcs_unassigned_category', '1')
addon_config.write()

cfgdata = {'interval':				interval.cvar.get_int(),
		   'bonusxp':				bonusxp.cvar.get_int(),
		   'killxp':				killxp.cvar.get_int(),
		   'knifexp':				knifexp.cvar.get_int(),
		   'headshotxp':			headshotxp.cvar.get_int(),
		   'racecategories':		racecategories.cvar.get_int(),
		   'defaulcategory':		defaultcategory.cvar.get_string(),
		   'showracelevel':			showracelevel.cvar.get_int()}

tmp = {}

gamestarted = 0

	
#Helper Functions
def get_addon_path():
    path = os.path.dirname(os.path.abspath(__file__))
    return path

if os.path.isfile(os.path.join(get_addon_path(), 'strings', 'strings.ini')):
	strings = LangStrings(os.path.join(get_addon_path(), 'strings', 'strings'))	
	
def find_between(s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""
		
def get_cooldown(userid):
	player = getPlayer(userid)
	race = player.player.currace
	race1 = racedb.getRace(race)
	if 'player_ultimate' in raceevents[race]:
		skills = player.race.skills.split('|')
		index = raceevents[race]['player_ultimate'][0]
		skill = 'skill'+str(int(index)+1)
		try:
			level = int(skills[int(index)])
		except IndexError:
			level = None
		if level:
			downtime = str(race1[skill]['cooldown']).split('|')
			if len(downtime) == int(player.race.racedb['numberoflevels']):
				downtime = int(downtime[level-1])
				if not downtime:
					downtime = str(race1[skill]['cooldown']).split('|')
					downtime = int(downtime[0])
				return downtime
			else:
				return int(downtime[len(downtime)-1])

	
def format_message(message):
	for color in color_codes:
		if color in message:
			message = message.replace(color, '')
	return message
	
def tell(userid, message):
	text_message = 1
	index = index_from_userid(userid)
	if text_message == 1:
		if SOURCE_ENGINE_BRANCH == "css":
			message = message.replace('\x05','\x03')
		SayText2(message).send(index)
	if text_message == 2:
		message = format_message(message)
		HintText(message).send(index)
		
def centertell(userid,message):
	index = index_from_userid(userid)
	if SOURCE_ENGINE_BRANCH == "css":
		queue_command_string("es_centertell %s %s" %(userid,message))
	else:
		HudMsg(message, -1, 0.35,hold_time=5.0).send(index)
		
'''def format_tell_message(message):
	if '#white' in message:
		message = message.replace('#white', '\x01')
	if '#red' in message:
		message = message.replace('#red', '\x02')
	if '#green' in message:
		message = message.replace('#green', '\x04')
	if '#lightgreen' in message:
		message = message.replace('#lightgreen', '\x05')
	if '#darkgreen' in message:
		message = message.replace('#darkgreen', '\x06')
	if '#lightred' in message:
		message = message.replace('#lightred', '\x07')

	return message'''
		
#Ini Manager	
class InI(object):
	def __init__(self):
		self.path = get_addon_path()

		self.races = os.path.join(self.path, 'races', 'races.ini')
		self.items = os.path.join(self.path, 'items', 'items.ini')

	@property
	def getRaces(self):
		try:
			return ConfigObj(self.races)
		except:
			sys.excepthook(*sys.exc_info())
			return ConfigObj(self._races)

	@property
	def getItems(self):
		return ConfigObj(self.items)
	
	@property
	def getCats(self):
		return ConfigObj(self.cats)			
ini = InI()

#Item Databse
class itemDatabase(object):
	def __init__(self):
		self.items = ini.getItems
		self.sectionlist = []
		self.itemlist = []
		self.itemtosection = {}

		for section in self.items:
			self.sectionlist.append(section)
			for item in self.items[section]:
				if item == 'desc':
					continue

				self.itemlist.append(item)
				self.itemtosection[item] = section

	def __contains__(self, item):
		return item in self.items

	def __iter__(self):
		for x in self.items:
			yield x

	def __getitem__(self, item):
		return self.items[item]

	def keys(self):
		return self.items.keys()

	def getSection(self, section):
		return dict(self.items[section])

	def getItem(self, item):
		return dict(self.items[self.getSectionFromItem(item)][item])

	def getSections(self):
		return list(self.sectionlist)

	def getItems(self):
		return list(self.itemlist)

	def getSectionFromItem(self, item):
		if item in self.itemtosection:
			return self.itemtosection[item]

		return None

	def getAll(self):
		return dict(self.items)
itemdb = itemDatabase()

#Race Database
class raceDatabase(object):
	def __init__(self):
		self.races = ini.getRaces

	def __contains__(self, race):
		return race in self.races

	def __iter__(self):
		for x in self.races:
			yield x

	def getRace(self, race):
		return self.races[race]

	def getAll(self):
		return self.races

	def getAlias(self):
		return aliass

	def index(self, race):
		return self.races.keys().index(race)     
racedb = raceDatabase()


if len(racedb.getAll()):
	standardrace = racedb.getAll().keys()[0]
	
#SQL Database
class SQLiteManager(object):
	def __init__(self, pathFile):
		if isinstance(pathFile, Path):
			self.pathFile = pathFile
		else:
			self.pathFile = Path(pathFile)

		self.connection   = sqlite.connect(self.pathFile.joinpath('players.sqlite'))
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
				currace       VARCHAR(30) NOT NULL,
				name          VARCHAR(30) NOT NULL,
				totallevel    INTEGER DEFAULT 0,
				lastconnect   INTEGER
			)""")

		self.execute("CREATE INDEX IF NOT EXISTS playersIndex ON Players(steamid)")

		self.execute("""\
			CREATE TABLE IF NOT EXISTS Races (
				RaceID        INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
				UserID        INTEGER NOT NULL,
				name          VARCHAR(50) NOT NULL,
				skills        VARCHAR(50) NOT NULL,
				level         INTEGER DEFAULT 0,
				xp            INTEGER DEFAULT 0,
				unused        INTEGER DEFAULT 0
			)""")

		self.execute("CREATE INDEX IF NOT EXISTS racesIndex ON Races(UserID)")

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

	def fetchall(self):
		trueValues = []
		for value in self.cursor.fetchall():
			if isinstance(value, tuple):
				if len(value) > 1:
					trueValues.append(value)
				else:
					trueValues.append(value[0])
			else:
				trueValues.append(value)
		return trueValues

	def save(self):
		self.connection.commit()

	def close(self):
		self.cursor.close()
		self.connection.close()

	def getUserIdFromSteamId(self, steamid):
		self.execute("SELECT UserID FROM Players WHERE steamid = ?", (steamid, ))
		value = self.cursor.fetchone()
		if value is None:
			return None

		return value[0]

	def addPlayer(self, steamid, name):
		self.execute("INSERT INTO Players (steamid, currace, name, totallevel, lastconnect) VALUES (?,?,?,0,?)", (steamid, standardrace, self.removeWarnings(name), time.time())) #Tha Pwned
		return self.cursor.lastrowid

	def getRaceIdFromUserIdAndRace(self, userid, race):
		if isinstance(userid, str):
			userid = self.getUserIdFromSteamId(userid)

		self.execute("SELECT RaceID FROM Races WHERE UserID = ? AND name = ?", (userid, race))
		value = self.cursor.fetchone()
		if value is None:
			return None

		return value[0]

	def addRaceIntoPlayer(self, userid, name):
		if isinstance(userid, str): #Tha Pwned
			userid = self.getUserIdFromSteamId(userid)

		self.execute("INSERT INTO Races (UserID, name, skills) VALUES (?,?,'')", (userid, name)) #Tha Pwned
		return self.cursor.lastrowid

	def updateRank(self):
		self.execute("SELECT steamid FROM Players ORDER BY totallevel DESC")
		results = self.cursor.fetchall()
		self.ranks = []

		for steamid in results:
			self.ranks.append(steamid[0])

	def getRank(self, steamid):
		if steamid in self.ranks:
			return self.ranks.index(steamid) + 1
		return self.__len__()

	def removeWarnings(self, value):
		return str(value).replace("'", "").replace('"', '')
database = SQLiteManager(Path(ini.path).joinpath('data'))

#PlayerObject Functions
def getPlayer(userid):
	userid = int(userid)
	if not userid in tmp:
		tmp[userid] = PlayerObject(userid)
	return tmp[userid]
	
class PlayerObject(object):
    def __init__(self, userid):
        self.userid             = userid
        self.index 				= index_from_userid(self.userid)
        self.player_entity 		= Player(self.index)
        self.steamid            = self.player_entity.steamid
        if self.steamid == 'BOT':
            self.steamid = 'BOT_'+str(self.player_entity.name)
        self.UserID             = database.getUserIdFromSteamId(self.steamid)
		
        if self.UserID is None:
            self.UserID         = database.addPlayer(self.steamid, self.player_entity.name)

        self.player             = _getPlayer(self.userid, self.UserID)
        self.race               = _getRace(self.UserID, self.player.currace, self.userid)

    def __del__(self):
        self.save()

    def __str__(self):
        return str(self.userid)

    def __int__(self):
        return self.userid

    def save(self):
        self.player.save()
        self.race.save()

    def changeRace(self, race, kill=True):
        self.race.save()

        if self.race.racedb['onchange']:
            command = self.race.racedb['onchange']
            command = command.split(";")
            for com in command:
                execute_server_command('es', com)
        oldrace = self.player.currace

        self.player.currace = str(race)

        self.race = _getRace(self.UserID, race, self.userid)
        self.race.update()
        self.race.refresh()
        self.race.save()
        if kill:
            self.player_entity.client_command("kill", True)
        tell(self.player_entity.userid, '\x04[WCS] \x05You changed your race to \x04%s.' % race)
        event_instance = wcs.events.wcs_changerace(userid=self.userid, oldrace=oldrace, newrace=race)
        event_instance.fire()

    def giveXp(self, amount, reason=''):
        return self.race.addXp(amount, reason)

    def giveLevel(self, amount):
        return self.race.addLevel(amount)

    def giveUnused(self, amount):
        return self.race.addUnused(amount)

    def givePoint(self, skill):
        return self.race.addPoint(skill)

    def showXp(self):
        xp         = self.race.xp
        level      = self.race.level
        needed     = int(cfgdata['interval'])*level if level else int(cfgdata['interval'])
        race       = self.player.currace

        tell(self.userid, '\x04[WCS] \x04%s \x05 - Level: \x04%s \x05 - XP: \x04%s/%s' % (race, level, xp, needed))

    def showRank(self):
        name       = self.player.name
        race       = self.player.currace
        level      = self.race.level
        place      = database.getRank(self.steamid)
        total      = str(len(database))
        xp         = self.race.xp
        needed     = int(cfgdata['interval'])*level if level else int(cfgdata['interval'])
        unused     = self.race.unused

        for player in PlayerIter():
            tell(player.userid, "\x05[WCS] \x05%s \x04is on race \x05%s \x04level\x05 %s\x04, ranked \x05%s/%s \x04with\x05 %s/%s \x04XP and \x05%s \x04Unused." % (name, race, level, place, total, xp, needed, unused))

    def delRace(self):
        self.player.totallevel -= int(self.race.level)
        database.execute("DELETE FROM Races WHERE UserID = ? AND name = ?", (self.UserID, self.player.currace))
        self.race.level = 0
        self.race.xp = 0
        self.race.skills = ''
        self.race.unused = 0
        self.race.refresh()
        self.race.save()

    def delPlayer(self):
        database.execute('DELETE FROM Players WHERE UserID = ?', (self.player.UserID, ))
        database.execute('DELETE FROM Races WHERE UserID = ?', (self.player.UserID, ))

        del tmp1[self.userid]
        del tmp2[self.userid]

        self.player = _getPlayer(self.userid, self.UserID)
        self.race = _getRace(self.UserID, self.player.currace, self.userid)

        self.race.refresh()

#Player Functions
tmp1 = {}
def _getPlayer(userid, UserID):
	userid = int(userid)
	if not userid in tmp1:
		tmp1[userid] = Player_WCS(userid, UserID)

	return tmp1[userid]

class Player_WCS(object):
	def __init__(self, userid, UserID):
		self.userid = userid
		self.UserID = UserID
		self.update()

	def update(self):
		self.steamid, self.currace, self.name, self.totallevel, self.lastconnect = self._getInfo(('steamid',
																								  'currace',
																								  'name',
																								  'totallevel',
																								  'lastconnect'))

		self.name = database.removeWarnings(self.name)

	def save(self):
		try:
			self._setInfo({'steamid':self.steamid,
						   'currace':self.currace,
						   'name':self.name,
						   'totallevel':self.totallevel,
						   'lastconnect':self.lastconnect})
		except:
			return
            
	def _getInfo(self, what):
		if not hasattr(what, '__iter__'):
			what = (what, )

		database.execute("SELECT "+','.join(map(str, what))+" FROM Players WHERE UserID = ?", (self.UserID, ))

		v = database.fetchone()
		if v is None:
			player_entity = Player(index_from_userid(self.userid))
			return (player_entity.steamid, standardrace, player_entity.name, 0, time.time())

		return v

	def _setInfo(self, options):
		keys = []
		for option, value in options.items():
			keys.append((option+"='"+str(value)+"'"))

		database.execute("UPDATE Players SET " + ','.join(keys) + " WHERE UserID = ?", (self.UserID, ))

#Race functions
tmp2 = {}
def _getRace(userid, race, user):
	user = int(user)
	if not user in tmp2:
		tmp2[user] = {}

	if not race in tmp2[user]:
		tmp2[user][race] = Race(userid, race, user)

	return tmp2[user][race]

class Race(object):
	def __init__(self, UserID, race, user):
		self.userid     = user
		self.index = index_from_userid(self.userid)
		self.player_entity = Player(self.index)
		self.steamid    = self.player_entity.steamid
		if self.steamid == 'BOT':
			self.steamid == 'BOT_'+str(self.player_entity.name)
		self.UserID     = UserID
		self.player     = _getPlayer(self.userid, self.UserID)

		if not race in racedb:
            #tell(self.userid, 'main: race no found', {'race':race})
			#es.tell(self.userid, '#multi', '\x04It seems like your current race ('+race+') is \x05not \x04in the database.')
			#logging.log('wcs: Information: Unknown race ('+race+') found on UserID '+str(self.UserID))
			race = standardrace
			self.player.currace = standardrace

		self.RaceID     = database.getRaceIdFromUserIdAndRace(self.UserID, race)
		if self.RaceID is None:
			self.RaceID = database.addRaceIntoPlayer(self.UserID, race)

		self.racedb = racedb.getRace(race)

		self.update()
		self.refresh()

	def __contains__(self, race):
		if isinstance(race, int):
			database.execute("SELECT RaceID FROM Races WHERE UserID = ? AND RaceID = ?", (self.UserID, race))
		else:
			database.execute("SELECT RaceID FROM Races WHERE UserID = ? AND name = ?", (self.UserID, race))
		return database.fetchone()

	def update(self):
		self.name, self.skills, self.level, self.xp, self.unused = self._getInfo(('name',
																				  'skills',
																				  'level',
																				  'xp',
																				  'unused'))

	def save(self):
		try:
			self._setInfo({'name':self.name,
						  'skills':self.skills,
						  'level':self.level,
						  'xp':self.xp,
						  'unused':self.unused})
		except:
			return
			#logging.log('wcs: Information: Unable to set information for UserID '+str(self.UserID))
			#logging.log('wcs: Information: Error message: '+str(sys.exc_info()[1]))
			#logging.log('wcs: Information: Possible errors: '+str(self.name)+' '+str(self.skills)+' '+str(self.level)+' '+str(self.xp)+' '+str(self.unused))

	def refresh(self):
		if not self.skills or self.skills is None or self.skills == 'None':
			skills = []
			for x in range(1,10):
				skill = 'skill'+str(x)
				if skill in self.racedb:
					skills.append('0')

			self.skills = '|'.join(skills)

	def _getInfo(self, what):
		if not hasattr(what, '__iter__'):
			what = (what, )

		database.execute("SELECT "+','.join(map(str, what))+" FROM Races WHERE UserID = ? AND RaceID = ?", (self.UserID, self.RaceID))

		v = database.fetchone()
		if v is None:
			return (self.player.currace, '', 0, 0, 0)

		return v

	def _setInfo(self, options):
		keys = []
		for option, value in options.items():
			keys.append((option+"='"+str(value)+"'"))

		database.execute("UPDATE Races SET " + ','.join(keys) + " WHERE UserID = ? AND RaceID = ?", (self.UserID, self.RaceID))


	def addXp(self, amount, reason=''):
		amount = int(amount)
		if not amount:
			return

		maximumlevel = 1000 #Tha Pwned

		if 'maximumlevel' in self.racedb: #Tha Pwned
			maximumlevel = int(self.racedb['maximumlevel']) #Tha Pwned

		if self.level >= maximumlevel: #Tha Pwned
			return #Tha Pwned

		currentXp = self.xp + amount

		amountOfLevels = 0
		nextLevelXp = int(cfgdata['interval'])*self.level if self.level else int(cfgdata['interval'])

		while currentXp >= nextLevelXp:
			amountOfLevels += 1
			currentXp -= nextLevelXp
			nextLevelXp += int(cfgdata['interval'])

		self.xp = currentXp
		if not reason:
			tell(self.userid, '\x04[WCS] \x05You have gained \x04%s XP.' % amount)
		else:
			tell(self.userid, '\x04[WCS] \x05You have gained \x04%s XP %s' % (amount, reason))

		if amountOfLevels+self.level >= maximumlevel: #Tha Pwned
			amountOfLevels = maximumlevel-self.level #Tha Pwned
			
		if amountOfLevels:
			self.addLevel(amountOfLevels)

		event_instance = wcs.events.wcs_gainxp(userid=self.userid, amount=amount, levels=amountOfLevels, currentxp=self.xp,reason=reason)
		event_instance.fire()		
		
		return currentXp

	def addLevel(self, amount):
		amount = int(amount)
		if not amount:
			return
			
		maximumlevel = 1000 #Tha Pwned

		if 'maximumlevel' in self.racedb: #Tha Pwned
			maximumlevel = int(self.racedb['maximumlevel']) #Tha Pwned

		if self.level >= maximumlevel: #Tha Pwned
			return #Tha Pwned

		if amount+self.level >= maximumlevel: #Tha Pwned
			amount = maximumlevel-self.level #Tha Pwned
			
		self.level += amount
		self.unused += amount
		self.player.totallevel += amount

		if 'BOT' in self.steamid:
			maxlevel = int(self.racedb['numberoflevels'])

			while True:
				if not self.unused:
					break

				possibleChoices = []
				skills = self.skills.split('|')

				if len(skills):
					if skills[0] == '':
						self.raceUpdate()

				for skill, level in enumerate(skills):
					if int(skills[skill]) < maxlevel:
						possibleChoices.append(str(skill+1))

				if not len(possibleChoices):
					break

				choice = random.choice(possibleChoices)
				self.addPoint(choice)

		else:
			tell(self.userid, '\x04[WCS] \x05You are on level \x04%s\x05 XP: \x04%s/%s' % (self.level, self.xp, self.level*int(cfgdata['interval'])))
			Delay(2.0, spendskills.doCommand, (self.userid,))
			return
		oldlevel = self.level - amount
		event_instance = wcs.events.wcs_levelup(userid=self.userid, race=self.name, oldlevel=oldlevel, newlevel=self.level,amount=amount)
		event_instance.fire()	

		return self.level

	def addUnused(self, amount):
		self.unused += amount
		return self.unused

	def addPoint(self, skill):
		skills = self.skills.split('|')
		index = int(skill)-1
		level = int(skills[index])

		if self.unused:
			skills.pop(index)
			skills.insert(index, str(level+1))

			self.skills = '|'.join(skills)

			self.unused -= 1

			return level+1
			
@SayCommand('ultimate')
@ClientCommand('ultimate')
def _ultimate_command(command, index, team=None):
	userid = userid_from_index(index)
	player = getPlayer(userid)
	player_entity = Player(index)
	if int(player_entity.team) > 1 and not int(player_entity.dead):
		returned = checkEvent1(userid, 'player_ultimate')
		if returned is not None:
			if returned is False:
				tell(userid, 'You cannot activate your ultimate now.')
			elif len(returned) == 3 and not returned[0]:
				tell(userid, '\x04[WCS] \x05You cannot use your \x04ultimate! \x05Cooldown time is \x04'+str(returned[1])+' \x05seconds, \x04'+str(returned[1]-returned[2])+' \x05left!')

@Event('round_freeze_end')
def _event_freeze(ev):
	global gamestarted
	gamestarted = 1
	
                
@SayCommand('ability')
@ClientCommand('ability')
def _ultimate_command(command, index, team=None):
	userid = userid_from_index(index)
	player = getPlayer(userid)
	player_entity = Player(index)
	if int(player_entity.team) > 1 and not int(player_entity.dead):
		value = wcsgroup.getUser(userid, 'ability')
		if value == None:
			returned = checkEvent1(userid, 'player_ability')
			if returned is not None:
				if returned is False:
					tell(userid, '\x04[WCS] \x05You cannot activate your ability now.')
				elif len(returned) == 3 and not returned[0]:
					tell(userid, '\x04[WCS] \x05You cannot use your \x04ability! \x05Cooldown time is \x04'+str(returned[1])+' \x05seconds, \x04'+str(returned[1]-returned[2])+' \x05left!')
		else:
			if gamestarted == 1:
				es.ServerVar('wcs_userid').set(userid)
				es.doblock('wcs/tools/abilities/'+str(value)+'/'+str(value))
			else:
				tell(userid, '\x04[WCS] \x05You cannot activate your ability now.')
                
@SayCommand('wcsrank')
@ClientCommand('wcsrank')
def _wcs_rank_command(command, index, team=None):
    userid = userid_from_index(index)
    wcstop.wcsRank(userid)
    
@SayCommand('wcstop')
@ClientCommand('wcstop')
def _wcs_top_command(command, index, team=None):
    userid = userid_from_index(index)
    wcstop.doCommand(userid)

@ServerCommand('wcs_test')
def _wcs_test(command):
	races = racedb.getAll()
	print(len(races))
	
@ServerCommand('wcs_reload')
def _wcs_reload_command(command):
    load_races()
	
@ServerCommand('wcs_givexp')
def _wcs_givexp_command(command):
	userid = int(command[1])
	amount = int(command[2])
	player = getPlayer(userid)
	player.giveXp(amount)

@ServerCommand('wcs_givelevel')
def _wcs_givelevel_command(command):
	userid = int(command[1])
	amount = int(command[2])
	player = getPlayer(userid)
	player.giveLevel(amount)

@SayCommand('showxp')
@ClientCommand('showxp')
def _showxp_command(command, index, team=None):
		userid = userid_from_index(index)
		getPlayer(userid).showXp()


@SayCommand('wcsmenu')
@SayCommand('wcs')
@ClientCommand('wcsmenu')
@ClientCommand('wcs')
def _wcsmenu_command(command, index, team=None):
	userid = userid_from_index(index)
	wcsmenu.doCommand(userid)
		
@SayCommand('raceinfo')
@ClientCommand('raceinfo')
def _raceinfo_command(command, index, team= None):
	userid = userid_from_index(index)
	raceinfo.doCommand(userid)
	
@SayCommand('shopinfo')
@ClientCommand('shopinfo')
def _shopinfo_command(command, index, team= None):
	userid = userid_from_index(index)
	shopinfo.doCommand(userid)
		
@SayCommand('spendskills')
@ClientCommand('spendskills')
def _spendskills_command(command, index, team= None):
	userid = userid_from_index(index)
	spendskills.doCommand(userid)

@SayCommand('changerace')
@ClientCommand('changerace')
def _changerace_command(command, index, team=None):
	userid = userid_from_index(index)
	changerace.HowChange(userid)
	
@SayCommand('resetskills')
@ClientCommand('resetskills')
def _resetskills_command(command, index, team=None):
	userid = userid_from_index(index)
	resetskills.doCommand(userid)

@SayCommand('savexp')
@ClientCommand('savexp')
def _savexp_command(command, index, team=None):
	userid = userid_from_index(index)
	savexp.doCommand(userid)
	
@SayCommand('showskills')
@ClientCommand('showskills')
def _showskills_command(command, index, team=None):
	userid = userid_from_index(index)
	showskills.doCommand(userid)

@SayCommand('wcshelp')
@ClientCommand('wcshelp')
def _wcshlep_command(command, index, team=None):
	userid = userid_from_index(index)
	wcshelp.doCommand(userid)
	
@SayCommand('shopmenu')
@ClientCommand('shopmenu')
def _shopmenu_command(command, index, team=None):
	userid = userid_from_index(index)
	shopmenu.doCommand(userid)
	
@SayCommand('playerinfo')
@ClientCommand('playerinfo')
def _playerinfo_command(command, index, team=None):
	userid = userid_from_index(index)
	playerinfo.doCommand(userid)


#Events
@Event('player_changename')
def _player_changename(event):
	userid = event.get_int('userid')
	getPlayer(userid).player.name = database.removeWarnings(ev['newname'])

@Event('player_activate')	
def _player_activate(event):
	userid = event.get_int('userid')
	player = getPlayer(userid)
	player_entity = Player(index_from_userid(userid))
	player.player.name = database.removeWarnings(player_entity.name)
	if not player_entity.steamid == 'BOT':
		Delay(10.0, tell, (userid, '\x04[WCS] \x05Welcome to this \x04WCS server\x05. Try \x04"wcshelp" \x05and bind mouse3 ultimate'))

	wcsgroup.addUser(userid)

@Event('player_disconnect')	
def player_disconnect(event):
	userid = event.get_int('userid')
	player_entity = Player(index_from_userid(userid))

	if userid in tmp:
		tmp[userid].player.lastconnect = time.time()
		tmp[userid].player.name = database.removeWarnings(player_entity.name)
		tmp[userid].save()
		tmp1[userid].save()
		for x in tmp2[userid]:
			tmp2[userid][x].save()

		del tmp[userid]
		del tmp1[userid]
		del tmp2[userid]

	wcsgroup.delUser(userid)

@Event('round_start')
def round_start(event):
	freezetime = ConVar('mp_freezetime').get_int()
	if freezetime == 0:
		global gamestarted
		gamestarted = 1
	for player in PlayerIter():
		userid = player.userid
		if player.team >= 2:
			race = getPlayer(userid).player.currace
			raceinfo = racedb.getRace(race)
			if raceinfo['roundstartcmd']:
				command = raceinfo['roundstartcmd']
				command = command.split(";")
				ConVar("wcs_userid").set_int(userid)
				for com in command:
					execute_server_command('es', com)
				#command = re.sub(r"\bes\b","",command)
				#queue_command_string(command)
saved = 0

@Event('round_end')
def round_end(event):
	global gamestarted
	gamestarted = 0
	for player in PlayerIter():
		userid = player.userid
		queue_command_string('wcs_color %s 255 255 255 255' % userid)
		queue_command_string('wcs_setgravity %s 1.0' % userid)
		queue_command_string('es playerset speed %s 1.0' % userid)
		queue_command_string('es wcsgroup set regeneration_active %s 0' % userid)
		if player.team >= 2:
			race = getPlayer(userid).player.currace
			raceinfo = racedb.getRace(race)
			if raceinfo['roundendcmd']:
				command = raceinfo['roundendcmd']
				command = command.split(";")
				for com in command:
					execute_server_command('es', com)
				
	xpsaver = 5
	if xpsaver:
		global saved
		if xpsaver >= saved:
			for x in tmp:
				tmp[x].save()

			for x in tmp1:
				tmp1[x].save()

			for x in tmp2:
				for q in tmp2[x]:
					tmp2[x][q].save()

			database.save()
			saved = 0

		else:
			saved += 1
			
#player_death vars			
#short 	userid 	user ID who died
#short 	attacker 	user ID who killed
#short 	assister 	user ID who assisted in the kill
#string 	weapon 	weapon name killer used
#bool 	headshot 	singals a headshot
#short 	penetrated 	number of objects shot penetrated before killing target 
			
			
			
@Event('player_death')			
def player_death(event):
	#player_death variables
	victim = event.get_int('userid')
	attacker = event.get_int('attacker')
	assister = event.get_int('assister')
	headshot = event.get_int('headshot')
	weapon = event.get_string('weapon')
	queue_command_string('es wcsgroup set regeneration_active %s 0' % victim)
	
	#player_death execution
	victim_entity = Player(index_from_userid(victim))
	if attacker:
		attacker_entity = Player(index_from_userid(attacker))

	if attacker and victim:
		player = getPlayer(victim)

		if not victim == attacker:
			if not victim_entity.team == attacker_entity.team:
				player1 = getPlayer(attacker)
				bonus = 0
				if player1.race.level < player.race.level:
					diffience = player.race.level - player1.race.level
					bonus = diffience * int(cfgdata['bonusxp'])

				if bonus:
					Delay(1, player1.giveXp, (int(cfgdata['killxp'])+bonus, 'for killing a higher-level enemy. (\x04%s level difference bonus xp!)' % diffience))
				else:
					Delay(1, player1.giveXp, (int(cfgdata['killxp']), 'for making a kill'))

				if headshot == 1:
					Delay(1, player1.giveXp, (int(cfgdata['headshotxp']), 'for making a headshot'))
				elif weapon == 'knife':
					Delay(1, player1.giveXp, (int(cfgdata['knifexp']), 'for making a knife kill'))

			checkEvent(victim,  'player_death',other_userid=attacker, assister=assister, headshot=headshot,weapon=weapon)
			checkEvent(attacker, 'player_kill', other_userid=victim, assister=assister, headshot=headshot,weapon=weapon)

		if player.race.racedb['deathcmd']:
			command = player.race.racedb['deathcmd']
			command = command.split(";")
			for com in command:
				execute_server_command('es', com)
			#queue_command_string(command)

	if victim and not attacker:
		checkEvent(victim,  'player_death')

		
#player_hurt
#short 	userid 	user ID who was hurt
#short 	attacker 	user ID who attacked
#byte 	health 	remaining health points
#byte 	armor 	remaining armor points
#string 	weapon 	weapon name attacker used, if not the world
#short 	dmg_health 	damage done to health
#byte 	dmg_armor 	damage done to armor
#byte 	hitgroup 	hitgroup that was damaged ; 1=hs 2=upper torso 3=lower torso 4=left arm 5=right arm 6=left leg 7=right leg 

@Event('player_hurt')
def _player_hurt(event):
	#player_hurt variables
	victim = event.get_int('userid')
	attacker = event.get_int('attacker')
	health = event.get_int('health')
	armor = event.get_int('armor')
	weapon = event.get_string('weapon')
	dmg_health = event.get_int('dmg_health')
	dmg_armor = event.get_int('dmg_armor')
	hitgroup = event.get_int('hitgroup')
	
	
	if victim:
		victim_entity = Player(index_from_userid(victim))
	if attacker:
		attacker_entity = Player(index_from_userid(attacker))
	if attacker and victim and not weapon.lower() in ('point_hurt') and not weapon.lower() in ('worldspawn'):
		if not victim == attacker:
			if not victim_entity.team == attacker_entity.team:
				checkEvent(victim, 'player_victim', other_userid=attacker, health=health, armor=armor, weapon=weapon, dmg_health=dmg_health, dmg_armor=dmg_armor, hitgroup=hitgroup)
				if health > 0:
					checkEvent(attacker, 'player_attacker', other_userid=victim, health=health, armor=armor, weapon=weapon, dmg_health=dmg_health, dmg_armor=dmg_armor, hitgroup=hitgroup)
				
			checkEvent(victim, 'player_hurt', other_userid=attacker, health=health, armor=armor, weapon=weapon, dmg_health=dmg_health, dmg_armor=dmg_armor, hitgroup=hitgroup)
			if health > 0:
				checkEvent(attacker, 'player_hurt', other_userid=victim, health=health, armor=armor, weapon=weapon, dmg_health=dmg_health, dmg_armor=dmg_armor, hitgroup=hitgroup)

@Event('player_spawn')			
def _player_spawn(event):
	userid = event.get_int('userid')
	
	index = index_from_userid(userid)
	player_entity = Player(index)

	if userid and player_entity.team >= 2:
		for i, v in {'gravity':1.0,'speed':1.0,'longjump':1.0}.items():
			wcsgroup.setUser(userid, i, v)

		player_entity.gravity = 1.0
		player_entity.color = Color(255,255,255,255)


		player = getPlayer(userid)


		wcsgroup.addUser(userid)

		player.showXp()

		checkEvent(userid, 'player_spawn')

		race = player.player.currace
		raceinfo = racedb.getRace(race)
		if int(raceinfo['restrictteam']) and not player_entity.steamid == 'BOT':
			if player_entity.team == int(raceinfo['restrictteam']) and player_entity.team >= 2 and not player_entity.steamid == 'BOT':
				player_entity.team = 1
				changerace.HowChange(userid)

		elif 'teamlimit' in raceinfo and not player_entity.steamid == 'BOT':
			q = int(raceinfo['teamlimit'])
			if q:
				v = wcsgroup.getUser({2:'T',3:'CT'}[player_entity.team], 'restricted')
				if v == None:
					v = 0
				if v > q:
					player_entity.team = 1
					changerace.HowChange(userid)

		elif curmap in raceinfo['restrictmap'].split('|'):
			if not player_entity.steamid == 'BOT':
					player_entity.team = 1
					changerace.HowChange(userid)

		if raceinfo['spawncmd']:
			command = raceinfo['spawncmd']
			command = command.split(";")
			for com in command:
				execute_server_command('es', com)


@Event('player_say')			
def player_say(event):
	userid = event.get_int('userid')
	checkEvent(userid, 'player_say')

DATABASE_STORAGE_METHOD = SQLiteManager

raceevents = {}
aliass = {}
database = None
databasePath = Path(ini.path).joinpath('data')

def unload():
	tmp.clear()
	tmp1.clear()
	tmp2.clear()
	aliass.clear()
	database.save()
	database.close()

def load_races():
	races = racedb.getAll()	
	for race in races:
		for section in races[race]:
			if section == 'skillcfg':
				global raceevents
				raceevents = {}
				if not race in raceevents:
					raceevents[race] = {}

				events = races[race]['skillcfg'].split('|')

				for index, cfg in enumerate(events):
					if not cfg in raceevents[race]:
						raceevents[race][cfg] = []

					raceevents[race][cfg].append(str(index))

			elif section == 'preloadcmd':
				command = races[race]['preloadcmd']
				command = command.split(";")
				for com in command:
					execute_server_command('es', com)

def load():
	global database
	database = DATABASE_STORAGE_METHOD(databasePath)
	database.updateRank()
	global curmap
	curmap = ConVar("host_map")
	races = racedb.getAll()
	global aliass
	for race in races:
		for section in races[race]:
			if 'racealias_' in section:
				if section not in aliass:
					aliass[section] = str(races[race][section])

			if section == 'skillcfg':
				global raceevents
				if not race in raceevents:
					raceevents[race] = {}

				events = races[race]['skillcfg'].split('|')

				for index, cfg in enumerate(events):
					if not cfg in raceevents[race]:
						raceevents[race][cfg] = []

					raceevents[race][cfg].append(str(index))

			elif section == 'preloadcmd':
				command = races[race]['preloadcmd']
				command = command.split(";")
				for com in command:
					execute_server_command('es', com)

			if 'skill' in section:
				for y in races[race][section]:
					if 'racealias_' in y:
						if y not in aliass:
							aliass[y] = str(races[race][section][y])

	items = ini.getItems
	for section in items:
		for item in items[section]:
			for q in items[section][item]:
				if 'shopalias_' in q:
					if q not in aliass:
						aliass[q] = str(items[section][item][q])

@OnLevelShutdown
def level_shutdown_listener():
	for player in PlayerIter():
		userid = player.userid
		savexp.doCommand(userid)
	
	database.save()
	database.updateRank()
    
@OnLevelInit
def level_init_listener(mapname):
	allow_alpha = ConVar('sv_disable_immunity_alpha')
	allow_alpha.set_int(1)
	tmp.clear()
	queue_command_string('sp reload wcs')
	global curmap
	curmap = mapname
    
def execute_command(command,event, userid, other_userid=0, health=0, armor=0, weapon=0, dmg_health=0, dmg_armor=0, hitgroup=0,headshot = 0,assister=0):
	command = command.split(";")
	for com in command:
		execute_server_command('es', com)

	
def checkEvent(userid, event, other_userid=0, health=0, armor=0, weapon='', dmg_health=0, dmg_armor=0, hitgroup=0,assister=0,headshot=0):
	if userid is not None:
		player_entity = Player(index_from_userid(userid))
		if int(player_entity.team) > 1:
			player = getPlayer(userid)
			race = player.player.currace
			race1 = racedb.getRace(race)
			if event in raceevents[race]:
				skills = player.race.skills.split('|')
				for index in raceevents[race][event]:
					try:
						level = int(skills[int(index)])
					except IndexError:
						level = None
					if level:
						wcs_dice = ConVar('wcs_dice')
						wcs_dice.set_int(random.randint(0, 100))
						skill = 'skill'+str(int(index)+1)

						try:
							if race1[skill]['setting'].split('|')[level-1]:
								settings = race1[skill]['setting'].split('|')[level-1]
								if ';' in settings:
									sub_settings = settings.split(';')
									for com in sub_settings:
										execute_server_command('es', com)
								else:
									execute_server_command('es', settings)
						except IndexError:
							continue

						if 'cmd' in race1[skill]:
							if race1[skill]['cmd']:
								command = race1[skill]['cmd']
								command = command.split(";")
								for com in command:
									execute_server_command('es', com)					
						else:
							continue
						if 'sfx' in race1[skill]:
							if race1[skill]['sfx']:
								command = race1[skill]['sfx']
								command = command.split(";")
								for com in command:
									execute_server_command('es', com)	
							

def checkEvent1(userid, event):
	if userid is not None:
		player_entity = Player(index_from_userid(userid))
		if int(player_entity.team) > 1:
			player = getPlayer(userid)
			race = player.player.currace
			race1 = racedb.getRace(race)
			if event in raceevents[race]:
				skills = player.race.skills.split('|')
				index = raceevents[race][event][0]

				try:
					level = int(skills[int(index)])
				except IndexError:
					level = None
				if level:
					gamestarted = 1
					if gamestarted:
						wcs_dice = ConVar('wcs_dice')
						wcs_dice.set_int(random.randint(0, 100))
						skill = 'skill'+str(int(index)+1)
						cooldown = wcsgroup.getUser(userid, event+'_cooldown')
						if cooldown is None:
							cooldown = 0
						cooldown = int(cooldown)
						wcsgroup.setUser(userid, event+'_pre_cooldown', cooldown)
						timed = int(float(time.time()))
						downtime = str(race1[skill]['cooldown']).split('|')
						if len(downtime) == int(player.race.racedb['numberoflevels']):
							downtime = int(downtime[level-1])
						else:
							downtime = int(downtime[0])

						if not downtime or (timed - cooldown >= downtime):
							if race1[skill]['setting']:
								try:
									if race1[skill]['setting'].split('|')[level-1]:
										settings = race1[skill]['setting'].split('|')[level-1]
										if ';' in settings:
											sub_settings = settings.split(';')
											for com in sub_settings:
												execute_server_command('es', com)
										else:
											execute_server_command('es', settings)
								except IndexError:
									return

							if 'cmd' in race1[skill]:
								ConVar("wcs_userid").set_int(userid)
								if race1[skill]['cmd']:
									command = race1[skill]['cmd']
									command = command.split(";")
									for com in command:
										execute_server_command('es', com)
									#command = re.sub(r"\bes\b","",command)
									#queue_command_string(command)
							else:
								return
							if 'sfx' in race1[skill]:
								ConVar("wcs_userid").set_int(userid)
								if race1[skill]['sfx']:
									command = race1[skill]['sfx']
									command = command.split(";")
									for com in command:
										execute_server_command('es', com)

							wcsgroup.setUser(userid, event+'_cooldown', timed)
							#Success
							return (1, downtime, timed-cooldown)
						#Cooldown
						return (0, downtime, timed-cooldown)
					#Game has not started
					return False
	return None

@ServerCommand('wcs_xalias')
def _wcs_xalias_command(command):
	alias = str(command[1])
	if alias in aliass:
		todo = aliass[alias].split(";")
		for com in todo:
			execute_server_command('es', com)
	
@ServerCommand('wcs_reload_races')
def _wcs_reload_races_command(command):
	if not 'reload' in time:
		time['reload'] = time.time()

	if time.time()-time['reload'] <= 180:
		racedb.races = ini.getRaces
		time['reload'] = time.time()
	load_races()
	
	
@ServerCommand('wcs_get_skill_level')
def get_skill_level(command):
	userid = str(command[1])
	var = str(command[2])
	skillnum = int(command[3])
	
	player = getPlayer(userid)
	skills = player.race.skills.split('|')
	if skillnum <= len(skills):
		ConVar(var).set_string(skills[skillnum-1])
	
@ServerCommand('wcs_getinfo')
def getInfoRegister(command):
	if len(command) == 5:
		userid = str(command[1])
		var = str(command[2])
		info = str(command[3])
		where = str(command[4])
 
		player = getPlayer(userid)
 
		if where == 'race':
			if hasattr(player.race, info):
				returned = getattr(player.race, info)
				ConVar(var).set_string(str(returned))
 
		elif where == 'player':
			if hasattr(player.player, info):
				returned = getattr(player.player, info)
				ConVar(var).set_string(str(returned))
		else:
			if not where in racedb:
				return
 
			v = _getRace(player.player.UserID, info, userid)
			if hasattr(v, info):
				returned = getattr(v, info)
				ConVar(var).set_string(str(returned))
				
@OnTick
def on_tick():
	if keymenu.get_int() == 1:
		for player in PlayerIter('all'):
			user_queue = PagedMenu.get_user_queue(player.index)
			if user_queue.active_menu is None:
				userid = player.userid
				p = getPlayer(userid)

				race = p.player.currace
				totallevel = p.player.totallevel
				level = p.race.level
				xp = p.race.xp
				needed = int(interval.get_int())*level if level else int(interval.get_int())
				steamid = player.steamid
				if steamid == 'BOT':
					steamid == 'BOT_'+str(player.name)
				rank = database.getRank(steamid)
				text = str(race)+'\n--------------------\nTotallevel: '+str(totallevel)+'\nLevel: '+str(level)+'\nXp: '+str(xp)+'/'+str(needed)+'\n--------------------\nWCS rank: '+str(rank)+'/'+str(len(database))
				HudMsg(text, 0.025, 0.4,hold_time=0.2).send(player.index)
