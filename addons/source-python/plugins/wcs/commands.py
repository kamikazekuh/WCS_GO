from commands.server import ServerCommand
from players.helpers import index_from_userid, playerinfo_from_userid, index_from_playerinfo, userid_from_index, edict_from_userid,inthandle_from_userid
from players.entity import Player
from messages import SayText2, HudMsg, TextMsg
from cvars import ConVar
from colors import Color
from engines.server import queue_command_string, execute_server_command
import string
from events import Event
from entities.entity import Entity
from entities.constants import DamageTypes
from filters.players import PlayerIter
from listeners.tick import Delay, Repeat
import random
from filters.recipients import RecipientFilter
from engines.precache import Model
from effects.base import TempEntity
from mathlib import Vector
from messages import Fade, FadeFlags
from entities import TakeDamageInfo
from entities.hooks import EntityCondition
from entities.hooks import EntityPreHook
from memory import make_object
import wcs
from wcs import wcsgroup
from weapons.entity import Weapon
import time
from random import choice
from core import SOURCE_ENGINE_BRANCH

beam_blood = Model('decals/bloodstain_003.vmt')
beam_glow = Model('sprites/light_glow02.vmt')
beam_chain = Model('sprites/cbbl_smoke.vmt')
ring_spawn_thunder = Model('sprites/cbbl_smoke.vmt')
ring_spawn_vampire = Model('decals/bloodstain_003.vmt')
ring_raging_burn = Model('sprites/xfireball3.vmt')
inner_fire_follow = Model('sprites/laserbeam.vmt')

anti_falldamage = {}
repeat_dict = {}
regen_dict = {}
for player in PlayerIter('all'):
	regen_dict[player.userid] = 0
	repeat_dict[player.userid] = 0
	
@ServerCommand('wcs_getindex')
def get_index(command):
	userid = int(command[1])
	var = str(command[2])
	ConVar(var).set_string(str(Player.from_userid(userid).index))
	
@ServerCommand('wcs_fade')
def fade(command):
	userid = int(command[1])
	r = int(command[2])
	g = int(command[3])
	b = int(command[4])
	a = int(command[5])
	time = float(command[6])
	color = Color(r,g,b,a)
	Fade(int(time), int(time),color,FadeFlags.PURGE).send(Player.from_userid(userid).index)
	

	
@ServerCommand('wcs_randplayer')
def randplayer(command):
	var = str(command[1])
	ident = str(command[2])
	if "#" in ident:
		ident = ident.replace("#","")
	if ";" in ident:
		ident = ident.split(";")
	elif "," in ident:
		ident = ident.split(",")
	playlist = []
	for play in PlayerIter(ident):
		playlist.append(play)
	ConVar(var).set_string(str(choice(playlist).userid))
	

@ServerCommand('wcs_getviewentity')
def getViewEntity(command):
	if len(command) == 3:
		ConVar(str(command[2])).set_string(str(Player.from_userid(int(command[1])).get_view_entity().index))

@ServerCommand('wcs_getviewplayer')
def getViewPlayer(command):
	if len(command) == 3:
		ConVar(str(command[2])).set_string(str(Player.from_userid(int(command[1])).get_view_player().userid))
	
@ServerCommand('wcs_setgravity')
def gravity(command):
	if len(command) == 3:
		Player.from_userid(int(command[1])).gravity = float(command[2])
	
@ServerCommand('wcs_drop')
def drop(command):
	if len(command) == 3:
		weapon = str(command[2])
		player = Player.from_userid(int(command[1]))
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
				
				
@ServerCommand('wcs_strip')
def strip(command):
	if len(command) == 2:
		player = Player.from_userid(int(command[1]))
		entity = Entity.create('player_weaponstrip')
		entity.call_input("Strip", activator=player)
		entity.remove()
	
@ServerCommand("wcs_spawn")
def _spawn(command):
	if len(command) >= 2:
		userid = int(command[1])
		if len(command) == 3:
			force = int(command[2])
		else:
			force = 0
		Player.from_userid(userid).spawn(force)
	
@ServerCommand('wcs_color')
def _color(command):
	if len(command) >= 5:
		userid = int(command[1])
		r = int(command[2])
		g = int(command[3])
		b = int(command[4])
		a = 255
		if len(command) >= 6:
			a = int(command[5])
		player = Player.from_userid(userid)
		player.color = Color(r,g,b,a)
		if len(command) == 7:
			wpn = int(command[6])
			if wpn == 1:
				for weapon in player.weapons():
					weapon.color = Color(r,g,b,a)
	
@ServerCommand('wcs_getdistance')
def _getdistance(command):
	var = str(command[1])
	x1 = float(command[2])
	y1 = float(command[3])
	z1 = float(command[4])
	x2 = float(command[5])
	y2 = float(command[6])
	z2 = float(command[7])
	vec1 = Vector(x1,y1,z1)
	vec2 = Vector(x2,y2,z2)
	distance = vec1.get_distance(vec2)
	ConVar(var).set_float(distance)
	
@ServerCommand('wcs_decimal')
def _decimal(command):
	#'Syntax: wcs_decimal <var> <amount>'
	var = str(command[1])
	amount = int(round(float(command[2])))
	ConVar(var).set_string(str(amount))
	
@Event('player_death')
def player_death(ev):
	if repeat_dict[ev['userid']] != 0:
		repeat_dict[ev['userid']].stop()
		repeat_dict[ev['userid']] = 0
		
