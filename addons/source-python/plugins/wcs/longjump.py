from wcs import wcsgroup
from players.entity import Player
from events import Event
from players.helpers import index_from_userid
from mathlib import Vector

@Event('player_jump')
def player_jump(ev):
	userid = ev['userid']
	player = Player(index_from_userid(userid))
	value = wcsgroup.getUser(userid, 'longjump')
	if value is not None:
		value = float(value)
		if value > 1.0:
			vec = player.get_property_vector("m_vecVelocity")
			vec_new = Vector(vec[0]*value,vec[1]*value,vec[2])
			player.set_property_vector("m_vecBaseVelocity", vec_new)