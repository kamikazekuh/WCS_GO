from commands.server import ServerCommand
from players.entity import Player
from cvars import ConVar
from colors import Color
from engines.server import execute_server_command
from listeners.tick import Repeat, Delay
from messages import SayText2
from events import Event
from entities.entity import Entity
from mathlib import Vector
from messages import Fade, FadeFlags
from core import SOURCE_ENGINE_BRANCH

@ServerCommand('wcs')
def register(command):
	if len(command) >= 4:
		todo = str(command[1]).lower()
		userid = str(command[2])
		if todo == 'damage':
			v,q,w = int(command[3]) if int(command[3]) else None, int(command[5]) if len(command) >= 6 else False, str(command[6]) if len(command) == 7 else None
			damage(userid, str(command[4]), v, q, w)

		elif todo == 'spawn':
			if len(command) in (3,4):
				spawn(userid, int(command[3]) if len(command) == 4 else False)
				
		elif todo == 'strip':
			if len(command) == 3:
				strip(userid)

		elif todo == 'drop':
			if len(command) == 4:
				drop(userid, command[3])

		elif todo == 'push':
			if len(command) >= 4:
				push(userid, command[3], command[4] if len(command) >= 5 else 0, command[5] if len(command) == 6 else 0)

		elif todo == 'pushto':
			if len(command) == 5:
				pushto(userid, command[3], command[4])

		elif todo == 'gravity':
			if len(command) == 4:
				gravity(userid, command[3])

		elif todo == 'removeweapon':
			if len(command) == 4:
				removeWeapon(userid, command[3])

		elif todo == 'getviewplayer':
			if len(command) == 4:
				v = getViewPlayer(userid)
				ConVar(str(command[3])).set_string(str(v) if v is not None else "0")

		elif todo == 'getviewentity':
			if len(command) == 4:
				v = getViewEntity(userid)
				ConVar(str(command[3])).set_string(str(v)if v is not None else "0")

		elif todo == 'keyhint':
			keyHint(userid, ' '.join(map(str, args[3:])))

		elif todo == 'give':
			if len(command) == 4:
				give(userid, command[3])

		elif todo == 'fire':
			if len(command) >= 3:
				fire(userid, float(command[3]) if len(command) == 4 else 0.0)

		elif todo == 'extinguish':
			if len(command) == 3:
				extinguish(userid)

		elif todo == 'drug':
			if len(command) >= 3:
				drug(userid, float(command[3]) if len(command) >= 4 else 0)

		elif todo == 'drunk':
			if len(command) >= 3:
				drunk(userid, float(command[3]) if len(command) >= 4 else 0, int(command[4]) if len(command) == 5 else 155)

		elif todo == 'poison':
			if len(command) == 6:
				dealPoison(userid, int(float(command[3])), int(command[4]), float(command[5]))

		elif todo == 'changeteam':
			if len(command) == 4:
				changeTeam(userid, str(command[3]))

		

def spawn(userid, force=False):
	Player.from_userid(int(userid)).spawn(force)
	
def fade(userid, r,g,b,a,time):
	color = Color(r,g,b,a)
	Fade(int(time), int(time),color,FadeFlags.PURGE).send(Player.from_userid(userid).index)	

def strip(userid):
	player = Player.from_userid(int(userid))
	entity = Entity.create('player_weaponstrip')
	entity.call_input("Strip", activator=player)
	entity.remove()

def drop(userid, weapon):
	player = Player.from_userid(int(userid))
	if str(weapon) == "1":
		wpn = player.get_weapon(is_filters='primary')
		if wpn:
			player.drop_weapon(wpn)
	elif str(weapon) == "2":
		wpn = player.get_weapon(is_filters='secondary')
		if wpn:
			player.drop_weapon(wpn)
	else:
		if player.get_weapon(is_filters='secondary'):
			if player.get_weapon(is_filters='secondary').classname == weapon:
				player.drop_weapon(player.get_weapon(is_filters='secondary'))
		if player.get_weapon(is_filters='primary'):
			if player.get_weapon(is_filters='primary').classname == weapon:
				player.drop_weapon(player.get_weapon(is_filters='primary'))

def push(userid, xm, ym=0, zm=0):
	userid = int(userid)
	vec = Vector(float(xm),float(ym),float(zm))
	player = Player.from_userid(int(userid))
	player.set_property_vector("m_vecBaseVelocity", vec)


def pushto(userid, coord, force):
	coords = coord.split(",")
	vec = Vector(coords[0],coords[1],coords[2])
	player = Player(index_from_userid(userid))
	player.teleport(None, None, vec - player.origin)

