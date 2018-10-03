# =============================================================================
# >> IMPORTS
# =============================================================================
#Python
from base64 import encodestring as estr, decodestring as dstr
from configobj import ConfigObj
import os
from path import Path
from queue import Empty, Queue
import random
from random import choice
from sqlite3 import dbapi2 as sqlite
import string
import sys
from threading import Thread
import time

#SourcePython
from colors import Color
from commands import CommandReturn
from commands.say import SayCommand
from commands.client import ClientCommand
from commands.server import ServerCommand
from contextlib import contextmanager
import core
from core import SOURCE_ENGINE_BRANCH
from cvars import ConVar
from engines.server import execute_server_command, queue_command_string
from entities.helpers import index_from_edict
from events import Event
from events.hooks import PreEvent, EventAction
from filters.players import PlayerIter
from listeners import ListenerManager
from listeners import ListenerManagerDecorator
from listeners import OnTick, OnLevelInit, OnLevelShutdown, OnClientActive
from listeners.tick import Delay, Repeat

from messages import HudMsg, SayText2, HintText, KeyHintText
from menus import PagedMenu
from menus import PagedOption
from menus import SimpleMenu
from menus import SimpleOption
from menus import Text
from paths import PLUGIN_PATH
from players.dictionary import PlayerDictionary
from players.entity import Player
from players.helpers import index_from_userid, userid_from_index,userid_from_edict,index_from_steamid
from translations.strings import LangStrings

#Eventscripts Emulator
import es

#SQL Alchemy
from sqlalchemy import Column, ForeignKey, Integer, String, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.expression import insert
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, desc

#Warcraft Source
from wcs import admin
from wcs import changerace
from wcs import commands
from wcs import config
from wcs import downloader
from wcs import effects
import wcs.events
from wcs import firefix
from wcs import ladderfix
from wcs import levelbank
from wcs import logging
from wcs import longjump
from wcs import mana
from wcs import myinfo
from wcs import playerinfo
from wcs import raceinfo
from wcs import randomrace
from wcs import resetskills
from wcs import restrictions
from wcs import savexp
from wcs import setfx
from wcs import shopinfo
from wcs import shopmenu
from wcs import showitems
from wcs import showskills
from wcs import spendskills
from wcs import svar
from wcs import teamrestrictions
from wcs import vip
from wcs import wcs_commands
from wcs import wcsgroup
from wcs import wcshelp
from wcs import wcsmenu
from wcs import wcstop
from wcs import xtell

color_codes = ['\x03', '\x04', '\x05', '\x06', '\x07']
raceevents = {}
aliass = {}
item_names = []
player_loaded = {}
output = Queue()
wcsplayers = {}
wcs_rank = {}
player_isdead = {}
gamestarted = 0
saved = 0

if os.path.isfile(os.path.join(PLUGIN_PATH, 'wcs/strings', 'strings.ini')):
	strings = LangStrings(os.path.join(PLUGIN_PATH, 'wcs/strings', 'strings'))
	
@contextmanager
def session_scope():
	session = Session()
	try:
		yield session
		session.commit()
	except:
		session.rollback()
		raise
	finally:
		session.close()
	
# =============================================================================
# >> DATABASE
# =============================================================================	
Base = declarative_base()
db_method = ConVar('wcs_database_connectstring').get_string()
engine = create_engine(db_method)

class Races(Base):
	__tablename__ = 'Races'
	RaceID = Column(Integer, nullable=False, primary_key=True)
	UserID = Column(Integer, nullable=False)
	name = Column(String(50),nullable=False)
	skills = Column(String(50),nullable=False)
	level = Column(Integer,default=0)
	xp = Column(Integer,default=0)
	unused = Column(Integer,default=0)
	Index('racesIndex',UserID)
 
class Players(Base):
	__tablename__ = 'Players'
	UserID = Column(Integer,nullable=False,primary_key=True)
	steamid = Column(String(30),nullable=False)
	currace = Column(String(30),nullable=False)
	name = Column(String(30),nullable=False)
	totallevel = Column(Integer,default=0)
	lastconnect = Column(Integer)
	Index('playersIndex', steamid)

if not engine.dialect.has_table(engine, 'Players'):
	Base.metadata.create_all(engine)
	
Session = sessionmaker(bind=engine)

# =============================================================================
# >> LOAD
# =============================================================================	
def load():
	Thread(target=_load_ranks).start()
	for player in PlayerIter():
		wcsplayers[player.userid] = WarcraftPlayer(player.userid)
		player_isdead[player.userid] = 0
	global curmap
	curmap = ConVar("host_map").get_string().strip('.bsp')
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
				if races[race]['preloadcmd'] != "":
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
	if config.coredata['saving'] == 1:
		repeat_delay = config.coredata['save_time']*60
		repeat = Repeat(do_save)
		repeat.start(repeat_delay)
		
# =============================================================================
# >> UNLOAD
# =============================================================================	
def unload():
	aliass.clear()
	
# =============================================================================
# >> INI MANAGER
# =============================================================================
class InI(object):
	def __init__(self):
		if os.path.isfile(os.path.join(PLUGIN_PATH, 'wcs/races', 'races.ini')):
			self.races = os.path.join(PLUGIN_PATH, 'wcs/races', 'races.ini')
		else:
			self.races = None
		if config.coredata['default_races'] == 1:
			self.default_races = os.path.join(PLUGIN_PATH, 'wcs/races', 'default_races.ini')
		else:
			self.default_races = None
		self.items = os.path.join(PLUGIN_PATH, 'wcs/items', 'items.ini')

	@property
	def getRaces(self):
		try:
			if self.races != None:
				user_races = ConfigObj(self.races,encoding="utf-8")
			else:
				user_races = {}
			if self.default_races != None:
				def_races = ConfigObj(self.default_races,encoding="utf-8")
			else:
				def_races = {}
			races_dict = {**def_races,**user_races}
			return ConfigObj(races_dict,encoding="utf-8")
		except:
			sys.excepthook(*sys.exc_info())
			return

	@property
	def getItems(self):
		return ConfigObj(self.items,encoding="utf-8")
	
	@property
	def getCats(self):
		return ConfigObj(self.cats,encoding="utf-8")			
ini = InI()

# =============================================================================
# >> INI CLASSES
# =============================================================================
#ITEMS DATABASE
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

#RACE DATABASE
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

list_of_str_keys = ["restrictmap","restrictteam","restrictitem","spawncmd","deathcmd","roundstartcmd","roundendcmd","preloadcmd","onchange","allowonly"]
list_of_int_keys = ["teamlimit"]
for race in racedb.getAll():
	for key in list_of_str_keys:
		if key not in racedb.getAll()[race]:
			racedb.getAll()[race][key] = ""
	for key in list_of_int_keys:
		if key not in racedb.getAll()[race]:
			racedb.getAll()[race][key] = 0