@ServerCommand('wcs_explosion')
def wcs_explosion(command):
	userid = int(command[1])
	magnitude = int(command[2])
	radius = int(command[3])
	if len(command) > 4:
		do_damage = int(command[4])
	else:
		do_damage = 1
	player = Player.from_userid(userid)
	ent = Entity.create('env_explosion' )
	ent.set_property_int('m_iMagnitude', magnitude)
	ent.set_property_int('m_iRadiusOverride', radius)
	if do_damage == 1:
		ent.spawn_flags = 8
	else:
		ent.spawn_flags = 1
	ent.owner_handle = inthandle_from_userid(userid)
	ent.spawn()
	ent.origin = player.origin
	ent.call_input('Explode')
	#Delay(0.1, ent.remove)
		
@Event('round_end')
def round_end(ev):
	for player in PlayerIter('all'):
		if repeat_dict[player.userid] != 0:
			repeat_dict[player.userid].stop()
			repeat_dict[player.userid] = 0
			
@Event('player_spawn')
def player_spawn(ev):
	if ev['userid'] not in repeat_dict:
		repeat_dict[ev['userid']] = 0
	if repeat_dict[ev['userid']] != 0:
		repeat_dict[ev['userid']].stop()
		repeat_dict[ev['userid']] = 0	
			
@Event('player_activate')
def player_activate(ev):
	regen_dict[ev['userid']] = 0
	repeat_dict[ev['userid']] = 0	
	
@ServerCommand('wcs_regeneration')
def _regeneration(command):
#<userid> <amount> <time> <maxhp> <maxheal> <radius>
	userid = int(command[1])
	amount = int(command[2])
	time = float(command[3])
	maxhp = int(command[4])
	maxheal = int(command[5])
	radius = float(command[6])
	wcsgroup.setUser(userid,'regeneration_active',1)
	player = Player.from_userid(userid)
	reg_repeat = Repeat(_regeneration_repeat,(player,amount,maxhp,maxheal,radius))
	repeat_dict[player.userid] = reg_repeat
	reg_repeat.start(time)
	
def _regeneration_repeat(player,amount,maxhp,maxheal,radius):
	if wcsgroup.getUser(player.userid,'regeneration_active') == 1:
		if regen_dict[player.userid] < maxheal:
			if player.health+amount <= maxhp:	
				player.health += amount
				if SOURCE_ENGINE_BRANCH	== 'css':
					SayText2('\x04[WCS] \x03You got healed by a spell').send(player.index)
				else:
					SayText2('\x04[WCS] \x05You got healed by a spell').send(player.index)	
				regen_dict[player.userid] += amount
			else:
				player.health = maxhp
			for play in PlayerIter('all'):
				if play != player:
					if play.origin.get_distance(player.origin) <= radius:
						if play.team == player.team:
							if (play.health+amount <= maxhp):
								if SOURCE_ENGINE_BRANCH	== 'css':
									SayText2('\x04[WCS] \x03You got healed by a spell').send(play.index)
								else:
									SayText2('\x04[WCS] \x05You got healed by a spell').send(play.index)									
								play.health += amount
							else:
								play.health = maxhp
	else:
		repeat_dict[player.userid].stop

@ServerCommand('wcs_drug')
def _drug(command):
	userid = int(command[1])
	delay = float(command[2])
	Player.from_userid(userid).client_command('r_screenoverlay effects/tp_eyefx/tp_eyefx')
	Delay(delay, remove_drug, (userid,))
	
def remove_drug(userid):
	Player.from_userid(userid).client_command('r_screenoverlay 0')
	
	
@ServerCommand('wcs_getweapon')
def getweapon(command):
	userid = int(command[1])
	var = str(command[2])
	slot = str(command[3])
	if slot == "1":
		slot = "primary"
	if slot == "2":
		slot = "secondary"
	player = Player.from_userid(userid)
	weapon = player.get_weapon(is_filters=slot)
	if weapon != None:
		ConVar(var).set_string(weapon.classname)
	else:
		ConVar(var).set_int(-1)
	
@ServerCommand('wcs_set_cooldown')
def set_cooldown(command):
	userid = int(command[1])
	amount = int(command[2])
	timed = int(float(time.time()))
	cooldown = wcs.wcs.get_cooldown(userid)
	if cooldown == None:
		cooldown = 0
	wcsgroup.setUser(userid, 'player_ultimate_cooldown', timed+amount-cooldown)
	
@ServerCommand('wcs_get_cooldown')
def get_cooldown(command):
	userid = int(command[1])
	var = str(command[2])
	cooldown = wcs.wcs.get_cooldown(userid)
	timed = int(float(time.time()))
	cooldown = wcsgroup.getUser(userid,'player_ultimate_cooldown')
	downtime = wcs.wcs.get_cooldown(userid)
	if cooldown == None:
		ConVar(var).set_int(downtime)
		return
	ConVar(var).set_int(downtime-(timed-cooldown))
	
	
@ServerCommand('wcs_getviewcoords')
def viewcoord(command):
	userid = int(command[1])
	xvar = str(command[2])
	yvar = str(command[3])
	zvar = str(command[4])
	player = Player(index_from_userid(userid))
	view_vec = player.get_view_coordinates()
	ConVar(xvar).set_float(view_vec[0])
	ConVar(yvar).set_float(view_vec[1])
	ConVar(zvar).set_float(view_vec[2])
	
@ServerCommand('wcs_pushto')
def push_forward(command):
	userid = int(command[1])
	x1 = float(command[2])
	y1 = float(command[3])
	z1 = float(command[4]) + 50.0
	vec = Vector(x1,y1,z1)
	player = Player(index_from_userid(userid))
	player.teleport(None, None, Vector(x1, y1, z1) - player.origin)
	
