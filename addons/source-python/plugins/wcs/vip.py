from players.entity import Player
from configobj import ConfigObj
import os
from paths import PLUGIN_PATH
from events import Event
import wcs

vips = ConfigObj(os.path.join(PLUGIN_PATH, 'wcs/vip', 'vip.ini'))
	
@Event('wcs_gainxp')
def _gain_xp_vip(ev):
	player = Player.from_userid(ev['userid'])
	if ev['reason'] != "for beeing a VIP":
		if str(player.steamid) in vips:
			amount = int((ev['amount']) * (int(vips[player.steamid]['xp_gain'])/100))
			wcs.wcs.wcsplayers[player.userid].give_xp(amount,"for beeing a VIP")
		