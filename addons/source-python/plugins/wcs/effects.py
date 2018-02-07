from engines.precache import Model
from effects.base import TempEntity
from filters.recipients import RecipientFilter
from filters.players import PlayerIter
from commands.server import ServerCommand
from mathlib import Vector
from players.entity import Player
from colors import Color


@ServerCommand('est_effect_01')
def est_effect_01(command):
#est_Effect_01 <player Filter> <delay> <model> <position "X Y Z"> <direction "X Y
	if len(command) == 10:
		te = TempEntity('Armor Ricochet',direction=Vector(float(command[7]),float(command[8]),float(command[9])),position=Vector(float(command[4]),float(command[5]),float(command[6])))
		te.create(delay=float(command[2]))
	elif len(command) == 6:
		str_vec = command[4]
		str_vec = str_vec.split(",")
		vec = Vector(float(str_vec[0]),float(str_vec[1]),float(str_vec[2]))
		str_vec = command[5]
		str_vec = str_vec.split(",")
		vec2 = Vector(float(str_vec[0]),float(str_vec[1]),float(str_vec[2]))
		te = TempEntity('Armor Ricochet',direction=vec2,position=vec)
		te.create(delay=float(command[2]))

@ServerCommand('est_effect_02')
def est_effect_02(command):
	if len(command) == 19:
	#est_Effect_02 <player Filter> <delay> <model> <start ent> <start position "X Y Z"> <end ent> <end position "X Y Z"> <framerate> <life> <start width> <end width> <fade distance> <amplitude> <R> <G> <B> <A> <speed>
		str_vec = command[5]
		str_vec = str_vec.split(",")
		vec = Vector(float(str_vec[0]),float(str_vec[1]),float(str_vec[2]))
		str_vec = command[7]
		str_vec = str_vec.split(",")
		vec2 = Vector(float(str_vec[0]),float(str_vec[1]),float(str_vec[2]))
		te = TempEntity('BeamEntPoint', start_entity_index=int(command[4]), start_point=Vector(float(command[5])), end_entity_index=int(command[6]), end_point=vec2, model_index=Model(str(command[3])).index,halo_index=Model(str(command[3])).index,frame_rate=int(command[8]), life_time=float(command[9]), start_width=int(command[10]), end_width=int(command[11]), fade_length=int(command[12]), amplitude=int(command[13]), red=int(command[14]), green=int(command[15]), blue=int(command[16]),alpha=int(command[17]), speed=int(command[18]))
		te.create(delay=float(command[2]))
	
@ServerCommand('est_effect_03')
def est_effect_03(command):
	#est_Effect_03 <player Filter> <delay> <model> <start ent> <end ent> <framerate><life> <start width> <end width> <fade distance> <amplitude> <R> <G> <B> <A> <speed>
	if len(command) == 16:
		te = TempEntity('BeamEnts', model_index=Model(str(command[3])),halo_index=Model(str(command[3])),start_entity_index=int(command[4]),end_entity_index=int(command[5]),frame_rate=int(command[6]),start_width=int(command[7]),end_with=int(command[8]),fade_length=int(command[9]),amplitude=int(command[10]),red=int(command[11]),green=int(command[12]),blue=int(command[13]),alpha=int(command[14]),speed=int(command[15]))
		te.create(delay=float(command[2]))
	
@ServerCommand('est_effect_04')
def est_effect_04(command):
	#est_Effect_04 <player Filter> <delay> <model> <Follow ent> <life> <start width> <end width> <fade distance> <R> <G> <B> <A>
	te = TempEntity('BeamFollow')
	te.alpha = int(command[12])
	te.blue = int(command[11])
	te.green = int(command[10])
	te.end_width = int(command[7])
	te.life_time = float(command[5])
	te.start_width = int(command[6])
	te.entity_index = Player.from_userid(int(command[4])).index
	te.fade_length = int(command[8])
	te.halo_index = Model(str(command[3])).index
	te.model_index = Model(str(command[3])).index
	te.red = int(command[9])
	te.create(delay=float(command[2]))
	