@ServerCommand('wcs_pushed')
def pushed(command):
	userid = int(command[1])
	x_force = float(command[2])
	y_force = float(command[3])
	z_force = float(command[4])
	vec = Vector(x_force,y_force,z_force)
	player = Player(index_from_userid(userid))
	player.set_property_vector("m_vecBaseVelocity", vec)
	
@ServerCommand('removeweapon')
def remove_weapon(command):
	userid = int(command[1])
	slot_weapon = command[2]
	player = Player(index_from_userid(userid))
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
	
    
@ServerCommand('es_getplayerlocation')
def _get_player_location(command):
	x = str(command[1])
	y = str(command[2])
	z = str(command[3])
	userid = int(command[4])
	player = Player(index_from_userid(userid))
	origin = player.origin
	ConVar(x).set_float(origin[0])
	ConVar(y).set_float(origin[1])
	ConVar(z).set_float(origin[2])
	
'''@ServerCommand('es_math')
def _es_math(command):
	var = str(command[1])
	op = str(command[2])
	amount = int(command[3])
	value = ConVar(var).get_float()
	if op == "+":
		value += amount
		ConVar(var).set_float(value)
	if op == "-":
		value -= amount
		ConVar(var).set_float(value)
	if op == "/":
		value /= amount
		ConVar(var).set_float(value)
	if op == "*":
		value *= amount
		ConVar(var).set_float(value)'''	
    
@ServerCommand('human_spawn')
def _human_spawn_effect(command):
    userid = int(command[1])
    player = Player(index_from_userid(userid))
    origin = player.origin
    queue_command_string('est_effect 10 #a 0 sprites/cbbl_smoke.vmt %s %s %s 40 60 1.5 10 10 0 255 255 255 255 1' % (origin[0], origin[1], origin[2]))
    queue_command_string('est_effect 10 #a 0 sprites/cbbl_smoke.vmt %s %s %s 80 100 1.5 10 10 0 255 255 255 255 1' % (origin[0], origin[1], origin[2]+12.0))
    queue_command_string('est_effect 10 #a 0 sprites/cbbl_smoke.vmt %s %s %s 60 80 1.5 10 10 0 255 255 255 255 2' % (origin[0], origin[1], origin[2]+24.0))

@ServerCommand('orc_spawn')
def _orc_spawn(command):
    userid = int(command[1])
    index = index_from_userid(userid)
    player = Player(index)
    entity = Entity.create('point_tesla')
    entity.set_key_value_int('m_flRadius', 600)
    entity.set_key_value_int('beamcount_min', 1000)
    entity.set_key_value_int('beamcount_max', 6000)
    entity.set_key_value_int('thick_min', 5)
    entity.set_key_value_int('thick_max', 6)
    entity.set_key_value_color('m_Color', Color(255, 71, 36))
    entity.set_key_value_float('lifetime_min', 0.1)
    entity.set_key_value_float('lifetime_max', 0.4)
    entity.set_key_value_float('interval_min', 0.1)
    entity.set_key_value_float('interval_max', 0.2)
    entity.set_key_value_string('texture', 'sprites/laserbeam.vmt')
    entity.teleport(player.origin, None, None)
    entity.spawn()
    entity.teleport(player.origin, None, None)
    entity.call_input('DoSpark')
    entity.call_input('DoSpark')
    entity.call_input('DoSpark')
    entity.call_input('DoSpark')
    entity.call_input('DoSpark')
    entity.call_input('DoSpark')
    entity.remove
    
@ServerCommand('orc_damage')
def orc_damage(command):
    userid = int(command[1])
    attacker = int(command[2])
    atk_player = Player(index_from_userid(attacker))
    player = Player(index_from_userid(userid))
    min = int(command[3])
    max = int(command[4])
    damage = random.randint(min, max)
    queue_command_string('wcs_dealdamage %s %s %s' % (userid, attacker, damage))
    if SOURCE_ENGINE_BRANCH	== 'css':
        SayText2('\x04[WCS] \x04Critical Strike -  \x03You got \x04%s Extra Damage \x03from \x04%s!' % (damage, atk_player.name)).send(player.index)
        SayText2('\x04[WCS] \x04Critical Strike - \x03You did \x04%s Extra Damage \x03to \x04%s!' % (damage, player.name)).send(atk_player.index)
    else:
        SayText2('\x04[WCS] \x04Critical Strike -  \x05You got \x04%s Extra Damage \x05from \x04%s!' % (damage, atk_player.name)).send(player.index)
        SayText2('\x04[WCS] \x04Critical Strike - \x05You did \x04%s Extra Damage \x05to \x04%s!' % (damage, player.name)).send(atk_player.index)	
    origin = player.origin
    atk_origin = atk_player.origin
    queue_command_string('est_effect 3 #a 0 sprites/laserbeam.vmt %s %s %s %s %s %s 0.5 8 8 255 71 36 255' % (atk_origin[0], atk_origin[1], atk_origin[2]+20.0, origin[0], origin[1], origin[2]+20.0))
 