if len(racedb.getAll()):
	standardrace = racedb.getAll().keys()[0]
	ConVar('wcs_default_race').set_string(standardrace)
	

# =============================================================================
# >> PLAYER CLASS
# =============================================================================
class WarcraftPlayer(object):
	def __init__(self,userid):
		self.userid = int(userid)
		self.player_entity = Player.from_userid(self.userid)
		self.index = self.player_entity.index
		self.steamid = self.player_entity.uniqueid
		self.name = self.remove_warnings(self.player_entity.name)
			
		#Dict to check for load status
		player_loaded[self.userid] = False
		
		#Dict to store all the players races:
		self.all_races = {}
			
		#Player data
		self.UserID = -1
		self.currace = ""
		self.totallevel = 0
		self.lastconnect = -1
		
		
		#Race data
		self.RaceID = -1
		self.level = -1
		self.xp = -1
		self.unused = -1
		self.skills = ''
		self.race_name = ''
				
		Thread(target=self._load_from_database).start()
		
	def _load_from_database(self):
		with session_scope() as session:
			#Player data
	
			player = session.query(Players).filter(Players.steamid==self.steamid).one_or_none()
			if player is None:
				player = Players(steamid=self.steamid,currace=ConVar('wcs_default_race').get_string(),name=self.name,lastconnect=time.time())
				session.add(player)
				session.commit()
			self.UserID = player.UserID
			self.currace = player.currace
			self.race_name = self.currace
			self.totallevel = player.totallevel
			self.lastconnect = player.lastconnect
			if self.steamid not in wcs_rank:
				wcs_rank[self.steamid] = {}
				wcs_rank[self.steamid]['name'] = self.name
				wcs_rank[self.steamid]['totallevel'] = self.totallevel
				wcs_rank[self.steamid]['currace'] = self.currace
				wcs_rank[self.steamid]['level'] = 0
			#Race data
			try:
				race = session.query(Races).filter(Races.UserID==self.UserID,Races.name==self.currace).one_or_none()
			except:
				races = session.query(Races).filter(Races.UserID==self.UserID,Races.name==self.currace).all()
				session.delete(races[1])
				session.commit()
				race = races[0]
			if race is None:
				if self.skills == '':
					skills = []
					for x in range(1,10):
						skill = 'skill'+str(x)
						if skill in racedb.races[self.race_name]:
							skills.append('0')

					self.skills = '|'.join(skills)
					
				race = Races(UserID=self.UserID,name=self.race_name,skills=self.skills)
				session.add(race)
				session.commit()
			self.RaceID = race.RaceID
			self.level = race.level
			self.xp = race.xp
			self.unused = race.unused
			self.skills = race.skills
			self.race_name = race.name

			#Storing all saved races in the all_races dict
			races = session.query(Races).filter(Races.UserID==self.UserID).all()
			if races:
				for race_ in races:
					self.all_races[race_.name] = {}
			for race in self.all_races:
				try:
					info = session.query(Races).filter(Races.UserID==self.UserID,Races.name==race).one_or_none()
				except:
					infos = session.query(Races).filter(Races.UserID==self.UserID,Races.name==race).all()
					session.delete(infos[1])
					session.commit()
					info = infos[0]					
				self.all_races[race]['level'] = info.level
				self.all_races[race]['xp'] = info.xp
				self.all_races[race]['unused'] = info.unused
				self.all_races[race]['skills'] = info.skills
				self.all_races[race]['name'] = race
				
		output.put(self._on_finish)
		
	def _on_finish(self):
		if exists(self.userid):
			OnPlayerLoaded.manager.notify(self)	
			
	def save(self):
		if exists(self.userid):		
			Thread(target=self._save_player_to_database).start()
		
	def _save_player_to_database(self):
		with session_scope() as session:
			player = session.query(Players).filter(Players.UserID==self.UserID).one_or_none()
			player.steamid = self.steamid
			player.currace = self.currace
			player.name = self.name
			player.totallevel = self.totallevel
			player.lastconnect = self.lastconnect
			
			session.commit()
			for race_ in self.all_races:
				race = session.query(Races).filter(Races.UserID==self.UserID,Races.name==race_).one_or_none()
				if not race:
					race = Races(UserID=self.UserID,name=race_,skills=self.all_races[race_]['skills'])
					session.add(race)
					session.commit()
				race.name = race_
				race.skills = self.all_races[race_]['skills']
				race.level = self.all_races[race_]['level']
				race.xp = self.all_races[race_]['xp']
				race.unused = self.all_races[race_]['unused']
				session.commit()
		output.put(self._on_player_saved)
		
	def _on_player_saved(self):
		if exists(self.userid):
			OnPlayerSaved.manager.notify(self)		
		
	def remove_warnings(self, value):
		return str(value).replace("'", "").replace('"', '')
		
	def show_xp(self):
		xp		   = self.all_races[self.currace]['xp']
		level	   = self.all_races[self.currace]['level']
		if config.cfgdata['experience_system'] == 0:
			needed	   = config.cfgdata['interval']*level if level else config.cfgdata['interval']
		elif config.cfgdata['experience_system'] == 1:
			level_string = config.cfgdata['custom_system'].split(',')
			if level < len(level_string):
				needed = int(level_string[level])
			else:
				needed = int(level_string[len(level_string)-1])
		race	   = self.currace

		tell(self.userid, '\x04[WCS] \x04%s \x05 - Level: \x04%s \x05 - XP: \x04%s/%s' % (race, level, xp, needed))
	
	def changerace(self, race, kill=True,who=None,safe=False):
		if safe == False:
			if racedb.races[self.race_name]['onchange']:
				command = racedb.races[self.race_name]['onchange']
				command = command.split(";")
				for com in command:
					execute_server_command('es', com)
		oldrace = self.currace

		self.currace = str(race)
		wcs_rank[self.steamid]['currace'] = str(race)
		
		if self.currace not in self.all_races:
			self.all_races[self.currace] = {}
			self.all_races[self.currace]['level'] = 0
			self.all_races[self.currace]['xp'] = 0
			self.all_races[self.currace]['unused'] = 0
			
			skill_list = []
			for x in range(1,10):
				skill = 'skill'+str(x)
				if skill in racedb.races[self.currace]:
					skill_list.append('0')
			skills = '|'.join(skill_list)
			self.all_races[self.currace]['skills'] = skills

		self.level = self.all_races[self.currace]['level']
		self.xp = self.all_races[self.currace]['xp']
		self.unused = self.all_races[self.currace]['unused']
		self.skills = self.all_races[self.currace]['skills']
		if kill:
			self.player_entity.client_command("kill", True)
		if who == None:
			tell(self.player_entity.userid, '\x04[WCS] \x05You changed your race to \x04%s.' % race)
		if who == 'admin':
			tell(self.player_entity.userid,'\x04[WCS] \x05An admin set your race to \x04%s.' % race)
		if config.coredata['race_in_tag'] == 1:
			self.player_entity.clan_tag = race
		event_instance = wcs.events.wcs_changerace(userid=self.userid, oldrace=oldrace, newrace=race)
		event_instance.fire()
		
	def give_xp(self, amount, reason=''):
		amount = int(amount)
		if not amount:
			return

		maximumlevel = config.cfgdata['maximum_level']

		if 'maximumlevel' in racedb.races[self.currace]: #Tha Pwned
			maximumlevel = int(racedb.races[self.currace]['maximumlevel']) #Tha Pwned

		if self.all_races[self.currace]['level'] >= maximumlevel: #Tha Pwned
			return #Tha Pwned

		current_xp = self.all_races[self.currace]['xp'] + amount

		amount_of_levels = 0
		
		
		if config.cfgdata['experience_system'] == 0:
			next_level_xp = config.cfgdata['interval']*self.all_races[self.currace]['level'] if self.all_races[self.currace]['level'] else config.cfgdata['interval']
		elif config.cfgdata['experience_system'] == 1:
			level_string = config.cfgdata['custom_system'].split(',')
			if self.all_races[self.currace]['level'] < len(level_string):
				next_level_xp = int(level_string[self.all_races[self.currace]['level']])
			else:
				next_level_xp = int(level_string[len(level_string)-1])
				
				
		if config.cfgdata['experience_system'] == 0:
			while current_xp >= next_level_xp:
				amount_of_levels += 1
				current_xp -= next_level_xp
				next_level_xp += config.cfgdata['interval']
		elif config.cfgdata['experience_system'] == 1:
			x = 0
			level_string = config.cfgdata['custom_system'].split(',')
			while current_xp >=next_level_xp:
				amount_of_levels += 1
				current_xp -= next_level_xp
				if self.all_races[self.currace]['level']+x < len(level_string):
					next_level_xp = int(level_string[self.all_races[self.currace]['level']+x])
				else:
					next_level_xp = int(level_string[len(level_string)-1])
				x += 1
		self.all_races[self.currace]['xp'] = current_xp
		if not reason:
			tell(self.userid, '\x04[WCS] \x05You have gained \x04%s XP.' % amount)
		else:
			tell(self.userid, '\x04[WCS] \x05You have gained \x04%s XP %s' % (amount, reason))

		if amount_of_levels+self.all_races[self.currace]['level'] >= maximumlevel: #Tha Pwned
			amount_of_levels = maximumlevel-self.all_races[self.currace]['level'] #Tha Pwned
			
		if amount_of_levels:
			self.give_level(amount_of_levels)

		event_instance = wcs.events.wcs_gainxp(userid=self.userid, amount=amount, levels=amount_of_levels, currentxp=self.xp,reason=reason)
		event_instance.fire()		
		
		return current_xp
		
	def give_level(self, amount):
		amount = int(amount)
		if not amount:
			return
			
		maximumlevel = config.cfgdata['maximum_level']

		if 'maximumlevel' in racedb.races[self.currace]: #Tha Pwned
			maximumlevel = int(racedb.races[self.currace]['maximumlevel']) #Tha Pwned

		if self.all_races[self.currace]['level'] >= maximumlevel: #Tha Pwned
			return #Tha Pwned

		if amount+self.all_races[self.currace]['level'] >= maximumlevel: #Tha Pwned
			amount = maximumlevel-self.all_races[self.currace]['level'] #Tha Pwned
			
		self.all_races[self.currace]['level'] += amount
		self.all_races[self.currace]['unused'] += amount
		self.totallevel += amount
		wcs_rank[self.steamid]['totallevel'] += amount

		if 'BOT' in self.steamid:
			nol = racedb.races[self.currace]['numberoflevels']
			nos = racedb.races[self.currace]['numberofskills']
			if '|' in nol:
				nol = nol.split('|')
				nol = [int(x) for x in nol]
			else:
				nos = int(racedb.races[self.currace]['numberofskills'])
				nol_tmp = int(racedb.races[self.currace]['numberoflevels'])
				nol = []
				x = 0
				while x < nos:
					nol.append(nol_tmp)
					x += 1

			while True:
				if not self.all_races[self.currace]['unused']:
					break

				possible_choices = []
				skills = self.all_races[self.currace]['skills'].split('|')

				for skill, level in enumerate(skills):
					if int(skills[skill]) < nol[skill]:
						possible_choices.append(str(skill+1))

				if not len(possible_choices):
					break

				choice = random.choice(possible_choices)
				self.add_point(choice)

		else:
			if config.cfgdata['experience_system'] == 0:
				needed = config.cfgdata['interval']*self.all_races[self.currace]['level']
			elif config.cfgdata['experience_system'] == 1:
				level_string = config.cfgdata['custom_system'].split(',')
				if self.all_races[self.currace]['level'] < len(level_string):
					needed = int(level_string[self.all_races[self.currace]['level']])
				else:
					needed = int(level_string[len(level_string)-1])
			tell(self.userid, '\x04[WCS] \x05You are on level \x04%s\x05 XP: \x04%s/%s' % (self.all_races[self.currace]['level'], self.all_races[self.currace]['xp'], needed))
			Delay(2.0, spendskills.doCommand, (self.userid,))
			return
		oldlevel = self.all_races[self.currace]['level'] - amount
		event_instance = wcs.events.wcs_levelup(userid=self.userid, race=self.name, oldlevel=oldlevel, newlevel=self.all_races[self.currace]['level'],amount=amount)
		event_instance.fire()	

		return self.all_races[self.currace]['level']
		

	def add_point(self, skill):
		skills = self.all_races[self.currace]['skills'].split('|')
		index = int(skill)-1
		level = int(skills[index])

		if self.all_races[self.currace]['unused']:
			skills.pop(index)
			skills.insert(index, str(level+1))

			self.all_races[self.currace]['skills'] = '|'.join(skills)

			self.all_races[self.currace]['unused'] -= 1

			return level+1
			
	def get_rank(self):
		rank_list = wcs_rank.values()
		rank_list = sorted(wcs_rank, key=lambda x: wcs_rank[x]['totallevel'],reverse=True)
		i = 0
		for x in rank_list:
			i+=1
			if self.steamid == x:
				rank = i
				break
		return (i,len(rank_list))
		
	def show_rank(self):
		rank,total = self.get_rank()
		if config.cfgdata['experience_system'] == 0:
			needed	   = config.cfgdata['interval']*self.level if self.level else config.cfgdata['interval']
		elif config.cfgdata['experience_system'] == 1:
			level_string = config.cfgdata['custom_system'].split(',')
			if self.level < len(level_string):
				needed = int(level_string[self.level])
			else:
				needed = int(level_string[len(level_string)-1])
		unused	   = self.unused
		for player in PlayerIter('all'):
			tell(player.userid, "\x04[WCS] \x05%s \x04is on race \x05%s \x04level\x05 %s\x04, ranked \x05%s/%s \x04with\x05 %s/%s \x04XP and \x05%s \x04Unused." % (self.name, self.currace, self.all_races[self.currace]['level'], rank, total, self.all_races[self.currace]['xp'], needed, self.all_races[self.currace]['unused']))
		
	def delete_race(self):
		Thread(target=self._delete_race).start()

	def _delete_race(self):
		with session_scope() as session:
			delete = session.query(Races).filter(Races.UserID==self.UserID,Races.name==self.currace).one_or_none()
			if delete != None:
				session.delete(delete)
				session.commit()
			else:
				self.totallevel -= self.all_races[self.currace]['level']
				self.all_races[self.currace] = {}
				self.all_races[self.currace]['level'] = 0
				self.all_races[self.currace]['xp'] = 0
				self.all_races[self.currace]['unused'] = 0
				
				skill_list = []
				for x in range(1,10):
					skill = 'skill'+str(x)
					if skill in racedb.races[self.currace]:
						skill_list.append('0')
				skills = '|'.join(skill_list)
				self.all_races[self.currace]['skills'] = skills
				
				
		output.put(self._on_race_deleted)
	
	def _on_race_deleted(self):
		if exists(self.userid):
			OnRaceDeleted.manager.notify(self.index,self.currace)
		
	def delete_player(self):
		wcsplayers.pop(self.userid)
		Thread(target=self._delete_player).start()
		
	def _delete_player(self):
		with session_scope() as session:
			delete_races = session.query(Races).filter(Races.UserID==self.UserID).all()
			delete = session.query(Players).filter(Players.UserID==self.UserID).one_or_none()
			for x in delete_races:
				session.delete(x)
			session.delete(delete)
			session.commit()
		output.put(self._on_player_deleted)
		
	def _on_player_deleted(self):
		if exists(self.userid):
			OnPlayerDeleted.manager.notify(self.index)	
			
		
		