@ServerCommand('est_effect_05')
def est_effect_05(command):
#est_Effect_05 - Beam Laser Effect est_Effect_05 <player Filter> <delay> <model> <start ent> <end ent> <framerate> <life> <start width> <end width> <fade distance> <amplitude> <R> <G> <B> <A> <speed>
	if len(command) == 17:
		te = TempEntity('BeamLaser', model_index=Model(str(command[3])).index,halo_index=Model(str(command[3])).index,start_entity_index=int(command[4]),end_entity_index=int(command[5]),frame_rate=int(command[6]),life_time=float(command[7]),start_width=int(command[8]),end_width=int(command[9]),fade_length=int(command[10]),amplitude=int(command[11]),red=int(command[12]),green=int(command[13]),blue=int(command[14]),alpha=int(command[15]),speed=int(command[16]))
		te.create(delay=float(command[2]))
	
@ServerCommand('est_effect_06')
def est_effect_06(command):
#est_Effect_06 - Beam Points Effect est_Effect_06 <player Filter> <delay> <model> <start position "X Y Z"> <end position "X Y Z"> <framerate> <life> <start width> <end width> <fade distance> <amplitude> <R> <G> <B> <A> <speed>
	if len(command) == 17:
		str_vec = command[4]
		str_vec = str_vec.split(",")
		vec = Vector(float(str_vec[0]),float(str_vec[1]),float(str_vec[2]))
		str_vec = command[5]
		str_vec = str_vec.split(",")
		vec2 = Vector(float(str_vec[0]),float(str_vec[1]),float(str_vec[2]))
		te = TempEntity('BeamPoints', model_index=Model(str(command[3])).index,halo_index=Model(str(command[3])).index,start_point=vec,end_point=vec2,frame_rate=int(command[6]),life_time=float(command[7]),start_width=float(command[8]),end_width=float(command[9]),fade_length=int(command[10]),amplitude=int(command[11]),red=int(command[12]),green=int(command[13]),blue=int(command[14]),alpha=int(command[15]),speed=int(command[16]))
		te.create(delay=float(command[2]))
	
@ServerCommand('est_effect_07')
def est_effect_07(command):
#est_Effect_07 <player Filter> <delay> <model> <start ent> <end ent> <framerate> <life> <width> <spread> <amplitude> <R> <G> <B> <A> <speed>
	if len(command) == 16:
		te = TempEntity('BeamRing', model_index=Model(str(command[3])).index,halo_index=Model(str(command[3])).index, start_entity_index = int(command[4]),end_entity_index=int(command[5]),frame_rate=int(command[6]),life_time=float(command[7]),start_width=int(command[8]),end_width=int(command[8]),amplitude=int(command[10]),red=int(command[11]),green=int(command[12]),blue=int(command[13]),alpha=int(command[14]),speed=int(command[15]))
		te.create(delay=float(command[2]))
	
@ServerCommand('est_effect_08')
def est_effect_08(command):
#est_Effect_08 - Beam Ring Ent Effect est_Effect_08 <player Filter> <delay> <model> <center "X Y Z"> <Start Radius> <End Radius> <framerate> <life> <width> <spread> <amplitude> <R> <G> <B> <A> <speed> <flags>
	if len(command) == 17:
		str_vec = command[4]
		str_vec = str_vec.split(",")
		vec = Vector(float(str_vec[0]),float(str_vec[1]),float(str_vec[2]))
		te = TempEntity('BeamRingPoint',model_index=Model(str(command[3])).index,halo_index=Model(str(command[3])).index, center=vec,start_radius=float(command[5]),end_radius=float(command[6]),frame_rate=int(command[7]),life_time=float(command[8]),start_width=int(command[9]),end_width=int(command[9]),amplitude=int(command[11]),red=int(command[12]),green=int(command[13]),blue=int(command[14]),alpha=int(command[15]),speed=int(command[16]))
		te.create(delay=float(command[2]))

	