@ServerCommand('orc_grenade')
def orc_grenade(command):
    userid = int(command[1])
    attacker = int(command[2])
    atk_player = Player(index_from_userid(attacker))
    player = Player(index_from_userid(userid))
    dmg = int(command[3])
    mult = float(command[4]) + 1.0
    damage = float(dmg) * mult
    queue_command_string('wcs_dealdamage %s %s %s' % (userid, attacker, int(damage)))
    if SOURCE_ENGINE_BRANCH	== 'css':
        SayText2('\x04[WCS] \x04Critical Grenade -  \x03You got \x04%s Extra Damage \x03from \x04%s!' % (int(damage), atk_player.name)).send(player.index)
        SayText2('\x04[WCS] \x04Critical Grenade - \x03You did \x04%s Extra Damage \x03to \x04%s!' % (int(damage), player.name)).send(atk_player.index)
    else:
        SayText2('\x04[WCS] \x04Critical Grenade -  \x05You got \x04%s Extra Damage \x05from \x04%s!' % (int(damage), atk_player.name)).send(player.index)
        SayText2('\x04[WCS] \x04Critical Grenade - \x05You did \x04%s Extra Damage \x05to \x04%s!' % (int(damage), player.name)).send(atk_player.index)		
    origin = player.origin
    atk_origin = atk_player.origin
    queue_command_string('est_effect 10 #a 0 sprites\laserbeam.vmt %s %s %s 25 26 0.75 8 5 0 255 71 36 255 0' % (origin[0], origin[1], origin[2]+20.0))
    queue_command_string('est_effect 10 #a 0 sprites\laserbeam.vmt %s %s %s 25 26 0.75 8 5 0 255 71 36 255 0' % (origin[0], origin[1], origin[2]+40.0))
    queue_command_string('est_effect 10 #a 0 sprites\laserbeam.vmt %s %s %s 25 26 0.75 8 5 0 255 71 36 255 0' % (origin[0], origin[1], origin[2]+60.0))

@ServerCommand('orc_respawn')
def orc_respawn(command):
    userid = int(command[1])
    player = Player(index_from_userid(userid))
    origin = player.origin
    wcs.wcs.tell(userid, '\x04[WCS] \x04Reincarnation - \x05You wilk \x04Respawn \x05in \x043 seconds!')
    queue_command_string('es_delayed 3 wcs_spawn %s' % userid)
    queue_command_string('es_delayed 3 est_effect 10 #a 0 sprites/laserbeam.vmt %s %s %s 130 131 3 80 20 0 255 71 36 200 10' % (origin[0], origin[1], origin[2]))
    
@ServerCommand('human_bash')
def _human_bash_effect(command):
    userid = int(command[1])
    attacker = int(command[2])
    player = Player(index_from_userid(userid))
    atk_player = Player(index_from_userid(attacker))
    origin = player.origin
    atk_origin = atk_player.origin
    queue_command_string('est_effect 3 #a 0 sprites/cbbl_smoke.vmt %s %s %s %s %s %s 0.5 10 10 255 255 255 255' % (atk_origin[0], atk_origin[1], atk_origin[2]+20.0,origin[0], origin[1], origin[2]+20.0))
    queue_command_string('est_effect 10 #a 0 sprites/cbbl_smoke.vmt %s %s %s 20 45 0.5 25 10 0 255 255 255 255 0' % (origin[0], origin[1], origin[2]+25.0))


@ServerCommand('nightelve_spawn')
def _nightelve_spawn(command):
	userid = int(command[1])
	player = Player(index_from_userid(userid))
	origin = player.origin
	queue_command_string("es_delayed 0.3 est_effect 10 #a 0 sprites/laserbeam.vmt %s %s %s 10 200 2 10 100 0 0 175 0 155 1" % (origin[0], origin[1], origin[2]+20.0))
	queue_command_string("es_delayed 0.2 est_effect 10 #a 0 sprites/laserbeam.vmt %s %s %s 10 200 2 10 100 0 0 175 0 155 1" % (origin[0], origin[1], origin[2]+40.0))

@ServerCommand('thorns_aura')
def _thorns_aura(command):
	victim = int(command[1])
	attacker = int(command[2])
	origin = Player(index_from_userid(victim)).origin
	atk_origin = Player(index_from_userid(attacker)).origin
	min = int(command[3])
	max = int(command[4])
	amount = random.randint(min, max)
	queue_command_string("wcs_dealdamage %s %s %s" % (victim, attacker, amount))
	queue_command_string("est_effect 3 #a 0 sprites/cbbl_smoke.vmt %s %s %s %s %s %s 1 8 8 175 175 255 155" % (atk_origin[0], atk_origin[1], atk_origin[2]+15.0, origin[0], origin[1], origin[2]+15.0))
	queue_command_string("est_effect 3 #a 0 sprites/cbbl_smoke.vmt %s %s %s %s %s %s 1 15 15 175 175 200 155" % (atk_origin[0], atk_origin[1], atk_origin[2]+15.0, origin[0], origin[1], origin[2]+15.0))
	
@ServerCommand('trueshot_aura')
def _trueshot_aura(command):
	victim = int(command[1])
	attacker = int(command[2])
	player_ent = Player(index_from_userid(attacker))
	player = Player(index_from_userid(victim))
	origin = Player(index_from_userid(victim)).origin
	atk_origin = Player(index_from_userid(attacker)).origin
	min = int(command[3])
	max = int(command[4])
	amount = random.randint(min, max)
	queue_command_string("wcs_dealdamage %s %s %s" % (victim, attacker, amount))
	queue_command_string("est_effect 10 #a 0 sprites/laserbeam.vmt %s %s %s 40 41 1 10 100 0 0 175 0 255 1" % (origin[0], origin[1], origin[2]+10.0))
	queue_command_string("est_effect 3 #a 0 sprites/laserbeam.vmt %s %s %s %s %s %s 1 15 15 0 175 0 255" % (origin[0], origin[1], origin[2]+20.0, atk_origin[0], atk_origin[1], atk_origin[2]+20.0))
	queue_command_string("est_effect 10 #a 0 sprites/laserbeam.vmt %s %s %s 40 41 1 10 100 0 0 175 0 255 1" % (origin[0], origin[1], origin[2]+30.0))
	if SOURCE_ENGINE_BRANCH	== 'css':
		SayText2('\x04[WCS] \x03You got \x04%s Extra Damage \x03from \x04%s!' % (amount, player_ent.name)).send(player.index)
		SayText2('\x04[WCS] \x03You did \x04%s Extra Damage \x03to \x04%s' % (amount, player.name)).send(player_ent.index)
	else:
		SayText2('\x04[WCS] \x05You got \x04%s Extra Damage \x05from \x04%s!' % (amount, player_ent.name)).send(player.index)
		SayText2('\x04[WCS] \x05You did \x04%s Extra Damage \x05to \x04%s' % (amount, player.name)).send(player_ent.index)		