def damage(victim, dmg, attacker=None, armor=False, weapon=None):
	vic_player = Player.from_userid(int(victim))
	if attacker:
		atk_player = Player.from_userid(int(attacker))
		if atk_player.get_weapon(is_filters='secondary'):
			if weapon == atk_player.get_weapon(is_filters='secondary').classname:
				wpn_index = player.get_weapon(is_filters='secondary').index
			else:
				wpn_index = 0
		if atk_player.get_weapon(is_filters='primary'):
			if weapon == atk_player.get_weapon(is_filters='primary').classname:
				wpn_index = atk_player.get_weapon(is_filters='primary').index
		
	vic_player.take_damage(int(dmg),attacker_index=atk_player.index, weapon_index=None,skip_hooks=True)

def gravity(userid, value):
	Player.from_userid(int(userid)).gravity = float(value)


def removeWeapon(userid, weapon):
	userid = int(userid)
	slot_weapon = weapon
	player = Player.from_userid(int(userid))
	if slot_weapon in "1;2;3;4;5":
		if slot_weapon == "1":
			weapon = player.get_weapon(is_filters='primary')
			if weapon != None:
				player.drop_weapon(weapon)
				weapon.remove()
		if slot_weapon == "2":
			weapon = player.get_weapon(is_filters='secondary')
			if weapon != None:
				player.drop_weapon(weapon)
				weapon.remove()
	else:
		for weapon in player.weapons():
			if weapon.classname == slot_weapon:
				player.drop_weapon(weapon)
				weapon.remove()

def getViewEntity(userid):	
	return Player.from_userid(int(userid)).get_view_entity().index


def getViewPlayer(userid):
	return Player.from_userid(int(userid)).get_view_player().userid


def keyHint(userid, text):
	if not len(text):
		return

	if str(userid).startswith('#'):
		userid = getUseridList(userid)

	elif not hasattr(userid, '__iter__'):
		userid = (userid, )

	es.usermsg('create', 'keyhint', 'KeyHintText')
	es.usermsg('write', 'byte', 'keyhint', 1)
	es.usermsg('write', 'string', 'keyhint', text)

	for user in userid:
		if es.exists('userid', user):
			es.usermsg('send', 'keyhint', user)

	es.usermsg('delete', 'keyhint')

def give(userid, entity):
	execute_server_command('es_give', '%s %s' % (userid, entity))

def fire(userid, time=0):
	if time == 0:
		time = 999
	Player.from_userid(int(userid)).ignite_lifetime(float(time))

def extinguish(userid):
	Player.from_userid(int(userid)).ignite_lifetime(0.0)

def drug(userid, time=0):
	userid = int(userid)
	delay = float(time)
	Player.from_userid(userid).client_command('r_screenoverlay effects/tp_eyefx/tp_eyefx')
	Delay(delay, remove_drug, (userid,))
	
def remove_drug(userid):
	Player.from_userid(userid).client_command('r_screenoverlay 0')


def drunk(userid, time=0, value=155):
	player = Player.from_userid(int(userid))
	player.set_property_uchar('m_iDefaultFOV', value)
	player.set_property_uchar('m_iFOV', value)
	if time:
		Delay(time, remove_drunk, (player,))

def remove_drunk(player):
	player.set_property_uchar('m_iDefaultFOV', 90)
	player.set_property_uchar('m_iFOV', 90)


	
@Event('player_spawn')
def player_spawn(ev):
	player = Player.from_userid(ev['userid'])
	player.set_property_uchar('m_iDefaultFOV', 90)
	player.set_property_uchar('m_iFOV', 90)
	player.gravity = 1.0
	player.client_command('r_screenoverlay 0')


def dealPoison(userid, attacker, dmg, time):
	poison_repeat = Repeat(_poison_repeat,(userid,attacker,dmg))
	poison_repeat.start(time)
	
def _poison_repeat(userid,attacker,dmg):
	damage(userid,attacker,dmg)
	if SOURCE_ENGINE_BRANCH == 'css':
		SayText2("\x04[WCS] \x03Poison did \x04%s \x03damage to you!" % (dmg)).send(Player.from_userid(int(userid)).index)
	else:
		SayText2("\x04[WCS] \x03Poison did \x04%s \x03damage to you!" % (dmg)).send(Player.from_userid(int(userid)).index)

def changeTeam(userid, team):
	Player.from_userid(userid).set_team(int(team))