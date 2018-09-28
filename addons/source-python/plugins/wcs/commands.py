from colors import Color
from commands.server import ServerCommand
from core import SOURCE_ENGINE_BRANCH
from cvars import ConVar
from effects.base import TempEntity
from engines.precache import Model
from engines.server import queue_command_string, execute_server_command
from engines.trace import ContentMasks
from engines.trace import engine_trace
from engines.trace import GameTrace
from engines.trace import Ray
from engines.trace import TraceFilterSimple
from entities import BaseEntityGenerator
from entities import TakeDamageInfo
from entities.constants import DamageTypes, MoveType
from entities.entity import Entity
from entities.hooks import EntityCondition
from entities.hooks import EntityPreHook
from events import Event
from events.hooks import PreEvent
from filters.players import PlayerIter
from filters.recipients import RecipientFilter
from listeners.tick import Delay, Repeat
import math
from mathlib import Vector,QAngle
from memory import make_object
from messages import Fade, FadeFlags, HudMsg, SayText2, TextMsg
from messages.base import Shake
from players.helpers import index_from_userid, playerinfo_from_userid, index_from_playerinfo, userid_from_index, edict_from_userid,inthandle_from_userid,playerinfo_from_index
from players.entity import Player
from random import choice,randint
import string
import time
import wcs
from wcs import changerace
from wcs import wcsgroup
from weapons.entity import Weapon




entity_health = {}

weapon_list = ["weapon_ak47","weapon_aug","weapon_awp","weapon_bizon","weapon_c4","weapon_cz75a","weapon_deagle","weapon_decoy","weapon_elite","weapon_famas","weapon_fiveseven","weapon_flashbang","weapon_g3sg1","weapon_galil","weapon_galilar","weapon_glock","weapon_hegrenade","weapon_incgrenade","weapon_hkp2000","weapon_knife","weapon_m249","weapon_m3","weapon_m4a1","weapon_m4a1_silencer","weapon_mac10","weapon_mag7","weapon_molotov","weapon_mp5navy","weapon_mp7","weapon_mp9","weapon_negev","weapon_nova","weapon_p228","weapon_p250","weapon_p90","weapon_sawedoff","weapon_scar17","weapon_scar20","weapon_scout","weapon_sg550","weapon_sg552","weapon_sg556","weapon_ssg08","weapon_smokegrenade","weapon_taser","weapon_tec9","weapon_tmp","weapon_ump45","weapon_usp","weapon_usp_silencer","weapon_xm1014","weapon_revolver"]

anti_falldamage = {}
repeat_dict = {}
for player in PlayerIter('all'):
	repeat_dict[player.userid] = 0
	
	
# =============================================================================
# >> SERVER COMMANDS
# =============================================================================	
	
@ServerCommand('wcs_absorb')
def absorb(command):
	userid = int(command[1])
	amount = float(command[2])
	if exists(userid):
		wcsgroup.setUser(userid,'absorb',amount)

	
@ServerCommand('wcs_ambush')
def test(command):
    player = Player.from_userid(int(command[1]))
    target = Player.from_userid(int(command[2]))
    if target:
        angles = target.get_view_angle()
        angle = math.radians(target.get_view_angle()[1])  # (0, angle)
        x = -40 * math.cos(angle)
        y = -40 * math.sin(angle)
 
        new_position = Vector(
            target.origin[0] + x,
            target.origin[1] + y,
            target.origin[2])
 
        # Check if there's enough space behind the target.
        trace = check_space(new_position, player.mins, player.maxs)
       
        # Did the trace hit something solid?
        if trace.did_hit():
            # Increase the height(z) of the new position,
            # in case the target was on sloped terrain.
            new_position[2] += 20
 
            # Is there enough space now?
            trace2 = check_space(new_position, player.mins, player.maxs)
            if trace2.did_hit():
                # There's still something solid behind the target.
                # Could be a wall or some other object.
                return
 
        # teleport(position, rotation, velocity)
        player.teleport(new_position, None, None)
        player.set_view_angle(angles)
		
			
