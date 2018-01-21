import es
import gamethread
import playerlib
import usermsg
import random
import vecmath
from wcs import wcs

def wcs_ulti_teleport():
	userid = int(es.ServerVar('wcs_userid'))

	if es.getplayerteam(userid) >= 2:
		if playerlib.getUseridList('#alive'):
			player = playerlib.getPlayer(userid)

			vector1 = vecmath.Vector(es.getplayerlocation(userid))
			vector2 = vecmath.Vector(player.getViewCoord())

			if vecmath.distance(vector1, vector2) <= float(es.ServerVar('wcs_range')):
				es.server.queuecmd("wcs_pushto %s %s 1.5" % (userid, vector2))
				es.tell(userid, '#multi', '#lightgreenYou Teleported!')
				es.playsound(userid, 'wcs/teleport.wav', 0.5)
			else:
				es.server.queuecmd("wcs_cancelulti %s" % (userid))
				es.tell(userid, '#multi', '#lightgreenSorry, you cannot teleport that far!')

def wcs_ulti_roots():
	userid = int(es.ServerVar('wcs_userid'))
	count = 0

	if es.getplayerteam(userid) >= 2:
		if playerlib.getUseridList('#alive'):
			usermsg.fade(userid, 0, 1, 1, 10, 55, 5, 200)
			x,y,z = es.getplayerlocation(userid)
			radius = float(es.ServerVar('wcs_radius'))
			time = float(es.ServerVar('wcs_duration'))

			for user in playerlib.getUseridList('#alive,#'+['ct','t'][es.getplayerteam(userid)-2]):
				x1,y1,z1 = es.getplayerlocation(user)

				if ((x1 - x) ** 2 + (y1 - y) ** 2 + (z1 - z) ** 2) ** 0.5 <= radius:

					if not wcs.wcsgroup.getUser(user, 'ulti_immunity'):
						playerlib.getPlayer(user).freeze = 1
						es.server.queuecmd('est_effect_06 #a 0 sprites/laser.vmt '+str(Vector(x,y,z+35))+' '+str(Vector(x1,y1,z1+35))+' 10 1 5 5 10 3.8 0 160 0 155 2')
						es.server.queuecmd('est_effect_06 #a 0 sprites/laser.vmt '+str(Vector(x,y,z+35))+' '+str(Vector(x1,y1,z1+35))+' 10 1 4 4 10 2.3 0 108 0 180 2')
						es.server.queuecmd('est_effect_06 #a 0 sprites/laser.vmt '+str(Vector(x,y,z+35))+' '+str(Vector(x1,y1,z1+35))+' 10 1 5 5 10 4.1 0 80 0 190 2')
						es.server.queuecmd('est_effect 10 #a 0 sprites/laser.vmt '+str(x)+' '+str(y)+' '+str(z+10)+' 60 20 1 3 3 5 0 80 0 155 0')
						es.server.queuecmd('est_effect 10 #a 0 sprites/laser.vmt '+str(x)+' '+str(y)+' '+str(z+25)+' 75 35 1 3 3 6 0 108 0 190 0')
						es.emitsound('player', user, 'wcs/root.wav', 1.0, 0.6)
						gamethread.delayed(time, reset, (user, 'freeze', 0))
						count += 1

					else:
						wcs.tell(user, 'u_ulti_immunity_v')
						wcs.tell(userid, 'u_ulti_immunity_a')

	if count:
		es.centertell(wcs.strings('c_u_entanglingroots', {'count':count}, playerlib.getPlayer(userid).lang))
	else:
		wcs.tell(userid, 'u_roots_failed')
		wcs.cancel(userid, 'player_ultimate')

def wcs_ulti_chain():
	userid = int(es.ServerVar('wcs_userid'))
	count = 0

	if es.getplayerteam(userid) >= 2:
		if playerlib.getUseridList('#alive'):
			usermsg.fade(userid, 0, 2, 1, 240, 240, 240, 100)
			x,y,z = es.getplayerlocation(userid)
			radius = float(es.ServerVar('wcs_radius'))

			for user in playerlib.getUseridList('#alive,#'+['ct','t'][es.getplayerteam(userid)-2]):
				x1,y1,z1 = es.getplayerlocation(user)

				if ((x1 - x) ** 2 + (y1 - y) ** 2 + (z1 - z) ** 2) ** 0.5 <= radius:

					if not wcs.wcsgroup.getUser(user, 'ulti_immunity'):
						es.server.queuecmd("wcs_dealdamage %s %s 32" % (user, userid))
						es.server.queuecmd('est_effect_06 #a 0 sprites/lgtning.vmt '+str(Vector(x,y,z+35))+' '+str(Vector(x1,y1,z1+35))+' 10 .2 10 1 1 13 160 160 230 255 11')
						es.server.queuecmd('est_effect_06 #a 0 sprites/lgtning.vmt '+str(Vector(x,y,z+35))+' '+str(Vector(x1,y1,z1+35))+' 10 .2 10 2 2 12 150 150 255 220 8')
						es.server.queuecmd('est_effect_06 #a 0 sprites/lgtning.vmt '+str(Vector(x,y,z+35))+' '+str(Vector(x1,y1,z1+35))+' 10 .2 10 1 1 14 200 200 255 235 10')
						es.emitsound('player', user, 'wcs/lightning.wav', 1.0, 0.6)
						count += 1

					else:
						wcs.tell(user, 'u_ulti_immunity_v')
						wcs.tell(userid, 'u_ulti_immunity_a')

	if count:
		es.centertell(wcs.strings('c_u_chainglightning', {'count':count}, playerlib.getPlayer(userid).lang))
	else:
		wcs.tell(userid, 'u_chain_failed')
		wcs.cancel(userid, 'player_ultimate')

def wcs_ulti_suicide():
	userid = int(es.ServerVar('wcs_userid'))

	if es.getplayerteam(userid) >= 2:
		if playerlib.getUseridList('#alive'):
			x,y,z = es.getplayerlocation(userid)
			radius = float(es.ServerVar('wcs_radius'))
			magnitude = float(es.ServerVar('wcs_magnitude'))
			v = round(radius * magnitude) / 150
			es.server.queuecmd('est_effect_20 #a 0 sprites/lgtning.vmt '+str(Vector(x,y,z+35))+' 1 10 5 200 10 '+str(x)+' '+str(y)+' '+str(z+10)+' metal')

			for user in playerlib.getUseridList('#alive,#'+['ct','t'][es.getplayerteam(userid)-2]):
				x1,y1,z1 = es.getplayerlocation(user)

				if ((x1 - x) ** 2 + (y1 - y) ** 2 + (z1 - z) ** 2) ** 0.5 <= radius:

					if not wcs.wcsgroup.getUser(user, 'ulti_immunity'):
						es.server.queuecmd("wcs_dealdamage %s %s %s" % (user, userid, v))
						es.emitsound('player', userid, 'ambient/explosions/explode_5.wav', 1.0, 0.6)

					else:
						wcs.tell(user, 'u_ulti_immunity_v')
						wcs.tell(userid, 'u_ulti_immunity_a')

def reset(userid, what, default):
	if es.exists('userid', userid):
		setattr(playerlib.getPlayer(userid), what, default)
