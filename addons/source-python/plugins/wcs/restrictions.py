from entities.helpers import edict_from_pointer, index_from_pointer, edict_from_baseentity
from players.helpers import index_from_userid, playerinfo_from_userid, index_from_playerinfo, userid_from_index, edict_from_userid
from entities.hooks import EntityCondition
from entities.hooks import EntityPreHook
from filters.players import PlayerIter
from memory import make_object
from players.entity import Player
from events import Event
from mathlib import NULL_VECTOR
from entities.entity import Entity
from weapons.restrictions import WeaponRestrictionHandler
import string
from weapons.manager import weapon_manager
from commands.server import ServerCommand

restrictions = {}
buffer = {}
my_handler = WeaponRestrictionHandler()

restrict_all = "weapon_ak47weapon_augweapon_awpweapon_bizonweapon_c4weapon_cz75aweapon_deagleweapon_decoyweapon_eliteweapon_famasweapon_fivesevenweapon_flashbangweapon_g3sg1weapon_galilweapon_galilarweapon_glockweapon_hegrenadeweapon_incgrenadeweapon_hkp2000weapon_knifeweapon_m249weapon_m3weapon_m4a1weapon_m4a1_silencerweapon_mac10weapon_mag7weapon_molotovweapon_mp5navyweapon_mp7weapon_mp9weapon_negevweapon_novaweapon_p228weapon_p250weapon_p90weapon_sawedoffweapon_scar17weapon_scar20weapon_scoutweapon_sg550weapon_sg552weapon_sg556weapon_ssg08weapon_smokegrenadeweapon_taserweapon_tec9weapon_tmpweapon_ump45weapon_uspweapon_usp_silencerweapon_xm1014weapon_revolver"

def load():
	for player in PlayerIter('all'):
		userid = player.userid
		restrictions[userid] = ""	

@ServerCommand('wcs_restrict')
def command_restrict(command):
	index = index_from_userid(int(command[1]))
	weapons = str(command[2])
	if len(command) > 3:
		reverse = int(command[3])
	else:
		reverse = 0
	restrict(index, weapons, reverse)

@ServerCommand('wcs_unrestrict')
def command_unrestrict(command):
	index = index_from_userid(int(command[1]))
	weapons = str(command[2])
	unrestrict(index, weapons)
	
@Event('player_activate')
def _player_activate(event):
	userid = event.get_int('userid')
	restrictions[userid] = ""

	   
@Event('player_death')
def _player_death(event):
	userid = event.get_int('userid')
	restrictions[userid] = ""
	
@EntityPreHook(EntityCondition.is_player, 'bump_weapon')
def on_bump_weapon(args):
	player = Player(index_from_pointer(args[0]))
	userid = player.userid
	weapon = Entity(index_from_pointer(args[1]))
	try:
		if weapon.classname not in restrictions[userid]:
			# Allow bumping
			return None
		# Disallow bumping
		return True
	except (KeyError):
		return
		
	
'''@EntityPreHook(EntityCondition.is_player, 'buy_internal')
def pre_buy(args):
	"""Called when a player is about to buy something."""
	# Get a PlayerEntity object from the pointer passed
	player = Player(index_from_pointer(args[0]))
	userid = player.userid
	if userid not in restrictions:
		restrictions[userid] = ""
	
	# Get the weapon name the player is about to buy
	core.console_message(str(args[1]))
	weapon = 'weapon_'+args[2]
	# Is the weapon restricted?
	if weapon in restrictions[userid]:
		# If yes, return False to block the purchase
		return False'''
	
def restrict(index, weapons, reverse=0):
	player = Player(index)
	userid = player.userid
	if userid not in restrictions:
		restrictions[userid] = ""
	if "," in weapons:
		buffer = weapons.split(",",53)
	else:
		buffer = weapons.split(";", 53)
	if weapons == "all":
		restrictions[userid] = restrict_all
		for index in player.weapon_indexes():
			weapon = Entity(index)
			player.drop_weapon(weapon.pointer, NULL_VECTOR, NULL_VECTOR)
	for x in buffer:
		if "weapon_" not in x:
			x = "weapon_"+x
		if reverse == 0:
			if x not in restrictions[userid]:
				restrictions[userid] = ''+restrictions[userid]+''+x
				for index in player.weapon_indexes():
					weapon = Entity(index)
					
					if weapon.classname == x:
						player.drop_weapon(weapon.pointer, NULL_VECTOR, NULL_VECTOR)
		else:
			weapon_restrict = restrict_all.replace(x, "")
			restrictions[userid] = weapon_restrict
			for index in player.weapon_indexes():
				weapon = Entity(index)
				if weapon.classname not in weapons:
					player.drop_weapon(weapon.pointer, NULL_VECTOR, NULL_VECTOR)				
	
def unrestrict(index, weapons):
	player = Player(index)
	userid = player.userid
	if userid not in restrictions:
		restrictions[userid] = ""
	buffer = weapons.split(";", 53)
	if weapons == 'all':
		restrictions[userid] = ""
	for x in buffer:
		if "weapon_" not in x:
			x = "weapon_"+x
		if x in restrictions[userid]:
			if x == "weapon_knife":
				player.give_named_item('weapon_knife', 0, None, True)
			restrictions[userid] = restrictions[userid].replace(x, "")