@ServerCommand('entanglin_roots')
def _entanglin_roots(command):
	userid = int(command[1])
	range = float(command[2])
	duration = float(command[3])
	player_ent = Player(index_from_userid(userid))
	for player in PlayerIter():
		if player.team != player_ent.team:
			distance = player_ent.origin.get_distance(player.origin)
			if distance <= range:
				if not player.isdead:
					queue_command_string('wcs_setfx freeze %s = 1 %s' % (player.userid, duration))
					if SOURCE_ENGINE_BRANCH	== 'css':
						SayText2('\x04[WCS] \x04Entangling roots - \x03You were stunned by \x04%s!' % player_ent.name).send(player.index)
						SayText2('\x04[WCS] \x05Entangling roots - \x03You stunned \x04%s' % player.name).send(player_ent.index)
					else:
						SayText2('\x04[WCS] \x04Entangling roots - \x05You were stunned by \x04%s!' % player_ent.name).send(player.index)
						SayText2('\x04[WCS] \x05Entangling roots - \x05You stunned \x04%s' % player.name).send(player_ent.index)						
					queue_command_string('est_effect_08 #a 0 sprites/blueglow1.vmt "%s, %s, %s" 60 40 1 1 90 400 0 0 255 0 255 20 1' % (player.origin[0], player.origin[1], player.origin[2]+40))
                    
					
					
@ServerCommand('wcs_teleport_push')
def _push_teleport(command):
    userid = int(command[1])
    force = float(command[2])
    index = index_from_userid(userid)
    player = Player(index)
    origin = player.origin
    coords = player.view_coordinates
    coords -= origin
    player.set_property_vector('localdata.m_vecBaseVelocity', coords*force)

@ServerCommand('hawk_attack')
def _hawk_attack_effect(command):
    userid = int(command[1])
    player = Player(index_from_userid(userid))
    origin = player.origin
    queue_command_string('est_effect_18 #a 0 "%s, %s, %s" 255 2 2 50 100 3 10' % (origin[0], origin[1], origin[2]))
    queue_command_string('est_effect_14 #a 0 models\seagull.mdl "%s, %s, %s" "%s, %s, %s" 1000 6 500' % (origin[0], origin[1], origin[2], origin[0], origin[1], origin[2]+200)) 

  
@ServerCommand('blood_strudel')
def _blood_strudel_effect(command):
    userid = int(command[1])
    player = Player(index_from_userid(userid))
    origin = player.origin
    queue_command_string('est_effect 10 #a 0 decals/bloodstain_003.vmt %s %s %s 250 251 .3 20 20 0 166 29 9 255 10' % (origin[0], origin[1], origin[2]+10))
    queue_command_string('est_effect 10 #a 0 decals/bloodstain_003.vmt %s %s %s 230 231 .3 20 20 0 166 29 9 255 10' % (origin[0], origin[1], origin[2]+30))
    queue_command_string('est_effect 10 #a 0 decals/bloodstain_003.vmt %s %s %s 210 211 .3 20 20 0 166 29 9 255 10' % (origin[0], origin[1], origin[2]+50))
    queue_command_string('est_effect 10 #a 0 decals/bloodstain_003.vmt %s %s %s 190 191 .3 20 20 0 166 29 9 255 10' % (origin[0], origin[1], origin[2]+70))
    queue_command_string('est_effect 10 #a 0 decals/bloodstain_003.vmt %s %s %s 170 171 .3 20 20 0 166 29 9 255 10' % (origin[0], origin[1], origin[2]+90))
    queue_command_string('est_effect 10 #a 0 decals/bloodstain_003.vmt %s %s %s 170 171 .3 20 20 0 166 29 9 255 10' % (origin[0], origin[1], origin[2]+110))
    queue_command_string('est_effect 10 #a 0 decals/bloodstain_003.vmt %s %s %s 190 191 .3 20 20 0 166 29 9 255 10' % (origin[0], origin[1], origin[2]+130))
    queue_command_string('est_effect 10 #a 0 decals/bloodstain_003.vmt %s %s %s 210 211 .3 20 20 0 166 29 9 255 10' % (origin[0], origin[1], origin[2]+150))
    queue_command_string('est_effect 10 #a 0 decals/bloodstain_003.vmt %s %s %s 230 231 .3 20 20 0 166 29 9 255 10' % (origin[0], origin[1], origin[2]+170))
    queue_command_string('est_effect 10 #a 0 decals/bloodstain_003.vmt %s %s %s 250 251 .3 20 20 0 166 29 9 255 10' % (origin[0], origin[1], origin[2]+190))
    queue_command_string('est_effect 3 #a 0 decals/bloodstain_003.vmt  %s %s %s %s %s %s .4 50 50 255 255 255 255' % (origin[0], origin[1], origin[2], origin[0], origin[1], origin[2]+250))
    