@ServerCommand('wcs_aoe')
def wcs_aoe(command):
	userid = int(command[1])
	attacker_userid = int(command[2])
	radius = float(command[3])
	damage = int(command[4])
	if exists(userid):
		victim = Player.from_userid(userid)
	else:
		return
	if exists(attacker_userid):
		attacker = Player.from_userid(attacker_userid)
	else:
		return
	for player in PlayerIter('alive'):
		if player.team == victim.team:
			if player.origin.get_distance(victim.origin) <= radius:
				queue_command_string("es wcs_dealdamage %s %s %s" % (player.userid,attacker_userid,damage))
				
				
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
	userid = command[1]
	if userid != '':
		userid = int(userid)
	else:
		return
	if exists(userid):
		command_string = command.arg_string
		command_string = command_string.replace(str(userid)+" ", '')
		index = index_from_userid(userid)
		if SOURCE_ENGINE_BRANCH == "css":
			queue_command_string("es_centertell %s %s" %(userid,command_string))
		else:
			HudMsg(command_string, -1, 0.35,hold_time=5.0).send(index)
					

@ServerCommand('wcs_changeteam')
def _changeteam_command(command):
	userid = int(command[1])
	if exists(userid):
		player = Player.from_userid(userid)
		team = int(command[2])
		player.team = team
					
				
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
		if exists(userid):
			player = Player.from_userid(userid)
			player.color = Color(r,g,b,a)
			if len(command) == 7:
				wpn = int(command[6])
				if wpn == 1:
					for weapon in player.weapons():
						weapon.color = Color(r,g,b,a)
						
						
@ServerCommand('wcs_create_prop')
def create_prop(command):
	userid = int(command[1])
	propname = str(command[2])
	prophealth = int(command[3])
	if "models/" not in propname:
		propname = "models/"+propname
	model = Model(propname)
	player = Player.from_userid(userid)
	entity = Entity.create('prop_physics_multiplayer')
	entity.origin = player.view_coordinates
	entity.set_model(model)
	entity_health[entity.index] = prophealth
	entity.set_property_uchar("m_takedamage",4)
	entity.spawn()
						
						
@ServerCommand('wcs_dealdamage')
def _deal_damage(command):
	victim = int(command[1])
	attacker = int(command[2])
	damage	= int(command[3])
	if len(command) > 4:
		weapon = str(command[4])
	else:
		weapon = None
	if exists(victim) and exists(attacker):
		victim_player = Player.from_userid(victim)
		attacker_player = Player.from_userid(attacker)
		victim_player.target_name = "wcs_hurtme"
		entity = Entity.create('point_hurt')
		entity.set_key_value_string("DamageTarget","wcs_hurtme")
		entity.damage = damage
		entity.damage_type = 0
		if weapon != None:
			entity.set_key_value_string("classname",weapon)
		entity.spawn()
		entity.call_input("Hurt",activator=attacker_player)
		victim_player.target_name = "wcs_donthurtme"
		entity.remove()
		
						
@ServerCommand('wcs_decimal')
def _decimal(command):
	var = str(command[1])
	amount = int(round(float(command[2])))
	ConVar(var).set_string(str(amount))
	
	
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
	
	
@ServerCommand('wcs_doteleport')
def _doteleport_command(command):
	userid = int(command[1])
	if exists(userid):
		player = Player.from_userid(userid)
		view_vector = player.view_coordinates
		queue_command_string('wcs_teleport %s %s %s %s' % (userid, view_vector[0], view_vector[1], view_vector[2]))


@ServerCommand('wcs_drop')
def drop(command):
	if len(command) == 3:
		weapon = str(command[2])
		if exists(int(command[1])):
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
						
						
@ServerCommand('wcs_drug')
def _drug(command):
	userid = int(command[1])
	delay = float(command[2])
	if exists(userid):
		Player.from_userid(userid).client_command('r_screenoverlay effects/tp_eyefx/tp_eyefx')
		Delay(delay, remove_drug, (userid,))
		
		
@ServerCommand('wcs_evasion')
def wcs_evasion(command):
	userid = int(command[1])
	onoff = int(command[2])
	chance = int(command[3])
	wcsgroup.setUser(userid,'evasion',onoff)
	wcsgroup.setUser(userid,'evasion_chance',chance)
	
	
@ServerCommand('wcs_explode')
def _wcs_explode_command(command):
	userid = int(command[1])
	range = float(command[2])
	damage = int(command[3])
	if exists(userid):
		player_ent = Player.from_userid(userid)
		for player in PlayerIter():
			if player.team != player_ent.team:
				distance = player_ent.origin.get_distance(player.origin)
				if distance <= range:
					if not player.isdead:
						queue_command_string('wcs_dealdamage %s %s %s' % (player.userid, player_ent.userid, damage))
						wcs.wcs.tell(player.userid,"\x04[WCS] \x05You were hit by \x04%s's Suicide Explosion!" % player_ent.name)
						wcs.wcs.tell(player_ent.userid,'\x04[WCS] \x05You hit \x04%s \x05with your \x04Suicide Explosion' % player.name)
						
		