for player in PlayerIter('all'):
	wcsplayers[player.userid] = WarcraftPlayer(player.userid)
		
@Repeat
def repeat():
	try:
		callback = output.get_nowait()
	except Empty:
		pass
	else:
		callback()
repeat.start(0.1)
			
# =============================================================================
# >> PLAYER COMMANDS
# =============================================================================
@SayCommand(config.ultimate_list)
@ClientCommand(config.ultimate_list)
def _ultimate_command(command, index, team=None):
	userid = userid_from_index(index)
	player_entity = Player(index)
	if int(player_entity.team) > 1 and not int(player_entity.dead):
		returned = checkEvent1(userid, 'player_ultimate')
		if returned is not None:
			if returned is False:
				tell(userid, 'You cannot activate your ultimate now.')
			elif len(returned) == 3 and not returned[0]:
				tell(userid, '\x04[WCS] \x05You cannot use your \x04ultimate! \x05Cooldown time is \x04'+str(returned[1])+' \x05seconds, \x04'+str(returned[1]-returned[2])+' \x05left!')
	return CommandReturn.BLOCK
	
		
@SayCommand(config.ability_list)
@ClientCommand(config.ability_list)
def _ultimate_command(command, index, team=None):
	userid = userid_from_index(index)
	player_entity = Player(index)
	if int(player_entity.team) > 1 and not int(player_entity.dead):
		value = wcsgroup.getUser(userid, 'ability')
		if value == "None":
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
	return CommandReturn.BLOCK
	