@ServerCommand('strudel_effect')
def _strudel_effect(command):
    userid = int(command[1])
    player = Player(index_from_userid(userid))
    origin[2] += 10.0
    Delay(0.1, query_command_string, 'est_effect 10 #a 0 effects/blood_core.vmt %s %s %s 1300 1 3 70 0 0 10 10 10 255 1' % (origin[0], origin[1], origin[2]))
    Delay(0.2, queue_command_string, 'est_effect 10 #a 0 effects/blood_core.vmt %s %s %s 1300 1 3 70 0 0 50 50 50 255 1' % (origin[0], origin[1], origin[2]))
    Delay(0.3, queue_command_string, 'est_effect 10 #a 0 effects/blood_core.vmt %s %s %s 1300 1 3 70 0 0 80 80 80 255 1' % (origin[0], origin[1], origin[2]))
    Delay(0.4, queue_command_string, 'est_effect 10 #a 0 effects/blood_core.vmt %s %s %s 1300 1 3 70 0 0 110 110 110 255 1' % (origin[0], origin[1], origin[2]))
    Delay(0.5, queue_command_string, 'est_effect 10 #a 0 effects/blood_core.vmt %s %s %s 1300 1 3 70 0 0 140 140 140 255 1' % (origin[0], origin[1], origin[2]))
    Delay(0.6, queue_command_string, 'est_effect 10 #a 0 effects/blood_core.vmt %s %s %s 1300 1 3 70 0 0 170 170 170 255 1' % (origin[0], origin[1], origin[2]))
    Delay(0.7, queue_command_string, 'est_effect 10 #a 0 effects/blood_core.vmt %s %s %s 1300 1 3 70 0 0 200 200 200 255 1' % (origin[0], origin[1], origin[2]))
    Delay(0.8, queue_command_string, 'est_effect 10 #a 0 effects/blood_core.vmt %s %s %s 1300 1 3 70 0 0 255 255 255 255 1' % (origin[0], origin[1], origin[2]))   
    
@ServerCommand('red_spawn')
def _red_spawn_effect(command):
    userid = int(command[1])
    player = Player(index_from_userid(userid))

    origin = player.origin
    queue_command_string('est_effect 10 #a 0 vgui/gfx/vgui/cs_logo.vmt %s %s %s 800 90 1.6 60 20 0 255 0 0 255 1' % (origin[0], origin[1], origin[2]))
    queue_command_string('est_effect 10 #a 0 particle\particle_noisesphere.vmt %s %s %s 80 90 1.6 5 10 0 255 0 0 255 1' % (origin[0], origin[1], origin[2]))
    queue_command_string('est_effect 10 #a 0 vgui/gfx/vgui/cs_logo.vmt %s %s %s 800 90 1.6 60 20 0 255 0 0 255 1' % (origin[0], origin[1], origin[2]))
    queue_command_string('est_effect 10 #a 0 particle\particle_noisesphere.vmt %s %s %s 80 90 1.6 5 10 0 255 0 0 255 1' % (origin[0], origin[1], origin[2]))
    origin[2] += 20.0
    queue_command_string('est_effect 10 #a 0 vgui/gfx/vgui/cs_logo.vmt %s %s %s 800 90 1.6 60 20 0 255 0 0 255 1' % (origin[0], origin[1], origin[2]))
    queue_command_string('est_effect 10 #a 0 particle\particle_noisesphere.vmt %s %s %s 80 90 1.6 5 10 0 255 0 0 255 1' % (origin[0], origin[1], origin[2]))
    origin[2] += 20.0
    queue_command_string('est_effect 10 #a 0 vgui/gfx/vgui/cs_logo.vmt %s %s %s 800 90 1.6 60 20 0 255 0 0 255 1' % (origin[0], origin[1], origin[2]))
    queue_command_string('est_effect 10 #a 0 particle\particle_noisesphere.vmt %s %s %s 80 90 1.6 5 10 0 255 0 0 255 1' % (origin[0], origin[1], origin[2]))
    origin[2] += 20.0
    queue_command_string('est_effect 10 #a 0 vgui/gfx/vgui/cs_logo.vmt %s %s %s 800 90 1.6 60 20 0 255 0 0 255 1' % (origin[0], origin[1], origin[2]))
    queue_command_string('est_effect 10 #a 0 particle\particle_noisesphere.vmt %s %s %s 80 90 1.6 5 10 0 255 0 0 255 1' % (origin[0], origin[1], origin[2]))
    origin[2] += 20.0
    queue_command_string('est_effect 10 #a 0 vgui/gfx/vgui/cs_logo.vmt %s %s %s 800 90 1.6 60 20 0 255 0 0 255 1' % (origin[0], origin[1], origin[2]))
    queue_command_string('est_effect 10 #a 0 particle\particle_noisesphere.vmt %s %s %s 80 90 1.6 5 10 0 255 0 0 255 1' % (origin[0], origin[1], origin[2]))
    