@ServerCommand('wcs_explosion')
def wcs_explosion(command):
	userid = int(command[1])
	magnitude = int(command[2])
	radius = int(command[3])
	if len(command) > 4:
		do_damage = int(command[4])
	else:
		do_damage = 1
	if exists(userid):
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

		
@ServerCommand('wcs_explosion_point')
def wcs_explosion_point(command):
	userid = int(command[1])
	x = float(command[2])
	y = float(command[3])
	z = float(command[4])
	magnitude = int(command[5])
	radius = int(command[6])
	if exists(userid):
		ent = Entity.create('env_explosion')
		ent.set_property_int('m_iMagnitude', magnitude)
		ent.set_property_int('m_iRadiusOverride', radius)	
		ent.owner_handle = inthandle_from_userid(userid)
		ent.spawn()
		ent.origin = Vector(x,y,z)
		ent.call_input('Explode')		


@ServerCommand('wcs_extinguish')
def wcs_extinguish(command):
	userid = int(command[1])
	Player.from_userid(userid).ignite_lifetime(0)		

	
@ServerCommand('wcs_fade')
def fade(command):
	userid = int(command[1])
	r = int(command[2])
	g = int(command[3])
	b = int(command[4])
	a = int(command[5])
	time = float(command[6])
	color = Color(r,g,b,a)
	if exists(userid):
		Fade(int(time), int(time),color,FadeFlags.PURGE).send(Player.from_userid(userid).index)
		
		
@ServerCommand('wcs_fire')
def wcs_fire(command):
	userid = int(command[1])
	duration = float(command[2])
	Player.from_userid(userid).ignite_lifetime(duration)
	
	
@ServerCommand(['wcs_getactiveweapon','wcs_getgun'])
def active_weapon(command):
	userid = int(command[1])
	var = str(command[2])
	if exists(userid):
		player = Player.from_userid(userid)
		ConVar(var).set_string(player.active_weapon.classname)
		
		
@ServerCommand('wcs_getcolors')
def get_colors(command):
	userid = int(command[1])
	r = command[2]
	g = command[3]
	b = command[4]
	a = command[5]
	if exists(userid):
		ConVar(r).set_int(Player.from_userid(userid).color[0])
		ConVar(g).set_int(Player.from_userid(userid).color[1])
		ConVar(b).set_int(Player.from_userid(userid).color[2])
		ConVar(a).set_int(Player.from_userid(userid).color[3])
		
	
@ServerCommand(['wcs_getcooldown','wcs_get_cooldown'])
def get_cooldown(command):
	userid = int(command[1])
	var = str(command[2])
	if exists(userid):
		cooldown = wcs.wcs.get_cooldown(userid)
		timed = int(float(time.time()))
		cooldown = wcsgroup.getUser(userid,'player_ultimate_cooldown')
		downtime = wcs.wcs.get_cooldown(userid)
		if cooldown == None:
			ConVar(var).set_int(downtime)
			return
		ConVar(var).set_int(downtime-(timed-cooldown))

		
@ServerCommand('wcs_getdeaths')
def _get_deaths(command):
	userid = int(command[1])
	var = str(command[2])
	if exists(userid):
		ConVar(var).set_int(Player.from_userid(userid).deaths)	

		
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
		
		
@ServerCommand('wcs_getgravity')
def _get_gravity(command):
	userid = int(command[1])
	var = str(command[2])
	if exists(userid):
		ConVar(var).set_float(Player.from_userid(userid).gravity)		
	
	
@ServerCommand('wcs_getplayerindex')
def _get_index(command):
	userid = int(command[1])
	var = str(command[2])
	if exists(userid):
		ConVar(var).set_int(index_from_userid(userid))
		
		
@ServerCommand('wcs_getrandomrace')
def random_race(command):
	userid = int(command[1])
	var = str(command[2])
	if exists(userid):
		race_list = []
		races = wcs.wcs.racedb.getAll()
		allraces = races.keys()
		for number, race in enumerate(allraces):
			v = changerace.canUse(userid,race)
			if not v:
				race_list.append(race)
		if len(race_list):
			chosen = str(choice(race_list))
			ConVar(var).set_string(chosen)
		
		