@SayCommand(config.wcsrank_list)
@ClientCommand(config.wcsrank_list)
def _wcs_rank_command(command, index, team=None):
	userid = userid_from_index(index)
	wcstop.wcsRank(userid)
	return CommandReturn.BLOCK
	
@SayCommand(config.wcstop_list)
@ClientCommand(config.wcstop_list)
def _wcs_top_command(command, index, team=None):
	userid = userid_from_index(index)
	wcstop.doCommand(userid)
	return CommandReturn.BLOCK

@SayCommand(config.showxp_list)
@ClientCommand(config.showxp_list)
def _showxp_command(command, index, team=None):
		userid = userid_from_index(index)
		wcsplayers[userid].show_xp()
		return CommandReturn.BLOCK

@SayCommand(config.wcsmenu_list)
@ClientCommand(config.wcsmenu_list)
def _wcsmenu_command(command, index, team=None):
	userid = userid_from_index(index)
	wcsmenu.doCommand(userid)
	return CommandReturn.BLOCK
		
@SayCommand(config.raceinfo_list)
@ClientCommand(config.raceinfo_list)
def _raceinfo_command(command, index, team= None):
	userid = userid_from_index(index)
	raceinfo.doCommand(userid)
	return CommandReturn.BLOCK
	
@SayCommand(config.shopinfo_list)
@ClientCommand(config.shopinfo_list)
def _shopinfo_command(command, index, team= None):
	userid = userid_from_index(index)
	shopinfo.doCommand(userid)
	return CommandReturn.BLOCK
		
@SayCommand(config.spendskills_list)
@ClientCommand(config.spendskills_list)
def _spendskills_command(command, index, team= None):
	userid = userid_from_index(index)
	spendskills.doCommand(userid)
	return CommandReturn.BLOCK

@SayCommand(config.changerace_list)
@ClientCommand(config.changerace_list)
def _changerace_command(command, index, team=None):
	userid = userid_from_index(index)
	if not command.arg_string:
		changerace.HowChange(userid)
	else:
		changerace.HowChange(userid,command.arg_string)
	return CommandReturn.BLOCK
	
@SayCommand(config.resetskills_list)
@ClientCommand(config.resetskills_list)
def _resetskills_command(command, index, team=None):
	userid = userid_from_index(index)
	resetskills.doCommand(userid)
	return CommandReturn.BLOCK

@SayCommand(config.savexp_list)
@ClientCommand(config.savexp_list)
def _savexp_command(command, index, team=None):
	userid = userid_from_index(index)
	savexp.doCommand(userid)
	return CommandReturn.BLOCK
	
@SayCommand(config.showskills_list)
@ClientCommand(config.showskills_list)
def _showskills_command(command, index, team=None):
	userid = userid_from_index(index)
	showskills.doCommand(userid)
	return CommandReturn.BLOCK

@SayCommand(config.wcshelp_list)
@ClientCommand(config.wcshelp_list)
def _wcshlep_command(command, index, team=None):
	userid = userid_from_index(index)
	wcshelp.doCommand(userid)
	return CommandReturn.BLOCK
	
@SayCommand(config.shopmenu_list)
@ClientCommand(config.shopmenu_list)
def _shopmenu_command(command, index, team=None):
	userid = userid_from_index(index)
	shopmenu.doCommand(userid)
	return CommandReturn.BLOCK
	
@SayCommand(config.playerinfo_list)
@ClientCommand(config.playerinfo_list)
def _playerinfo_command(command, index, team=None):
	userid = userid_from_index(index)
	playerinfo.doCommand(userid)
	return CommandReturn.BLOCK
		