@ServerCommand('ice_spawn')
def _ice_spawn_effect(command):
    userid = int(command[1])
    player = Player(index_from_userid(userid))

    coords = player.origin
    coords[2] += 50.0
    origin = player.origin
    queue_command_string('est_effect_14 #a 0 effects/tesla_glow_noz.vmt "%s, %s, %s" "%s, %s, %s" 250 25 95' % (origin[0], origin[1], origin[2], coords[0], coords[1], coords[2]))
    queue_command_string('est_effect_08 #a 0 effects/tesla_glow_noz.vmt "%s, %s, %s" 20 400 1 1 90 400 0 128 64 12 255 10 1' % (origin[0], origin[1], origin[2]))
    queue_command_string('est_effect_06 #a 0 effects/tesla_glow_noz.vmt "%s, %s, %s" "%s, %s, %s"  10 1 1 1 10 0 176 176 255 255 30' % (origin[0], origin[1], origin[2], coords[0], coords[1], coords[2]))
    queue_command_string('est_effect_06 #a 0 effects/tesla_glow_noz.vmt "%s, %s, %s" "%s, %s, %s" 10 1 1 1 10 0 255 0 128 255 30' % (origin[0], origin[1], origin[2], coords[0], coords[1], coords[2]))
    queue_command_string('est_effect 10 #a 0 effects/tesla_glow_noz.vmt %s %s %s 50 101 1 30 40 1 255 255 255 255 10' % (origin[0], origin[1], origin[2]))
    queue_command_string('est_effect 10 #a 0 effects/tesla_glow_noz.vmt %s %s %s 100 101 1 30 40 1 255 0 128 255 10' % (origin[0], origin[1], origin[2]))
    
@ServerCommand('hawk_girl_spawn')
def _hawk_spawn_effect(command):
    userid = int(command[1])
    player = Player(index_from_userid(userid))

    coords = player.origin
    coords[2] += 50.0
    origin = player.origin
    queue_command_string('est_effect_14 #a 0 effects/muzzleflashx.vmt "%s, %s, %s" "%s, %s, %s" 250 25 95' % (origin[0], origin[1], origin[2], coords[0], coords[1], coords[2]))
    queue_command_string('est_effect_08 #a 0 effects/muzzleflashx.vmt "%s, %s, %s" 20 400 1 1 90 400 0 128 64 12 255 10 1' % (origin[0], origin[1], origin[2]))
    queue_command_string('est_effect_06 #a 0 effects/muzzleflashx.vmt "%s, %s, %s" "%s, %s, %s"  10 1 1 1 10 0 176 176 255 255 30' % (origin[0], origin[1], origin[2], coords[0], coords[1], coords[2]))
    queue_command_string('est_effect_06 #a 0 effects/muzzleflashx.vmt "%s, %s, %s" "%s, %s, %s" 10 1 1 1 10 0 255 0 128 255 30' % (origin[0], origin[1], origin[2], coords[0], coords[1], coords[2]))
    queue_command_string('est_effect 10 #a 0 effects/muzzleflashx.vmt %s %s %s 50 101 1 30 40 1 255 255 255 255 10' % (origin[0], origin[1], origin[2]))
    queue_command_string('est_effect 10 #a 0 effects/muzzleflashx.vmt %s %s %s 100 101 1 30 40 1 255 0 128 255 10' % (origin[0], origin[1], origin[2]))
    
@ServerCommand('inner_fire_effect')
def _inner_fire_effect(command):
    userid = int(command[1])
    delay = float(command[2])
    player = Player(index_from_userid(userid))
    entity = Entity.create('env_smokestack')
    entity.set_key_value_int('BaseSpread', 10)
    entity.set_key_value_int('EndSize', 5)
    entity.set_key_value_int('JetLength', 180)
    entity.set_key_value_int('Rate', 40)
    entity.set_key_value_int('renderamt', 255)
    entity.set_key_value_color('rendercolor', Color(255, 255, 255))
    entity.set_key_value_string('SmokeMaterial', 'particle/SmokeStack.vmt')
    entity.set_key_value_int('Speed', 60)
    entity.set_key_value_int('SpreadSpeed', 5)
    entity.set_key_value_int('StartSize', 20)
    entity.set_key_value_int('InitialState', 1)
    entity.teleport(player.origin, None, None)
    entity.spawn()
    entity.set_parent(player, player.lookup_attachment('rfoot'))
    Delay(delay, entity.remove)
    

    
    
    

@ServerCommand('wcs_speed_ulti')
def _speed_ulti(command):
    userid = int(command[1])
    speed = float(command[2])
    delay = float(command[3])
    player = Player(index_from_userid(userid))
    player.speed += speed
    queue_command_string('es_delayed %s playerset speed %s %s' % (delay, userid, player.speed-speed))
    if SOURCE_ENGINE_BRANCH	== 'css':
        SayText2('\x04[WCS] \x03You got \x04%s%% Extra Speed \x03for \x04%s Seconds!' % (speed*100.0, delay)).send(index_from_userid(userid))
    else:
        SayText2('\x04[WCS] \x05You got \x04%s%% Extra Speed \x05for \x04%s Seconds!' % (speed*100.0, delay)).send(index_from_userid(userid))
    
    
	
@ServerCommand('wcs_ice_age')
def _wcs_ice_age(command):
    userid = int(command[1])
    range = float(command[2])
    speed = float(command[3])
    delay = float(command[4])
    player_ent = Player(index_from_userid(userid))
    for player in PlayerIter():
        if player.team != player_ent.team:
            distance = player_ent.origin.get_distance(player.origin)
            if distance <= range:
                if not player.isdead:
                    player.speed -= speed
                    if SOURCE_ENGINE_BRANCH	== 'css':
                        SayText2('\x04[WCS] \x03You were slowed by \x04%s Ice Age!' % player_ent.name).send(player.index)
                        SayText2('\x04[WCS] \x03You slowed \x04%s \x03with your \x04Ice Age' % player.name).send(player_ent.index)
                    else:
                        SayText2('\x04[WCS] \x05You were slowed by \x04%s Ice Age!' % player_ent.name).send(player.index)
                        SayText2('\x04[WCS] \x05You slowed \x04%s \x05with your \x04Ice Age' % player.name).send(player_ent.index)						
                    queue_command_string('es_delayed %s playerset speed %s %s' % (delay, player.userid, player.speed+speed))
                    queue_command_string('est_effect_08 #a 0 sprites/blueglow1.vmt "%s, %s, %s" 60 40 1 1 90 400 0 255 255 255 255 20 1' % (player.origin[0], player.origin[1], player.origin[2]+40))
                    
    