@ServerCommand('wcs_getscore')
def _get_deaths(command):
	userid = int(command[1])
	var = str(command[2])
	if exists(userid):
		ConVar(var).set_int(Player.from_userid(userid).kills)
		
		
@ServerCommand('wcs_getviewcoords')
def viewcoord(command):
	userid = int(command[1])
	xvar = str(command[2])
	yvar = str(command[3])
	zvar = str(command[4])
	if exists(userid):
		player = Player(index_from_userid(userid))
		view_vec = player.get_view_coordinates()
		ConVar(xvar).set_float(view_vec[0])
		ConVar(yvar).set_float(view_vec[1])
		ConVar(zvar).set_float(view_vec[2])


@ServerCommand('wcs_getviewentity')
def getViewEntity(command):
	if len(command) == 3:
		if exists(int(command[1])):
			ConVar(str(command[2])).set_string(str(Player.from_userid(int(command[1])).get_view_entity().index))

			
@ServerCommand('wcs_getviewplayer')
def getViewPlayer(command):
	if len(command) == 3:
		if exists(int(command[1])):
			ConVar(str(command[2])).set_string(str(Player.from_userid(int(command[1])).get_view_player().userid))
		
		
@ServerCommand('wcs_getwallbetween')
def get_wall_between(command):
	var = str(command[1])
	user_one = int(command[2])
	user_two = int(command[3])
	origin_vector = Player.from_userid(user_one).origin
	direction_vector = Player.from_userid(user_two).origin
	trace = GameTrace()
	engine_trace.trace_ray(Ray(origin_vector, direction_vector), ContentMasks.ALL, None, trace)
	ConVar(var).set_int(trace.did_hit_world())

	
@ServerCommand('wcs_getweapon')
def getweapon(command):
	userid = int(command[1])
	var = str(command[2])
	slot = str(command[3])
	if slot == "1":
		slot = "primary"
	if slot == "2":
		slot = "secondary"
	if exists(userid):
		player = Player.from_userid(userid)
		weapon = player.get_weapon(is_filters=slot)
		if weapon != None:
			ConVar(var).set_string(weapon.classname)
		else:
			ConVar(var).set_int(-1)
	
			
@ServerCommand('wcs_give')
def _give(command):
	userid = int(command[1])
	weapon = command[2]
	if "weapon_" not in weapon:
		weapon = "weapon_"+command[2]
	if exists(userid):
		Player.from_userid(userid).give_named_item(weapon)
		
		
@ServerCommand('wcs_leech')
def wcs_leech(command):
	userid = int(command[1])
	victim_uid = int(command[2])
	amount = int(command[3])
	player = Player.from_userid(userid)
	victim = Player.from_userid(victim_uid)
	if victim.health - amount < 0:
		player.health += victim.health
		queue_command_string("es wcs_dealdamage %s %s %s" % (victim_uid,userid,amount))
	else:
		player.health += amount
		queue_command_string("es wcs_dealdamage %s %s %s" % (victim_uid,userid,amount))
	print(victim.armor)
		
		
@ServerCommand('wcs_noflash')
def noflash(command):
	userid = int(command[1])
	on_off = int(command[2])
	if exists(userid):
		wcsgroup.setUser(userid,'noflash',on_off)
		
		
@ServerCommand('wcs_overlay')
def wcs_overlay(command):
	userid = int(command[1])
	overlay = str(command[2])
	duration = float(command[3])
	if exists(userid):
		create_overlay(userid,overlay,duration)
		
	
@ServerCommand('wcs_pushed')
def pushed(command):
	userid = int(command[1])
	x_force = float(command[2])
	y_force = float(command[3])
	z_force = float(command[4])
	if exists(userid):
		vec = Vector(x_force,y_force,z_force)
		player = Player(index_from_userid(userid))
		player.set_property_vector("m_vecBaseVelocity", vec)	

			
