# -*- coding:Utf-8 -*-
import es
import cmdlib
 
esInfo = es.AddonInfo()
esInfo.author = "DoCky, edited by wcs community"
esInfo.version = "1.101pEdit"
esInfo.name = "PlayerViewLib"
esInfo.basename = "playerviewlib"
esInfo.url = ""
esInfo.description = "Allow you to know what entity a player is aiming"
 
version = es.ServerVar("playerviewlib", "", " Created by DoCky -")
version.set(esInfo.version)
version.makepublic()
 
 
# players dict
players = {}
 
def _command(args):
    # exec internal i_entity method
    players[args[0]].i_entity(args[1])
# register server command
cmdlib.registerServerCommand('_playerview_cmd', _command, 'playerview: internal command')
 
class PlayerView(object):
    """ PlayerView object """
    def __init__(self, userid):
        self.userid = str(userid)
        self.entities = {}
 
    def i_entities(self):
        # clear dict
        self.entities.clear()
        # for entities in map
        for index, attribute in es.createentityindexlist().items():
            # store "index" = "classname", "targetname"
            self.entities[index] = (attribute["classname"], es.entitygetvalue(index, "targetname"))
 
    def i_entity(self, target):
        # default index value
        entity = -1
        # targetname to find
        targetname = "_playerview_%s_%s" % (target, self.userid)
 
        # for index, info in entity list
        for index, info in self.entities.items():
            # check if targetname is corresponding
            if es.entitygetvalue(index, "targetname") == targetname:
                entity = index
                # restore last targetname
                es.entitysetvalue(index, "targetname", info[1])
                break
            # remove player from dict
        del players[self.userid]
 
        # if asked value is entity
        if target == "entity":
            # try to execute function with "userid" and "index" as arguments
            es.ServerVar('wcs_userid').set(self.userid)
            es.ServerVar('wcs_index').set(entity)
 
        # if asked value is player
        elif target == "player":
            # try to execute function with "userid" and "playerid" as arguments
            player = es.getuserid(es.gethandlefromindex(index))
            es.ServerVar('wcs_userid').set(self.userid)
            es.ServerVar('wcs_player').set(player)
 
 
    def i_command(self):
        if not es.exists("userid", self.userid): es.dbgmsg(0, "playerview: userid <%s> was not found" % self.userid)
        elif not players.has_key(self.userid):
            # refresh entity list
            self.i_entities()
            # add object in players dict
            players[self.userid] = self
 
    def entity(self):
        # check user, refresh entity list, add object in players dict
        self.i_command()
        # set entity targetname, exec internal server command
        es.server.insertcmd("es_xentsetname %s _playerview_entity_%s;_playerview_cmd %s entity" % (self.userid, self.userid, self.userid))
 
    def player(self):
        # check user, refresh entity list, add object in players dict
        self.i_command()
        # set entity targetname, exec internal server command
        es.server.insertcmd("es_xentsetname %s _playerview_player_%s;_playerview_cmd %s player" % (self.userid, self.userid, self.userid))
 
 
 
def entity(userid, callback):
    # playerviewlib.entity(<userid>, <callback>)
    PlayerView(userid, callback).entity()
 
def player(userid, callback):
    # playerviewlib.player(<userid>, <callback>)
    PlayerView(userid, callback).player()
 
def es_map_start(event_var):
    # clear players dict
    players.clear()
# registering es_map_start event
es.addons.registerForEvent(__import__(__name__), "es_map_start", es_map_start)