@ServerCommand('est_effect_09')
def est_effect_09(command):
	#est_Effect_09 - Beam Spline Effect est_Effect_09 <player Filter> <delay> <model> <points> <rgPoints "X Y Z">
	if len(command) == 6:
		str_vec = command[5]
		str_vec = str_vec.split(",")
		vec = Vector(float(str_vec[0]),float(str_vec[1]),float(str_vec[2]))
		te = TempEntity('BeamSpline', points_length=int(command[4]),points=vec)
		te.create(delay=float(command[2]))
	
@ServerCommand('est_effect_10')
def est_effect_10(command):
	#est_Effect_10 <player Filter> <delay> <model> <origin "X Y Z"> <direction "X Y Z"> <R> <G> <B> <A> <Size>
	if len(command) == 11:
		str_vec = command[4]
		str_vec = str_vec.split(",")
		vec = Vector(float(str_vec[0]),float(str_vec[1]),float(str_vec[2]))
		str_vec = command[5]
		str_vec = str_vec.split(",")
		vec2 = Vector(float(str_vec[0]),float(str_vec[1]),float(str_vec[2]))
		te = TempEntity('Blood Sprite', drop_model_index=Model(str(command[3])).index,spray_model_index=Model(str(command[3])).index,origin=vec,direction=vec2,red=int(command[6]),green=int(command[7]),blue=int(command[8]),alpha=int(command[9]),size=float(command[10]))
		te.create(delay=float(command[2]))
	
@ServerCommand('est_effect_11')
def est_effect_11(command):
	#est_Effect_11 <player Filter> <delay> <model> <origin "X Y Z"> <direction "X Y Z"> <R> <G> <B> <A> <Amount>
	if len(command) == 11:
		str_vec = command[4]
		str_vec = str_vec.split(",")
		vec = Vector(float(str_vec[0]),float(str_vec[1]),float(str_vec[2]))
		str_vec = command[5]
		str_vec = str_vec.split(",")
		vec2 = Vector(float(str_vec[0]),float(str_vec[1]),float(str_vec[2]))
		te = TempEntity('Blood Stream', origin=vec,direction=vec2,red=int(command[6]),green=int(command[7]),blue=int(command[8]),alpha=int(command[9]),amount=int(comman[10]))
		te.create(delay=float(command[2]))
		
@ServerCommand('est_effect_12')
def est_effect_12(command):
	return 
	
@ServerCommand('est_effect_13')
def est_effect_13(command):
	return	
	
@ServerCommand('est_effect_14')
def est_effect_14(command):
	#est_Effect_14 - Bubbles Effectest_Effect_14 <player Filter> <delay> <model> <Min "X Y Z"> <Max "X Y Z"> <heigth> <count> <speed>
	if len(command) == 9:
		str_vec = command[4]
		str_vec = str_vec.split(",")
		vec = Vector(float(str_vec[0]),float(str_vec[1]),float(str_vec[2]))
		str_vec = command[5]
		str_vec = str_vec.split(",")
		vec2 = Vector(float(str_vec[0]),float(str_vec[1]),float(str_vec[2]))
		te = TempEntity('Bubbles', model_index = Model(str(command[3])).index,halo_index = Model(str(command[3])).index,mins=vec,maxs=vec2,height=int(command[6]),count=int(command[7]),speed=int(command[8]))
		te.create(delay=float(command[2]))
		
		
@ServerCommand('est_effect_15')
def est_effect_15(command):
	if len(command) == 9:
		#est_Effect_15 - Bubble Trail Effect est_Effect_15 <player Filter> <delay> <model> <Min "X Y Z"> <Max "X Y Z"> <heigth> <count> <speed>	
		te = TempEntity('Bubble Trail', model_index = Model(str(command[3])).index,halo_index = Model(str(command[3])).index,mins=vec,maxs=vec2,height=int(command[6]),count=int(command[7]),speed=int(command[8]))
		te.create(delay=float(command[2]))
	
	
@ServerCommand('est_effect_16')
def est_effect_16(command):
	return	
	
@ServerCommand('est_effect_17')
def est_effect_17(command):
	return	
	