@ServerCommand('wcs_pushto')
def push_forward(command):
	userid = int(command[1])
	if exists(userid):
		player = Player.from_userid(userid)
		if len(command) >= 5:
			x1 = float(command[2])
			y1 = float(command[3])
			z1 = float(command[4])
			force = float(command[5])
			coord = Vector(x1,y1,z1)
		if len(command) < 5:
			coords = command[2].split(',')
			force = float(command[3])
			coord = Vector(float(coords[0],float(coords[1]),float(coords[2])))
		loca = player.origin
		coord -= loca
		coord = coord * float(force)
		player.set_property_vector('m_vecBaseVelocity',coord)
			
		
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
	
	
@ServerCommand('wcs_regeneration')
def _regeneration(command):
#<userid> <amount> <time> <maxhp> <maxheal> <radius>
	userid = int(command[1])
	amount = int(command[2])
	time = float(command[3])
	maxhp = int(command[4])
	maxheal = int(command[5])
	radius = float(command[6])
	if exists(userid):
		wcsgroup.setUser(userid,'regeneration_active',1)
		player = Player.from_userid(userid)
		repeat_dict[player.userid] = Repeat(_regeneration_repeat,(player,amount,maxhp,maxheal,radius))
		repeat_dict[player.userid].start(time)
		
		
@ServerCommand('wcs_removeweapon')
def remove_weapon(command):
	userid = int(command[1])
	slot_weapon = command[2]
	if exists(userid):
		player = Player.from_userid(userid)
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
	
	
@ServerCommand('wcs_resize')
def wcs_resize(command):
	userid = int(command[1])
	size = float(command[2])
	if exists(userid):
		player = Player.from_userid(userid)
		player.set_property_float("m_flModelScale",size)
		
		
@ServerCommand(['wcs_setcooldown','wcs_set_cooldown'])
def set_cooldown(command):
	userid = int(command[1])
	amount = int(command[2])
	timed = int(float(time.time()))
	if exists(userid):
		cooldown = wcs.wcs.get_cooldown(userid)
		if cooldown == None:
			cooldown = 0
		wcsgroup.setUser(userid, 'player_ultimate_cooldown', timed+amount-cooldown)


@ServerCommand('wcs_setdeaths')
def _set_deaths(command):
	userid = int(command[1])
	amount = int(command[2])
	if exists(userid):
		Player.from_userid(userid).deaths = amount	


@ServerCommand('wcs_setgravity')
def gravity(command):
	if len(command) == 3:
		Player.from_userid(int(command[1])).gravity = float(command[2])	

	
@ServerCommand('wcs_setmodel')
def set_model(command):
	userid = int(command[1])
	model_str = str(command[2])
	if exists(userid):
		if ".mdl" not in model_str:
			model_str = model_str+".mdl"
		if "models/" not in model_str:
			model_str = "models/"+model_str
		model = Model(model_str)
		player = Player.from_userid(userid)
		player.model = model
	
	
@ServerCommand('wcs_setresist')
def set_resist(command):
	userid = int(command[1])
	amount = float(command[2])
	weapon = str(command[3])
	if exists(userid):
		wcsgroup.setUser(userid,'resist_'+weapon,amount)
		
	
@ServerCommand('wcs_setscore')
def _set_deaths(command):
	userid = int(command[1])
	amount = int(command[2])
	if exists(userid):
		Player.from_userid(userid).kills = amount			

	
@ServerCommand('wcs_shake')
def wcs_shake(command):
	userid = int(command[1])
	amplitude = float(command[2])
	frequency = float(command[3])
	duration = float(command[4])
	Shake(amplitude, duration, frequency).send(index_from_userid(userid))
	
	
@ServerCommand("wcs_spawn")
def _spawn(command):
	if len(command) >= 2:
		userid = int(command[1])
		if exists(userid):
			if len(command) == 3:
				force = int(command[2])
			else:
				force = 0
			Player.from_userid(userid).spawn(force)
			
			
@ServerCommand('wcs_speed_ulti')
def _speed_ulti(command):
	userid = int(command[1])
	speed = float(command[2])
	delay = float(command[3])
	if exists(userid):
		player = Player.from_userid(userid)
		player.speed += speed
		queue_command_string('es_delayed %s playerset speed %s %s' % (delay, userid, player.speed-speed))
		wcs.wcs.tell(player.userid,'\x04[WCS] \x05You got \x04%s%% Extra Speed \x05for \x04%s Seconds!' % (speed*100.0, delay))
			
			
@ServerCommand('wcs_steal')
def wcs_steal(command):
	userid = int(command[1])
	victim_uid = int(command[2])
	amount = int(command[3])
	player = Player.from_userid(userid)
	victim = Player.from_userid(victim_uid)
	if victim.cash - amount < 0:
		player.cash += victim.cash
		victim.cash = 0
	else:
		player.cash += amount
		victim.cash -= amount
		
				