def buyitem_menu_select(menu, index, choice):
	userid = userid_from_index(index)
	shopmenu.addItem(userid, choice.value, pay=True, tell=True,close_menu=True)
		
@SayCommand(config.wcsbuyitem_list)
@ClientCommand(config.wcsbuyitem_list)
def wcs_buy_item(command,index,team=None):
	userid = userid_from_index(index)
	if len(command) < 2:
		return
	if len(command) > 2:
		item = command[1]
		for x in command:
			if x != "wcsbuyitem" and x != command[1]:
				item = item+" "+x
	else:
		item = str(command[1])
	items = find_items(item)
	if items != -1:
		if len(items) == 1:
			shopmenu.addItem(userid, items[0], pay=True, tell=True,close_menu=True)
		if len(items) > 1:
			buyitem_menu = PagedMenu(title='Choose item',select_callback=buyitem_menu_select,fill=False)
			buyitem_menu.clear()
			for i in items:
				iteminfo = itemdb.getItem(i)
				option = PagedOption('%s - %s$' % (str(iteminfo['name']), str(iteminfo['cost'])), i)
				buyitem_menu.append(option)
			buyitem_menu.send(index)
	return CommandReturn.BLOCK
	
# =============================================================================
# >> SERVER COMMANDS
# =============================================================================		
@ServerCommand('wcs_changerace')
def _wcs_changerace(command):
	userid = int(command[1])
	if len(command) > 3:
		race = command[2]
		for x in command:
			if x != "wcs_changerace" and not is_number(x) and x != command[2]:
				race = race+" "+x
	else:
		race = str(command[2])
	wcsplayers[userid].changerace(race)
	
	
@ServerCommand('wcs_reload')
def _wcs_reload_command(command):
	load_races()
	
@ServerCommand('wcs_givexp')
def _wcs_give_xp_command(command):
	userid = int(command[1])
	amount = int(command[2])
	wcsplayers[userid].give_xp(amount)

@ServerCommand('wcs_givelevel')
def _wcs_givelevel_command(command):
	userid = int(command[1])
	amount = int(command[2])
	wcsplayers[userid].give_level(amount)
	
@ServerCommand('wcs_xalias')
def _wcs_xalias_command(command):
	alias = str(command[1])
	if len(command) == 2:
		if alias in aliass:
			todo = aliass[alias].split(";")
			for com in todo:
				execute_server_command('es', com)
	elif len(command) == 3:
		aliass[alias] = str(command[2])
	
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
	
	skills = wcsplayers[userid].all_races[race]['skills'].split('|')
	if skillnum <= len(skills):
		ConVar(var).set_string(skills[skillnum-1])
		
	
@ServerCommand('wcs_getinfo')
def getInfoRegister(command):
	if len(command) == 5:
		userid = int(command[1])
		var = str(command[2])
		info = str(command[3])
		where = str(command[4])
		race = wcsplayers[userid].currace
 
		if where == 'race':
			if info in wcsplayers[userid].all_races[race]:
				returned = wcsplayers[userid].all_races[race][info]
				ConVar(var).set_string(str(returned))
 
		elif where == 'player':
			if hasattr(wcsplayers[userid], info):
				returned = getattr(wcsplayers[userid], info)
				ConVar(var).set_string(str(returned))
		else:
			if not where in racedb:
				return
 
			if info in wcsplayers[userid].all_races[where]:
				returned = wcsplayers[userid].all_races[where][info]
				ConVar(var).set_string(str(returned))
	
# =============================================================================
# >> EVENTS
# =============================================================================	
@Event('player_activate')	
def _player_activate(event):
	userid = int(event['userid'])
	player_entity = Player(index_from_userid(userid))
	wcsplayers[userid].name = wcsplayers[userid].remove_warnings(player_entity.name)

	if not player_entity.steamid == 'BOT':
		Delay(10.0, tell, (userid, '\x04[WCS] \x05Welcome to this \x04WCS server\x05. Try \x04"wcshelp" \x05and bind mouse3 ultimate'))
	race = wcsplayers[userid].currace
	if player_loaded[userid] == True:
		raceinfo = racedb.races[race]
		if raceinfo['allowonly'] != "":
			if not player_entity.steamid in raceinfo['allowonly']:
				rand_race = get_random_race(int(userid))
				player.changerace(rand_race)
		player_entity.clan_tag = race
	wcsgroup.addUser(userid)
	if SOURCE_ENGINE_BRANCH == 'csgo':
		delay = ConVar('mp_force_pick_time').get_int()
		Delay(float(delay),set_team,(event['userid'],))

@Event('round_freeze_end')
def _event_freeze(ev):
	global gamestarted
	gamestarted = 1

@Event('player_disconnect')	
def player_disconnect(ev):
	userid = ev.get_int('userid')
	player_entity = Player(index_from_userid(userid))
	
	wcsplayers[ev['userid']].save()
	if userid in wcsplayers:
		wcsplayers[ev['userid']].lastconnect = time.time()
		wcsplayers[ev['userid']].name = wcsplayers[ev['userid']].remove_warnings(player_entity.name)
		wcsplayers[ev['userid']].save()

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
			race = wcsplayers[userid].currace
			if race != '':
				raceinfo = racedb.races[race]
				if raceinfo['roundstartcmd']:
					command = raceinfo['roundstartcmd']
					command = command.split(";")
					ConVar("wcs_userid").set_int(userid)
					for com in command:
						execute_server_command('es', com)
	round_count = ConVar('wcs_roundcounter').get_int()
	round_count += 1
	ConVar('wcs_roundcounter').set_int(round_count)
	
@Event('round_end')
def round_end(event):
	global gamestarted
	gamestarted = 0
	for player in PlayerIter():
		userid = player.userid
		if player_loaded[userid] == True:
			if player.team >= 2:
				race = wcsplayers[userid].currace
				raceinfo = racedb.getRace(race)
				if raceinfo['roundendcmd']:
					command = raceinfo['roundendcmd']
					command = command.split(";")
					for com in command:
						execute_server_command('es', com)
				
	xpsaver = config.coredata['xpsaver']
	if xpsaver:
		global saved
		if xpsaver <= saved:
			for user in wcsplayers:
				wcsplayers[user].save()
			saved = 0

		else:
			saved += 1
			
	if int(event['winner']) == 3:
		team = 'ct'
		other = ['t','alive']
	if int(event['winner']) == 2:
		team = 't'
		other = ['ct','alive']
	if str(event['winner']) not in "2;3":
		return
	for player in PlayerIter(team):
		if player.steamid == 'BOT':
			winxp = config.cfgdata['bot_roundwxp']
		else:
			winxp = config.cfgdata['player_roundwxp']
		Delay(1, wcsplayers[player.userid].give_xp, (winxp, 'for winning the round'))
	for player in PlayerIter(other):
		if player.steamid == 'BOT':
			surxp = config.cfgdata['bot_roundsxp']
		else:
			surxp = config.cfgdata['player_roundsxp']		
		Delay(1,  wcsplayers[player.userid].give_xp, (surxp, 'for surviving the round'))

