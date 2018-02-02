import os
from path import Path
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
from cvars import ConVar

import sys
from sqlalchemy import Column, ForeignKey, Integer, String, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.expression import insert
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, desc
Base = declarative_base()

import time

lb_db_method = ConVar('wcs_levelbank_connectstring').get_string()

engine = create_engine(lb_db_method)

maxlevel = ConVar('race_maximum_level')


class BankPlayers(Base):
	__tablename__ = 'BankPlayers'
	UserID = Column(Integer,nullable=False,primary_key=True)
	steamid = Column(String(30),nullable=False)
	levels = Column(Integer,default=0)
	Index('playersIndex', steamid)
	
if not engine.dialect.has_table(engine, 'BankPlayers'):
	Base.metadata.create_all(engine)

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
class SQLManager(object):
	def __init__(self):

		self.engine = engine
		self.DBSession = sessionmaker()
		self.DBSession.configure(bind=self.engine)
		self.session = self.DBSession()

	def __len__(self):
		return self.session.query(BankPlayers).count()

	def __contains__(self, user):
		if not isinstance(user, str): #Tha Pwned
			player = self.session.query(BankPlayers).filter(BankPlayers.UserID==user).all()
			if player.steamid:
				return 1
			else:
				return 0
		else:
			player = self.session.query(BankPlayers).filter(BankPlayers.steamid==user).all()
			if player.steamid:
				return 1
			else:
				return 0
		return bool(self.cursor.fetchone())


	def save(self):
		self.session.commit()
		
	def close(self):
		self.session.commit()
		self.session.close()

	def getUserIdFromSteamId(self, steamid):
		try:
			player = self.session.query(BankPlayers).filter(BankPlayers.steamid==steamid).one()
		except:
			return None
		
		if player.UserID == None:
			return None

		return player.UserID

	def getInfoPlayer(self,what,UserID):
		all = self.session.query(BankPlayers).filter(BankPlayers.UserID==UserID).one()
		if all != None:
			return (all.levels)
		else:
			return None

	def setInfoPlayer(self,options,UserID):
		user = self.session.query(BankPlayers).filter(BankPlayers.UserID==UserID).one()
		user.levels = options
		self.session.commit()
		
	def addPlayer(self, steamid):
		new_player = BankPlayers(steamid=steamid)
		self.session.add(new_player)
		self.session.commit()
		return self.session.query(BankPlayers).filter(BankPlayers.steamid==steamid).one().UserID

	def removeWarnings(self, value):
		return str(value).replace("'", "").replace('"', '')
		
database = SQLManager()


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
		v = database.getInfoPlayer(what,self.UserID)
		if v is None:
			return 0
		return v

	def _setInfo(self, options):
		database.setInfoPlayer(options,self.UserID)

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
		mxlvl = maxlevel.get_int()
		wcs_player = wcs.wcs.getPlayer(userid_from_index(index))
		if player.levels >= amount:
			if int(wcs_player.race.level+amount) > int(mxlvl):
				amount = int(mxlvl) - int(wcs_player.race.level)
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
		

def unload():
	tmp.clear()

	database.save()
	database.close()

@OnLevelInit
def level_init_listener(mapname):
	database.save()


@Event('player_disconnect')
def player_disconnect(event):
	global tmp
	userid = event.get_int('userid')
	if userid in tmp:
		tmp[userid].save()
		del tmp[userid]