@ServerCommand('wcs_strip')
def strip(command):
	if len(command) == 2:
		if exists(int(command[1])):
			player = Player.from_userid(int(command[1]))
			entity = Entity.create('player_weaponstrip')
			entity.call_input("Strip", activator=player)
			entity.remove()
		

@ServerCommand('wcs_teleport')
def _wcs_teleport(command):
	userid = int(command[1])
	x = float(command[2])
	y = float(command[3])
	z = float(command[4])
	target_location = Vector(x,y,z,)
	player = Player.from_userid(userid)
	origin = player.origin
	angles = QAngle(*player.get_property_vector('m_angAbsRotation'))
	forward = Vector()
	right = Vector()
	up = Vector()
	angles.get_angle_vectors(forward, right, up)
	forward.normalize()
	forward *= 10.0
	loop_limit = 100
	can_teleport = 1
	while is_player_stuck(player.index, target_location):
		target_location -= forward
		loop_limit -= 1
		if target_location.get_distance(origin) <= 10.0 or loop_limit < 1:
			can_teleport = 0
			break
	if can_teleport == 1:
		player.teleport(target_location,None,None)
		
		
@ServerCommand('wcs_teleport_push')
def _push_teleport(command):
	userid = int(command[1])
	force = float(command[2])
	if exists(userid):
		player = Player.from_userid(userid)
		origin = player.origin
		coords = player.view_coordinates
		coords -= origin
		player.set_property_vector('localdata.m_vecBaseVelocity', coords*force)
			

# =============================================================================
# >> HOOKS
# =============================================================================	
		

@EntityPreHook(EntityCondition.equals_entity_classname('prop_physics_multiplayer'), 'on_take_damage')
def take_damage_hook(stack_data):
	take_damage_info = make_object(TakeDamageInfo, stack_data[1])
	attacker = Entity(take_damage_info.attacker)
	victim = make_object(Entity, stack_data[0])
	if victim.index in entity_health:
		damage = take_damage_info.damage
		if entity_health[victim.index] <= 0:
			Delay(0.1,victim.remove)
		else:
			entity_health[victim.index] -= damage
	else:
		return
	

# =============================================================================
# >> EVENTS
# =============================================================================	

	
@Event('player_activate')
def player_activate(ev):
	repeat_dict[ev['userid']] = 0
	
	
@Event('player_blind')
def player_blind(ev):
	noflash = wcsgroup.getUser(int(ev['userid']),'noflash')
	if noflash == 1:
		player = Player.from_userid(int(ev['userid']))
		player.set_property_float('m_flFlashDuration',0.0)
		player.set_property_float('m_flFlashMaxAlpha',0.0)	


@Event('player_death')
def player_death(ev):
	if valid_repeat(repeat_dict[ev['userid']]):
		repeat_dict[ev['userid']].stop()
		repeat_dict[ev['userid']] = 0
		
		
@Event('round_end')
def round_end(ev):
	for user in repeat_dict:
		if valid_repeat(repeat_dict[user]):
			repeat_dict[user].stop()
			repeat_dict[user] = 0
	for player in PlayerIter('all'):
		for weapon in weapon_list:
			wcsgroup.setUser(player.userid,'resist_'+weapon,0.0)
			
			
@Event('player_hurt')
def player_hurt(ev):
	userid = int(ev['userid'])
	if wcsgroup.getUser(userid,'noflash') == 1:
		remove_overlay(index_from_userid(userid))	

		