@PreEvent('player_death')
def pre_death(event):
	userid = int(event['userid'])
	if player_isdead[userid] == 0:
		player_isdead[userid] = 1
		attacker = Player.from_userid(int(event['attacker']))
	elif player_isdead[userid] == 1:
		return EventAction.BLOCK

@Event('player_death')			
def player_death(event):
	#player_death variables
	victim = event.get_int('userid')
	attacker = event.get_int('attacker')
	if SOURCE_ENGINE_BRANCH == 'csgo':
		assister = event.get_int('assister')
	else:
		assister = 0
	headshot = event.get_int('headshot')
	weapon = event.get_string('weapon')
	queue_command_string('es wcsgroup set regeneration_active %s 0' % victim)
	#player_death execution
	victim_entity = Player(index_from_userid(victim))
	if attacker:
		attacker_entity = Player(index_from_userid(attacker))
	if attacker and victim:

		if not victim == attacker:
			if not victim_entity.team == attacker_entity.team:
				bonus = 0
				if wcsplayers[attacker_entity.userid].level <  wcsplayers[victim_entity.userid].level:
					diffience = wcsplayers[victim_entity.userid].level - wcsplayers[attacker_entity.userid].level
					#Bonus XP
					if attacker_entity.steamid == 'BOT':
						limit = config.cfgdata['bot_levellimit']
						if limit:
							if diffience > limit:
								diffience = limit
						bonus = config.cfgdata['bot_difxp']*diffience
					else:
						limit = config.cfgdata['player_levellimit']
						if limit:
							if diffience > limit:
								diffience = limit
						bonus = config.cfgdata['player_difxp']*diffience
				#Normal XP Gain
				if victim_entity.steamid == 'BOT':
					killxp = config.cfgdata['bot_killxp']
					headshotxp = config.cfgdata['bot_headshotxp']
					knifexp = config.cfgdata['bot_knifexp']
					hexp = config.cfgdata['bot_hexp']
					flashxp = config.cfgdata['bot_flashxp']
					smokexp = config.cfgdata['bot_smokexp']
					if SOURCE_ENGINE_BRANCH == 'csgo':
						molotovxp = config.cfgdata['bot_molotovxp']
				else:
					killxp = config.cfgdata['player_killxp']
					headshotxp = config.cfgdata['player_headshotxp']
					knifexp = config.cfgdata['player_knifexp']
					hexp = config.cfgdata['player_hexp']
					flashxp = config.cfgdata['player_flashxp']
					smokexp = config.cfgdata['player_smokexp']
					if SOURCE_ENGINE_BRANCH == 'csgo':
						molotovxp = config.cfgdata['player_molotovxp']
				if bonus:
					Delay(1, wcsplayers[attacker_entity.userid].give_xp, (killxp+bonus, 'for killing a higher-level enemy. (\x04%s level difference bonus xp!)' % diffience))
				else:
					Delay(1, wcsplayers[attacker_entity.userid].give_xp, (killxp, 'for making a kill'))

				if headshot == 1:
					Delay(1, wcsplayers[attacker_entity.userid].give_xp, (headshotxp, 'for making a headshot'))
					
				elif 'knife' in weapon:
					Delay(1, wcsplayers[attacker_entity.userid].give_xp, (knifexp, 'for making a knife kill'))
				elif weapon == 'hegrenade':
					Delay(1, wcsplayers[attacker_entity.userid].give_xp, (hexp, 'for making a explosive grenade kill'))
				elif weapon == 'smokegrenade':
					Delay(1, wcsplayers[attacker_entity.userid].give_xp, (smokexp, 'for making a smoke grenade kill'))
				elif weapon == 'flashbang':
					Delay(1, wcsplayers[attacker_entity.userid].give_xp, (flashbangxp, 'for making a flashbang grenade kill'))
				elif weapon == 'inferno':
					Delay(1, wcsplayers[attacker_entity.userid].give_xp, (molotovxp, 'for making a fire kill'))
			

			checkEvent(victim,	'player_death')
			checkEvent(attacker, 'player_kill')

		race = wcsplayers[attacker].currace
		if racedb.races[race]['deathcmd']:
			command = racedb.races[race]['deathcmd']
			command = command.split(";")
			for com in command:
				execute_server_command('es', com)
	if (victim and not attacker) or (victim == attacker):
		checkEvent(victim,	'player_death')
	if assister:
		assist_player = Player.from_userid(int(assister))
		if assist_player.steamid == 'BOT':
			assistxp = config.cfgdata['bot_assistxp']
		else:
			assistxp = config.cfgdata['player_assistxp']
		Delay(1, wcsplayers[assister].give_xp, (assistxp, 'for assisting in a kill'))
		checkEvent(assister,'player_assister')
		

@Event('player_hurt')
def _player_hurt(event):
	victim = event.get_int('userid')
	attacker = event.get_int('attacker')
	weapon = event.get_string('weapon')
	health = event.get_int('health')
	
	if victim:
		victim_entity = Player(index_from_userid(victim))
	if attacker:
		attacker_entity = Player(index_from_userid(attacker))
	if attacker and victim and not weapon.lower() in ('point_hurt') and not weapon.lower() in ('worldspawn'):
		if not victim == attacker:
			if not victim_entity.team == attacker_entity.team:
				checkEvent(victim, 'player_victim')
				if health > 0:
					checkEvent(attacker, 'player_attacker')
				
			checkEvent(victim, 'player_hurt')
			if health > 0:
				checkEvent(attacker, 'player_hurt')
				
@Event('bomb_planted')
def bomb_planted(event):
	userid = int(event['userid'])
	player = Player.from_userid(userid)
	if player.steamid == 'BOT':
		plantxp = config.cfgdata['bot_plantxp']
	else:
		plantxp = config.cfgdata['player_plantxp']
	Delay(1, wcsplayers[userid].give_xp, (plantxp, 'for planting the bomb!'))
		
@Event('bomb_defused')
def bomb_planted(event):
	userid = int(event['userid'])
	player = Player.from_userid(userid)
	if player.steamid == 'BOT':
		defusexp = config.cfgdata['bot_defusexp']
	else:
		defusexp = config.cfgdata['player_defusexp']
	Delay(1, wcsplayers[userid].give_xp, (defusexp, 'for defusing the bomb!'))

@Event('bomb_exploded')
def bomb_exploded(event):
	userid = int(event['userid'])
	player = Player.from_userid(userid)
	if player.steamid == 'BOT':
		explodexp = config.cfgdata['bot_explodexp']
	else:
		explodexp = config.cfgdata['player_explodexp']
	Delay(1, wcsplayers[userid].give_xp, (explodexp, 'for letting the bomb explode!'))

