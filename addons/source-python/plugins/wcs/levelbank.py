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
from queue import Empty, Queue
import wcs
from listeners.tick import Delay, Repeat
from contextlib import contextmanager
from cvars import ConVar
from threading import Thread
from listeners import ListenerManager
from listeners import ListenerManagerDecorator

import sys
from sqlalchemy import Column, ForeignKey, Integer, String, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.expression import insert
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, desc
Base = declarative_base()

class OnBankPlayerLoaded(ListenerManagerDecorator):
	manager = ListenerManager()
	
class OnBankPlayerSaved(ListenerManagerDecorator):
	manager = ListenerManager()

import time

lb_db_method = ConVar('wcs_levelbank_connectstring').get_string()

engine = create_engine(lb_db_method)

	
Session = sessionmaker(bind=engine)

maxlevel = ConVar('race_maximum_level')
output = Queue()
bank_player_loaded = {}
bankplayer = {}

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

class BankPlayers(Base):
	__tablename__ = 'BankPlayers'
	user_id = Column(Integer,nullable=False,primary_key=True)
	steamid = Column(String(30),nullable=False)
	levels = Column(Integer,default=0)
	Index('BankPlayersIndex', steamid)
	
if not engine.dialect.has_table(engine, 'BankPlayers'):
	Base.metadata.create_all(engine)


@Event('player_activate')
def _player_activate(event):
	userid = event.get_int('userid')
	bankplayer[userid] = WarcraftBankPlayer(userid)
	
@OnBankPlayerLoaded
def bank_loaded(bankplayer):
	bank_player_loaded[bankplayer.userid] = True
	
class WarcraftBankPlayer(object):
	def __init__(self,userid):
		self.userid = int(userid)
		self.steamid = Player.from_userid(self.userid).uniqueid
		bank_player_loaded[self.userid] = False
		self.levels = 0
		Thread(target=self._load_from_database).start()
		
	def _load_from_database(self):
		with session_scope() as session:
			player = session.query(BankPlayers).filter(BankPlayers.steamid==self.steamid).one_or_none()
			if player is None:
				player = BankPlayers(steamid=self.steamid)
				session.add(player)
				session.commit()
			self.user_id = player.user_id
			self.levels = player.levels
		output.put(self._on_finish)
		
	def _on_finish(self):
		if exists(self.userid):
			OnBankPlayerLoaded.manager.notify(self)
			
	def save(self):
		if exists(self.userid):		
			Thread(target=self._save_player_to_database).start()

	def _save_player_to_database(self):
		with session_scope() as session:
			player = session.query(BankPlayers).filter(BankPlayers.user_id==self.user_id).one_or_none()
			player.steamid = self.steamid
			player.levels = self.levels
			session.commit()
		output.put(self._on_player_saved)
	
	def _on_player_saved(self):
		if exists(self.userid):
			OnBankPlayerSaved.manager.notify(self)
			
	def remove_warnings(self, value):
		return str(value).replace("'", "").replace('"', '')
		
@Repeat
def repeat():
	try:
		callback = output.get_nowait()
	except Empty:
		pass
	else:
		callback()
repeat.start(0.1)
		
for player in PlayerIter('all'):
	bankplayer[player.userid] = WarcraftBankPlayer(player.userid)
		
def exists(userid):
	try:
		index_from_userid(userid)
	except ValueError:
		return False
	return True		
						
def wcsadmin_bank_menu_build(menu, index):
	menu.clear()
	for player in PlayerIter():
		if player.steamid != 'BOT':
			option = PagedOption('%s' % player.name, player)
			menu.append(option)
			
def wcs_amount_select(menu, index, choice):
	if choice.value == 'spendlevels':
		userid = userid_from_index(index)
		amount = int(choice.text)
		mxlvl = maxlevel.get_int()
		if bankplayer[userid].levels >= amount:
			if int(wcs.wcs.wcsplayers[userid].all_races[wcs.wcs.wcsplayers[userid].currace]['level']+amount) > int(mxlvl):
				amount = int(mxlvl) - int(wcs.wcs.wcsplayers[userid].all_races[wcs.wcs.wcsplayers[userid].currace]['level'])
			wcs.wcs.wcsplayers[userid].give_level(amount)
			bankplayer[userid].levels -= amount
			wcs.wcs.tell(userid_from_index(index), '\x04[WCS] \x05You got \x04%s Levels \x05left in your \x04Bank!' % bankplayer[userid].levels)
			bankplayer[userid].save()
		else:
			wcs.wcs.tell(userid_from_index(index), "\x04[WCS] \x05You don't have enough \x04levels \x05in your \x04bank!")
			menu.send(index)
	else:		
		userid = choice.value.userid
		amount = int(choice.text)
		player = Player(index)
		bankplayer[userid].levels += amount
		wcs.wcs.tell(userid, '\x04[WCS] \x05You got \x04%s Bank-Levels \x05from admin \x04%s!' % (amount, player.name))
		bankplayer[userid].save()
			
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
	userid = userid_from_index(index)
	if bank_player_loaded[userid] == True:
		print('test')
		if int(bankplayer[userid].levels) > 0:
			print('test2')
			amount_menu.clear()
			amount_menu.append(Text('You have %s Levels in your bank' % bankplayer[userid].levels))
			amount_menu.append(PagedOption('1', 'spendlevels'))
			amount_menu.append(PagedOption('5', 'spendlevels'))
			amount_menu.append(PagedOption('10', 'spendlevels'))
			amount_menu.append(PagedOption('25', 'spendlevels'))
			amount_menu.append(PagedOption('100', 'spendlevels'))
			amount_menu.append(PagedOption('250', 'spendlevels'))
			amount_menu.append(PagedOption('1000', 'spendlevels'))
			amount_menu.append(PagedOption('2500', 'spendlevels'))
			amount_menu.send(index)
		else:
			print('test3')
			wcs.wcs.tell(userid, '\x04[WCS] \x05You do not have \x04any \x05levels in your \x04Levelbank')
	else:
		print('false')
			
def doCommand(userid):
	index = index_from_userid(userid)
	wcsadmin_bank_menu.send(index)	
	
wcsadmin_bank_menu = PagedMenu(title='WCSBank Menu', build_callback=wcsadmin_bank_menu_build, select_callback=wcsadmin_bank_menu_select)
	
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
	for userid in bankplayer:
		bankplayer[userid].save()

@OnLevelInit
def level_init_listener(mapname):
	for userid in bankplayer:
		bankplayer[userid].save()


@Event('player_disconnect')
def player_disconnect(event):
	userid = event.get_int('userid')
	bankplayer[userid].save()