@ServerCommand('est_effect_18')
def est_effect_18(command):
	if len(command) == 11:
		str_vec = command[3]
		str_vec = str_vec.split(",")
		vec = Vector(float(str_vec[0]),float(str_vec[1]),float(str_vec[2]))
		#est_Effect_18 - Dynamic Light Effect est_Effect_18 <player Filter> <delay> <Position "X Y Z"> <R> <G> <B> <exponent> <radius> <time> <decay>
		te = TempEntity('Dynamic Light', origin=vec,red=int(command[4]),green=int(command[5]),blue=int(command[6]),exponent=int(command[7]),radius=int(command[8]),life_time=float(command[9]),decay=float(command[10]))
		te.create(delay=float(command[2]))
		
@ServerCommand('est_effect_19')
def est_effect_19(command):
	return	
	
	
@ServerCommand('est_effect_20')
def est_effect_20(command):
	return	
	
@ServerCommand('est_effect_21')
def est_effect_21(command):
	return	
	
@ServerCommand('est_effect_22')
def est_effect_22(command):
	return	
	
@ServerCommand('est_effect_23')
def est_effect_23(command):
	return

@ServerCommand('est_effect_24')
def est_effect_24(command):
	if len(command) == 6:
		str_vec = command[4]
		str_vec = str_vec.split(",")
		vec = Vector(float(str_vec[0]),float(str_vec[1]),float(str_vec[2]))
		#est_Effect_24 - Large Funnel Effect est_Effect_24 <player Filter> <delay> <model> <Position "X Y Z"> <reversed>
		te = TempEntity('Large Funnel', model_index=Model(str(command[3])).index,origin=vec,reversed=int(command[5]))
		te.create(delay=float(command[2]))

@ServerCommand('est_effect_25')
def est_effect_25(command):
	return

@ServerCommand('est_effect_26')
def est_effect_26(command):
	return


@ServerCommand('est_effect_27')
def est_effect_27(command):
	return


@ServerCommand('est_effect_28')
def est_effect_28(command):
	return


@ServerCommand('est_effect_29')
def est_effect_29(command):
	return


@ServerCommand('est_effect_30')
def est_effect_30(command):
	return

@ServerCommand('est_effect_31')
def est_effect_31(command):
	return

@ServerCommand('est_effect_32')
def est_effect_32(command):
	return

@ServerCommand('est_effect_33')
def est_effect_33(command):
	return

@ServerCommand('est_effect_34')
def est_effect_34(command):
	return


@ServerCommand('est_effect_35')
def est_effect_35(command):
	return
	
	