@Event('hostage_rescued')
def hostage_rescued(event):
	userid = int(event['userid'])
	player = Player.from_userid(userid)
	if player.steamid == 'BOT':
		rescuexp = config.cfgdata['bot_rescuexp']
	else:
		rescuexp = config.cfgdata['player_rescuexp']
	Delay(1, wcsplayers[userid].give_xp, (rescuexp, 'for rescuing a hostage!'))		

			
@Event('player_spawn')			
def _player_spawn(event):
	userid = event.get_int('userid')
	player_isdead[userid] = 0
	player = Player.from_userid(userid)
	player.color = Color(255,255,255,255)
	player.gravity = 1.0
	player.speed = 1.0
	queue_command_string('es wcsgroup set regeneration_active %s 0' % userid)
	if player_loaded[userid] == True:
		event_instance = wcs.events.wcs_player_spawn(userid=userid)
		event_instance.fire()
	else:
		return
		
@Event('wcs_player_spawn')
def _wcs_player_spawn(event):
	userid = event.get_int('userid')
	index = index_from_userid(userid)
	players = PlayerDictionary()
	if userid not in wcsplayers:
		wcsplayers[userid] = WarcraftPlayer(userid)
	race = wcsplayers[userid].currace
	allraces = racedb.getAll()
	if race not in allraces:
		race = ConVar('wcs_default_race').get_string()
		wcsplayers[userid].changerace(ConVar('wcs_default_race').get_string(), kill=False,who='silent',safe=True)
	players[index].clan_tag = race
	if userid and players[index].team >= 2:
		for i, v in {'gravity':1.0,'speed':1.0,'longjump':1.0}.items():
			wcsgroup.setUser(userid, i, v)

		players[index].gravity = 1.0
		players[index].color = Color(255,255,255,255)
		wcsgroup.setUser(userid,'ability',None)


		wcsgroup.addUser(userid)

		wcsplayers[userid].show_xp()

		checkEvent(userid, 'player_spawn')

		raceinfo = racedb.getRace(race)
		if int(raceinfo['restrictteam']) and not players[index].steamid == 'BOT':
			if players[index].team == int(raceinfo['restrictteam']) and players[index].team >= 2 and not players[index].steamid == 'BOT':
				players[index].team = 1
				changerace.HowChange(userid)

		elif 'teamlimit' in raceinfo and not players[index].steamid == 'BOT':
			q = int(raceinfo['teamlimit'])
			if q:
				v = wcsgroup.getUser({2:'T',3:'CT'}[players[index].team], 'restricted')
				if v == None:
					v = 0
				if v > q:
					players[index].team = 1
					changerace.HowChange(userid)

		elif curmap in raceinfo['restrictmap'].split('|'):
			if not players[index].steamid == 'BOT':
					players[index].team = 1
					changerace.HowChange(userid)

		if raceinfo['spawncmd'] != "":
			command = raceinfo['spawncmd']
			command = command.split(";")
			for com in command:
				execute_server_command('es', com)

@Event('player_say')			
def player_say(event):
	userid = event.get_int('userid')
	checkEvent(userid, 'player_say')
# =============================================================================
# >> LISTENERS
# =============================================================================	
class OnPlayerSaved(ListenerManagerDecorator):
	manager = ListenerManager()
	
class OnPlayerLoaded(ListenerManagerDecorator):
	manager = ListenerManager()
	
class OnPlayerDeleted(ListenerManagerDecorator):
	manager = ListenerManager()
	
class OnRaceDeleted(ListenerManagerDecorator):
	manager = ListenerManager()
	
@OnPlayerLoaded
def on_loaded(wcsplayer):
	player_loaded[wcsplayer.userid] = True
	player = Player.from_userid(int(wcsplayer.userid))
	if player.dead == 0:
		event_instance = wcs.events.wcs_player_spawn(userid=wcsplayer.userid)
		event_instance.fire()
	
@OnClientActive
def on_client_active(index):
	wcsplayers[Player(index).userid] = WarcraftPlayer(Player(index).userid)
	race = wcsplayers[Player(index).userid].currace
	Player(index).clan_tag = race
	
@OnPlayerDeleted
def on_player_deleted(index):
	userid = userid_from_index(index)
	if userid not in wcsplayers:
		wcsplayers[userid] = WarcraftPlayer(userid)
		
@ServerCommand('changelevel')
def _changelevel_hook(command):
	for user in wcsplayers:
		wcsplayers[user].save()
	return CommandReturn.CONTINUE
		

@OnLevelShutdown
def level_shutdown_listener():
	for player in PlayerIter():
		userid = player.userid
		savexp.doCommand(userid)
	
	for user in wcsplayers:
		wcsplayers[user].save()

@OnLevelInit
def level_init_listener(mapname):
	allow_alpha = ConVar('sv_disable_immunity_alpha')
	allow_alpha.set_int(1)
	autokick = ConVar('mp_autokick')
	autokick.set_int(0)
	queue_command_string('sp reload wcs')
	global curmap
	if ".bsp" in mapname:
		mapname = mapname.strip('.bsp')
	curmap = mapname
	if config.coredata['saving'] == 1:
		repeat_delay = float(config.coredata['save_time'])*60.0
		repeat = Repeat(do_save)
		repeat.start(repeat_delay)
		
@OnTick
def on_tick():
	if config.coredata['keyinfo'] == 1:
		for player in PlayerIter('all'):
			if not player.is_bot():
				user_queue = PagedMenu.get_user_queue(player.index)
				if user_queue.active_menu is None:
					userid = player.userid
					race = wcsplayers[userid].currace
					if race in wcsplayers[userid].all_races:
						totallevel = wcsplayers[userid].totallevel
						if 'level' in wcsplayers[userid].all_races[race]:
							level = wcsplayers[userid].all_races[race]['level'] 
							xp = wcsplayers[userid].all_races[race]['xp'] 
							if config.cfgdata['experience_system'] == 0:
								needed = config.cfgdata['interval']*level if level else config.cfgdata['interval']
							elif config.cfgdata['experience_system'] == 1:
								level_string = config.cfgdata['custom_system'].split(',')
								if level < len(level_string):
									needed = int(level_string[level])
								else:
									needed = int(level_string[len(level_string)-1])
							steamid = player.uniqueid
							rank,total = wcsplayers[player.userid].get_rank()
							text = str(race)+'\n--------------------\nTotallevel: '+str(totallevel)+'\nLevel: '+str(level)+'\nXp: '+str(xp)+'/'+str(needed)+'\n--------------------\nWCS rank: '+str(rank)+'/'+str(total)
							if SOURCE_ENGINE_BRANCH == "css":
								KeyHintText(text).send(player.index)
							else:
								HudMsg(text, 0.025, 0.4,hold_time=0.2).send(player.index)
				
				
