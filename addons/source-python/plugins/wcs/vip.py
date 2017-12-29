from engines.server import engine_server
from events import Event
from players.helpers import index_from_userid, playerinfo_from_userid, index_from_playerinfo, userid_from_index, edict_from_userid
from players.entity import Player



steam_groups = "WCS;WCS2" #add steam group short name here like this: "WCS;ASDF;XYZ". Seperate different groups with a ;
message = "for beeing in our steamgroup!"
extra_xp = 15



@Event('wcs_gainxp')
def wcs_gainxp(event):
    reason = event.get_string('reason')
    if reason != message:
        userid = event.get_int('userid')
        player = Player(index_from_userid(userid))
        if player.clan_tag in steam_groups:
            #engine_server.server_command('wcs_givexp %s %s %s' % (userid, extra_xp, message))