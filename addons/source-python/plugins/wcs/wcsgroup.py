from commands.server import ServerCommand
from players.helpers import index_from_userid, playerinfo_from_userid, index_from_playerinfo, userid_from_index
from cvars import ConVar

@ServerCommand('wcsgroup')
def wcsgroup_command(command):
    todo = str(command[1])
    if todo == 'get':
        key = str(command[2])
        var = str(command[3])
        userid = str(command[4])       
        if not existsUser(userid):
            addUser(userid)
        value = getUser(userid, key)
        var = ConVar(var)
        if value is None:
            var.set_string('0')
        else:
            var.set_string(str(value))
            
    elif todo == 'set':
        key = str(command[2])
        userid = str(command[3])
        value = str(command[4])       
        if not existsUser(userid):
            addUser(userid)
        setUser(userid, key, value)
            
keys = {}


def addUser(userid):
	userid = str(userid)
	if not userid in keys:
		keys[userid] = {}

def delUser(userid):
	userid = str(userid)
	if userid in keys:
		del keys[userid]

def existsUser(userid):
	userid = str(userid)
	return userid in keys

def setUser(userid, key, value):
	userid = str(userid)
	addUser(userid)
	keys[userid][key] = value

def getUser(userid, key):
	userid = str(userid)
	addUser(userid)
	if key in keys[userid]:
		value = str(keys[userid][key])
		if value.isdigit():
			return int(value)
		return value
	return None
