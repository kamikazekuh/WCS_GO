from players.entity import Player
from filters.players import PlayerIter
from commands.server import ServerCommand
from cvars import ConVar
from events import Event
from messages import HintText
from players.helpers import index_from_userid
from listeners.tick import Repeat, RepeatStatus

mana_players = {}


class ManaPlayer(object):
	def __init__(self,userid,max_mana):
		self.userid = userid
		self.index = index_from_userid(self.userid)
		self.max_mana = max_mana
		self.current_mana = max_mana
		self.regeneration = -1
		self.regeneration_speed = -1
		self.show_mana = True
		
	def give_mana(self,amount):
		if self.current_mana + amount > self.max_mana:
			self.current_mana = self.max_mana
		else:
			self.current_mana += amount
	
	def give_max_mana(self,amount):
		self.max_mana += amount
		if self.current_mana == -1:
			self.current_mana = amount
		
	def take_mana(self,amount):
		if self.max_mana != -1:
			if self.current_mana - amount < 0:
				self.current_mana = 0
			else:
				self.current_mana -= amount
			
	def take_max_mana(self,amount):
		if self.max_mana != -1:
			if self.max_mana - amount < 0:
				self.max_mana = 0
			else:
				self.max_mana -= amount
			if self.current_mana > amount:
				self.current_mana = amount
			
	def set_mana(self,amount):
		if amount > self.max_mana:
			self.current_mana = self.max_mana
		else:
			self.current_mana = amount
			
	def set_regeneration(self,amount,speed):
		if self.regeneration_repeat.status != RepeatStatus.STOPPED:
			self.regeneration_repeat.stop()
		if amount != -1:
			self.regeneration_speed = speed
			self.regeneration = amount
			if self not in self.regeneration_repeat.args:
				self.regeneration_repeat.args += (self,)
			self.regeneration_repeat.start(speed)
		
			
	def set_max_mana(self,amount):
		self.max_mana = amount
		if self.current_mana > amount:
			self.current_mana = amount
		if self.current_mana == -1:
			self.current_mana = amount
			
	def show_info(self):
		if self.max_mana != -1:
			HintText("Mana: %s/%s" % (self.current_mana,self.max_mana)).send(self.index)
	
	@Repeat
	def regeneration_repeat(self):
		if self.current_mana < self.max_mana:
			if self.current_mana + self.regeneration > self.max_mana:
				self.current_mana = self.max_mana
			else:
				self.current_mana += self.regeneration
		
		
for player in PlayerIter():
	mana_players[player.userid] = ManaPlayer(player.userid,-1)
	
@Event('player_death')
def _player_death(ev):
	userid = int(ev['userid'])
	if mana_players[userid].regeneration_repeat.status != RepeatStatus.STOPPED:
		mana_players[userid].regeneration_repeat.stop()
	mana_players[userid].set_max_mana(-1)
	
@Event('player_activate')
def player_connect(ev):
	userid = int(ev['userid'])
	if userid not in mana_players:
		mana_players[userid] = ManaPlayer(userid,-1)
		
@Event('player_disconnect')
def player_disconnect(ev):
	userid = int(ev['userid'])
	if userid in mana_players:
		mana_players.pop(userid)
	
	
@ServerCommand('wcs_set_max_mana')
def _set_max_mana(command):
	userid = int(command[1])
	amount = int(command[2])
	mana_players[userid].set_max_mana(amount)
	
@ServerCommand('wcs_set_mana')
def _set_mana(command):
	userid = int(command[1])
	amount = int(command[2])
	mana_players[userid].set_mana(amount)
	
@ServerCommand('wcs_get_max_mana')
def _get_max_mana(command):
	userid = int(command[1])
	var = str(command[2])
	ConVar(var).set_int(mana_players[userid].max_mana)

@ServerCommand('wcs_give_max_mana')
def _add_max_mana(command):
	userid = int(command[1])
	amount = int(command[2])
	mana_players[userid].give_max_mana(amount)


@ServerCommand('wcs_take_max_mana')
def _take_max_mana(command):
	userid = int(command[1])
	amount = int(command[2])
	mana_players[userid].take_max_mana(amount)
	
@ServerCommand('wcs_get_mana')
def _get_mana(command):
	userid = int(command[1])
	var = str(command[2])
	ConVar(var).set_int(mana_players[userid].current_mana)

@ServerCommand('wcs_give_mana')
def _add_mana(command):
	userid = int(command[1])
	amount = int(command[2])
	mana_players[userid].give_mana(amount)

@ServerCommand('wcs_take_mana')
def _take_mana(command):
	userid = int(command[1])
	amount = int(command[2])
	mana_players[userid].take_mana(amount)
	
@ServerCommand('wcs_set_mana_regeneration')
def _set_regeneration(command):
	userid = int(command[1])
	amount = int(command[2])
	speed = float(command[3])
	mana_players[userid].set_regeneration(amount,speed)
	
@Repeat
def info_repeat():
	for player in mana_players.values():
		if exists(player.userid):
			if Player.from_userid(player.userid).dead != 1:
				player.show_info()
		
info_repeat.start(0.1)

def exists(userid):
	try:
		index_from_userid(userid)
	except ValueError:
		return False
	return True