@ServerCommand('est_effect')
def _est_effect(command):
	todo = str(command[1])
	filter = str(command[2])
	delay = float(command[3])
	if todo == "1":
		te = TempEntity('Armor Ricochet')
		te.position = Vector(float(command[4]),float(command[5]),float(command[6]))
		te.direction = Vector(float(command[7]),float(command[8]),float(command[9]))
		te.create()
	if todo == "2":
		te = TempEntity('BeamEntPoint')
		te.alpha = int(command[13])
		te.blue = int(command[12])
		te.green = int(command[11])
		te.end_width = float(command[9])
		te.life_time = float(command[7])
		te.start_width = float(command[8])
		te.end_entity_index = Player.from_userid(int(command[6])).index
		te.halo_index = Model(str(command[4])).index
		te.model_index = Model(str(command[4])).index
		te.start_entity_index = Player.from_userid(int(command[5])).index
		te.red = int(command[11])
		te.create()
	if todo == "3":
		te = TempEntity('BeamPoints')
		model = Model(str(command[4]))
		x1 = float(command[5])
		y1 = float(command[6])
		z1 = float(command[7])
		x2 = float(command[8])
		y2 = float(command[9])
		z2 =  float(command[10])
		life =  float(command[11])
		width = int(command[12])
		end_width = int(command[13])
		red = int(command[14])
		green = int(command[15])
		blue = int(command[16])
		alpha = int(command[17])
		te.alpha = alpha
		te.green = green
		te.blue = blue
		te.red = red
		te.end_width = end_width
		te.life_time = life
		te.start_width = width
		te.halo_index = model.index
		te.model_index = model.index
		te.end_point = Vector(x1,y1,z1)
		te.start_point = Vector(x2,y2,z2)
		te.create()
	if todo == "4":
		te = TempEntity('BeamFollow')
		te.alpha = int(command[13])
		te.blue = int(command[12])
		te.green = int(command[11])
		te.end_width = int(command[8])
		te.life_time = float(command[6])
		te.start_width = int(command[7])
		te.entity_index = Player.from_userid(int(command[5])).index
		te.fade_length = int(command[9])
		te.halo_index = Model(str(command[4])).index
		te.model_index = Model(str(command[4])).index
		te.red = int(command[10])
		te.create()
	if todo == "5":
		te = TempEntity('BeamRing')
		te.alpha = int(command[14])
		te.blue = int(command[13])
		te.green = int(command[12])
		te.amplitude = float(command[10])
		te.end_width = int(command[8])
		te.life_time = float(command[7])
		te.start_width = int(command[8])
		te.end_entity_index = int(command[6])
		te.halo_index = Model(str(command[4])).index
		te.model_index = Model(str(command[4])).index
		te.speed = int(command[15])
		te.start_entity_index = Player.from_userid(int(command[5])).index
		te.red = int(command[11])
	 #est_effect [BeamRing] <player Filter> <delay> <model> <userid> <end index> <life> <width> <spread> <amplitude> <Red> <Green> <Blue> <Alpha> <speed>
	if todo == "6":
		te = TempEntity('Large Funnel')
		te.model_index = Model(str(command[4])).index
		te.reversed = int(command[8])
		te.origin = Vector(float(command[5]),float(command[6]),float(command[7]))
		te.create()
		#est_effect [LargeFunnel] <player Filter> <delay> <model> <x> <y> <z> <reversed> 
	if todo == "7":
		te = TempEntity('Smoke')
		te.scale = float(command[8])
		te.frame_rate = int(command[9])
		te.model_index = Model(str(command[4])).index
		te.model = Model(str(command[4]))
		te.origin = Vector(float(command[5]),float(command[6]),float(command[7]))
		te.create()
	if todo == "8":
		te = TempEntity('Metal Sparks')
		te.direction = Vector(float(command[8]),float(command[9]),float(command[10]))
		te.position = Vector(float(command[5]),float(command[6]),float(command[7]))
		te.create()
		#est_effect [MetalSparks] <player Filter> <delay> <model> <x> <y> <z> (towards <x> <y> <z>) +
	if todo == "9":
		te = TempEntity('GaussExplosion')
		te.type = int(command[11])
		te.direction = Vector(float(command[8]),float(command[9]),float(command[10]))
		te.origin = Vector(float(command[5]),float(command[6]),float(command[7]))
		te.create()
		#est_effect [GaussExplosion] <player Filter> <delay> <model> <x> <y> <z> (towards <x> <y> <z>) <type>
	if todo == "10":
		te = TempEntity('BeamRingPoint')
		te.alpha = int(command[17])
		te.blue = int(command[16])
		te.green = int(command[15])
		te.amplitude = float(command[13])
		te.end_width = float(command[11])
		te.life_time = float(command[10])
		te.start_width = float(command[11])
		te.end_radius = float(command[9])
		te.start_radius = float(command[8])
		te.fade_length = int(command[12])
		te.halo_index = Model(str(command[4])).index
		te.model_index = Model(str(command[4])).index
		te.speed = int(command[18])
		te.center = Vector(float(command[5]),float(command[6]),float(command[7]))
		te.red = int(command[14])
		te.create()
	if todo == "11":
		te = TempEntity('GlowSprite')
		te.life_time = float(command[8])
		te.scale = float(command[9])
		te.brightness = int(command[10])
		te.model_index = Model(str(command[4])).index
		te.origin = Vector(float(command[5]),float(command[6]),float(command[7]))
		te.create()