@ServerCommand('wcs_jetpack_ulti')
def _wcs_jetpack_ulti(command):
    userid = int(command[1])
    delay = float(command[2])
    player = Player(index_from_userid(userid))
    player.set_jetpack(1)
    player.push(0, 200, True)
    if SOURCE_ENGINE_BRANCH	== 'css':
        SayText2('\x04[WCS] \x03Flying activated for \x04%s seconds!' % delay)
    else:
        SayText2('\x04[WCS] \x05Flying activated for \x04%s seconds!' % delay)
    queue_command_string('es_delayed %s playerset jetpack %s 0' % (delay, userid))
    
    
	
@ServerCommand('wcs_explode')
def _wcs_explode_command(command):
	userid = int(command[1])
	range = float(command[2])
	damage = int(command[3])
	index = index_from_userid(userid)
	player_ent = Player(index)
	for player in PlayerIter():
		if player.team != player_ent.team:
			distance = player_ent.origin.get_distance(player.origin)
			if distance <= range:
				if not player.isdead:
					queue_command_string('wcs_dealdamage %s %s %s' % (player.userid, player_ent.userid, damage))
					if SOURCE_ENGINE_BRANCH	== 'css':	
						SayText2("\x04[WCS] \x03You were hit by \x04%s's Suicide Explosion!" % player_ent.name).send(player.index)
						SayText2('\x04[WCS] \x03You hit \x04%s \x03with your \x04Suicide Explosion' % player.name).send(player_ent.index)
					else:	
						SayText2("\x04[WCS] \x05You were hit by \x04%s's Suicide Explosion!" % player_ent.name).send(player.index)
						SayText2('\x04[WCS] \x05You hit \x04%s \x05with your \x04Suicide Explosion' % player.name).send(player_ent.index)
						
@ServerCommand('wcs_chainlightning')
def _wcs_chainlightning_command(command):
    userid = int(command[1])
    range = float(command[2])
    damage = int(command[3])
    targets = int(command[4])
    index = index_from_userid(userid)
    player_ent = Player(index)
    x = 0
    for player in PlayerIter():
        if x <= targets:
            if player.team != player_ent.team:
                distance = player_ent.origin.get_distance(player.origin)
                if distance <= range:
                    if not player.isdead:
                        queue_command_string('wcs_dealdamage %s %s %s' % (player.userid, player_ent.userid, damage))
                        chainlightning_effect(userid, player.userid)
						
                        if SOURCE_ENGINE_BRANCH	== 'css':			
                            SayText2('\x04[WCS] \x03You were hit by \x04%s Chainlightning!' % player_ent.name).send(player.index)
                            SayText2('\x04[WCS] \x03You hit \x04%s \x03with your \x04Chainlightning' % player.name).send(player_ent.index)
                        else:
                            SayText2('\x04[WCS] \x05You were hit by \x04%s Chainlightning!' % player_ent.name).send(player.index)
                            SayText2('\x04[WCS] \x05You hit \x04%s \x05with your \x04Chainlightning' % player.name).send(player_ent.index)							
                        x += 1
                    
	
@ServerCommand('wcs_doteleport')
def _doteleport_command(command):
	userid = int(command[1])
	index = index_from_userid(userid)
	player = Player(index)
	view_vector = player.view_coordinates
	queue_command_string('wcs_teleport %s %s %s %s' % (userid, view_vector[0], view_vector[1], view_vector[2]))
	
	
@ServerCommand('wcs_changeteam')
def _changeteam_command(command):
	userid = int(command[1])
	index = index_from_userid(userid)
	player = Player(index)
	team = int(command[2])
	player.team = team
	
@ServerCommand('wcs_centermsg')
def _centermessage_command(command):
	message = command.arg_string
	for player in PlayerIter():
		if SOURCE_ENGINE_BRANCH == "css":
			queue_command_string("es_centertell %s %s" %(player.userid,message))
		else:
			HudMsg(message, -1, 0.35,hold_time=5.0).send(player.index)
		
@ServerCommand('wcs_centertell')
def _centertell(command):
	userid = int(command[1])
	command_string = command.arg_string
	command_string = command_string.replace(str(userid)+" ", '')
	index = index_from_userid(userid)
	if SOURCE_ENGINE_BRANCH == "css":
		queue_command_string("es_centertell %s %s" %(userid,command_string))
	else:
		HudMsg(command_string, -1, 0.35,hold_time=5.0).send(index)

		
@ServerCommand('wcs_delayed')
def _delayed_command(command):
	delay = float(command[1])
	command_string = command.arg_string
	command_parts = command_string.split(' ')
	command_parts.remove(command_parts[0])
	command_parts_text = ''
	for arg in command_parts:
		command_parts_text = ''+command_parts_text+' '+arg
	command_parts_text = command_parts_text.replace(' ', '', 1)
	Delay(delay, queue_command_string, (('%s' % command_parts_text),))	