# =============================================================================
# >> Functions
# =============================================================================

def _load_ranks():
	with session_scope() as session:
		query = session.query(Players, Races).filter(Players.UserID == Races.UserID).filter(Players.currace == Races.name).all()
		if query != None:
			for (user, race) in query:
				wcs_rank[user.steamid] = {}
				wcs_rank[user.steamid]['name'] = user.name
				wcs_rank[user.steamid]['totallevel'] = user.totallevel
				wcs_rank[user.steamid]['currace'] = user.currace
				wcs_rank[user.steamid]['level'] = race.level
				
	
def centertell(userid,message):
	index = index_from_userid(userid)
	if SOURCE_ENGINE_BRANCH == "css":
		queue_command_string("es_centertell %s %s" %(userid,message))
	else:
		HudMsg(message, -1, 0.35,hold_time=5.0).send(index)

def checkEvent(userid, event, other_userid=0, health=0, armor=0, weapon='', dmg_health=0, dmg_armor=0, hitgroup=0,assister=0,headshot=0):
	if userid is not None:
		player_entity = Player(index_from_userid(userid))
		if int(player_entity.team) > 1:
			race = wcsplayers[userid].currace
			race1 = racedb.races[race]
			if event in raceevents[race]:
				skills = wcsplayers[userid].all_races[race]['skills'].split('|')
				for index in raceevents[race][event]:
					try:
						level = int(skills[int(index)])
					except IndexError:
						level = None
					if level:
						wcs_dice = ConVar('wcs_dice')
						wcs_dice.set_int(random.randint(0, 100))
						for x in range(1, 9):
							wcs_dice = ConVar('wcs_dice'+str(x))
							wcs_dice.set_int(random.randint(0,100))
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
			race = wcsplayers[userid].currace
			race1 = racedb.races[race]
			if event in raceevents[race]:
				skills = wcsplayers[userid].all_races[race]['skills'].split('|')
				index = raceevents[race][event][0]

				try:
					level = int(skills[int(index)])
				except IndexError:
					level = None
				if level:
					if gamestarted:
						wcs_dice = ConVar('wcs_dice')
						wcs_dice.set_int(random.randint(0, 100))
						for x in range(1, 9):
							wcs_dice = ConVar('wcs_dice'+str(x))
							wcs_dice.set_int(random.randint(0,100))
						skill = 'skill'+str(int(index)+1)
						cooldown = wcsgroup.getUser(userid, event+'_cooldown')
						if cooldown is None:
							cooldown = 0
						cooldown = int(cooldown)
						wcsgroup.setUser(userid, event+'_pre_cooldown', cooldown)
						timed = int(float(time.time()))
						downtime = str(race1[skill]['cooldown']).split('|')
						nol = race1['numberoflevels']
						if '|' in nol:
							nol = nol.split('|')
							nol = [int(x) for x in nol]
						else:
							nos = int(race1['numberofskills'])
							nol_tmp = int(race1['numberoflevels'])
							nol = []
							x = 0
							while x < nos:
								nol.append(nol_tmp)
								x += 1
						
						if len(downtime) == int(nol[int(index)]):
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

def do_save():
	for x in wcsplayers:
		wcsplayers[x].save()
		
def exists(userid):
	try:
		index_from_userid(userid)
	except ValueError:
		return False
	return True

def find_items(name):
	item_list = []
	items_all = wcs.wcs.ini.getItems
	items_all.walk(gather_subsection)
	for item in item_names:
		item_sec = itemdb.getSectionFromItem(item)
		iteminfo = itemdb.getItem(item)
		if name.lower() in iteminfo['name'].lower():
			item_list.append(item)
	if len(item_list):
		return item_list
	else:
		return -1

def format_message(message):
	for color in color_codes:
		if color in message:
			message = message.replace(color, '')
	return message
	
def gather_subsection(section, key):
	if section.depth > 1:
		if section.name not in item_names:
			item_names.append(section.name)
			
def get_cooldown(userid):
	race = wcsplayers[userid].currace
	race1 = racedb.races[race]
	if 'player_ultimate' in raceevents[race]:
		skills = wcsplayers[userid].all_races[race]['skills'].split('|')
		index = raceevents[race]['player_ultimate'][0]
		skill = 'skill'+str(int(index)+1)
		try:
			level = int(skills[int(index)])
		except IndexError:
			level = None
		if level:
			downtime = str(race1[skill]['cooldown']).split('|')
			nol = race1['numberoflevels']
			if '|' in nol:
				nol = nol.split('|')
				nol = [int(x) for x in nol]
			else:
				nos = int(race1['numberofskills'])
				nol_tmp = int(race1['numberoflevels'])
				nol = []
				x = 0
				while x < nos:
					nol.append(nol_tmp)
					x += 1
			if len(downtime) == nol[int(index)]:
				downtime = int(downtime[level-1])
				if not downtime:
					downtime = str(race1[skill]['cooldown']).split('|')
					downtime = int(downtime[0])
				return downtime
			else:
				return int(downtime[len(downtime)-1])	
		
def get_random_race(userid):
	race_list = []
	races = racedb.getAll()
	allraces = races.keys()
	for number, race in enumerate(allraces):
		v = changerace.canUse(userid,race)
		if not v:
			race_list.append(race)
	if len(race_list):
		chosen = str(choice(race_list))
		return chosen
	else:
		return -1

def is_number(s):
	try:
		float(s)
		return True
	except ValueError:
		return False	
		
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
				if races[race]['preloadcmd'] != "":
					command = races[race]['preloadcmd']
					command = command.split(";")
					for com in command:
						execute_server_command('es', com)
def remove_effects():
	for player in PlayerIter():
		userid = player.userid
		queue_command_string('wcs_color %s 255 255 255 255' % userid)
		queue_command_string('wcs_setgravity %s 1.0' % userid)
		queue_command_string('es playerset speed %s 1.0' % userid)
		queue_command_string('es wcsgroup set regeneration_active %s 0' % userid)
	
def set_team(userid):
	if exists(userid):
		player = Player.from_userid(userid)
		if player.team == 0:
			Player.from_userid(userid).team = 1
	
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

@ServerCommand("wcs_giveprivate")
def _give_private_race(command):
	userid = int(command[1])
	race_name = str(command[2])
	steamid = Player.from_userid(userid).uniqueid
	race_dict = ConfigObj(ini.races,encoding="utf-8")
	allowonly = race_dict[race_name]['allowonly']
	if steamid not in allowonly:
		if allowonly != "":
			new_only = str(allowonly)+"|"+str(steamid)
		else:
			new_only = str(steamid)
		race_dict[race_name]['allowonly'] = new_only
		race_dict.write()
		ini.races = os.path.join(PLUGIN_PATH, 'wcs/races', 'races.ini')
		racedb.races = ini.getRaces