@PreEvent('player_hurt')
def pre_hurt(ev):
	victim = Player.from_userid(int(ev['userid']))
	if ev['attacker'] != 0:
		attacker = Player.from_userid(int(ev['attacker']))
		weapon = ev['weapon']
		damage = int(ev['dmg_health'])
		absorb = wcsgroup.getUser(victim.userid,'absorb')
		if absorb != None:
			absorb = float(absorb)
			if absorb > 0:
				absorb_dmg = damage*absorb
				if int(absorb_dmg) > 0:
					victim.health += int(absorb_dmg)
					wcs.wcs.tell(victim.userid,'\x04[WCS] \x05You absorbed %s damage!' % int(absorb_dmg))
				return
		resist = wcsgroup.getUser(victim.userid,'resist_'+weapon)
		if resist != None:
			resist = float(resist)
			if resist > 0:
				resist_dmg = damage*resist
				if int(resist_dmg) > 0:
					victim.health += int(resist_dmg)
					wcs.wcs.tell(victim.userid,'\x04[WCS] \x05You resisted %s damage!' % int(absorb_dmg))
		evasion = wcsgroup.getUser(victim.userid,'evasion')
		evasion_chance = wcsgroup.getUser(victim.userid,'evasion_chance')
		if evasion != None:
			evasion  = int(evasion)
			if evasion > 0:
				if randint(0,100) <= int(evasion_chance):
					victim.health += damage
					wcs.wcs.tell(victim.userid,'\x04[WCS] \x05You evaded %s damage!' % damage)			
	else:
		falldamage = wcsgroup.getUser(victim.userid,'falldamage')
		if falldamage != None:
			falldamage = float(falldamage)
			if falldamage != 1.0:
				damage = int(ev['dmg_health'])
				falldamage_dmg = damage-(damage*falldamage)
				if falldamage_dmg > 0:
					victim.health += int(falldamage_dmg)
					wcs.wcs.tell(victim.userid,'\x04[WCS] \x05You blocked %s falldamage!' % int(falldamage_dmg))		
			
			
@Event('player_spawn')
def player_spawn(ev):
	wcsgroup.setUser(ev['userid'],'absorb',0.0)
	wcsgroup.setUser(ev['userid'],'noflash',0)
	if ev['userid'] not in repeat_dict:
		repeat_dict[ev['userid']] = 0
	if repeat_dict[ev['userid']] != 0:
		repeat_dict[ev['userid']].stop()
		repeat_dict[ev['userid']] = 0	
			

# =============================================================================
# >> HELPER FUNCTIONS
# =============================================================================	

def check_space(position, mins, maxs):
    mask=ContentMasks.ALL
    generator=BaseEntityGenerator
    ray = Ray(position, position, mins, maxs)
 
    trace = GameTrace()
    engine_trace.trace_ray(ray, mask, TraceFilterSimple(generator()), trace)
    return trace
		
		
def create_overlay(userid,overlay,duration):
	if exists(userid):
		player = Player.from_userid(userid)
		player.client_command('r_screenoverlay %s' % overlay)
		player.delay(duration, remove_overlay, (player.index,))
		

def exists(userid):
	try:
		index_from_userid(userid)
	except ValueError:
		return False
	return True
	
	

def is_player_stuck(player_index,origin):
    '''Return whether or not the given player is stuck in solid.'''
    
    # Get the player's PlayerInfo instance...
    player_info = playerinfo_from_index(player_index)
    
    # Get the player's origin...
    #origin = player_info.origin
    
    # Get a Ray object based on the player physic box...
    ray = Ray(origin, origin, player_info.mins,
        player_info.maxs)
        
    # Get a new GameTrace instance...
    trace = GameTrace()
    
    # Do the trace...
    engine_trace.trace_ray(ray, ContentMasks.PLAYER_SOLID, TraceFilterSimple(
        PlayerIter()), trace)
        
    # Return whether or not the trace did hit...
    return trace.did_hit()

	
def _regeneration_repeat(player,amount,maxhp,maxheal,radius):
	if exists(player.userid):
		if wcsgroup.getUser(player.userid,'regeneration_active') == 1:
			if repeat_dict[player.userid] < maxheal:
				if player.health+amount <= maxhp:	
					player.health += amount
					wcs.wcs.tell(player.userid,'\x04[WCS] \x05You got healed by a spell')
					repeat_dict[player.userid] += amount
				else:
					player.health = maxhp
				for play in PlayerIter('all'):
					if play != player:
						if play.origin.get_distance(player.origin) <= radius:
							if play.team == player.team:
								if (play.health+amount <= maxhp):
									wcs.wcs.tell(play.userid,'\x04[WCS] \x05You got healed by a spell')
									play.health += amount
								else:
									play.health = maxhp
		else:
			if valid_repeat(repeat_dict[player.userid]) == 1:
				if repeat_dict[player.userid].status == RepeatStatus.RUNNING:
					repeat_dict[player.userid].stop
	
	
def remove_drug(userid):
	if exists(userid):
		Player.from_userid(userid).client_command('r_screenoverlay 0')

	
def remove_overlay(index):
    player = Player(index)
    player.client_command('r_screenoverlay 0')
		

def valid_repeat(repeat):
	try:
		if repeat.status == RepeatStatus.RUNNIN:
			return True
	except:
		return False