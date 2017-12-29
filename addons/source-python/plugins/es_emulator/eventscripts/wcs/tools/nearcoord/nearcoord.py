from es import server, getplayerlocation
from cmdlib import registerServerCommand, unregisterServerCommand
from playerlib import getUseridList

def load():
	registerServerCommand('wcs_nearcoord', register, '')

def unload():
	unregisterServerCommand('wcs_nearcoord')

def register(args):
	if len(args) == 7:
		var    = str(args[0])
		id     = str(args[1])
		x      = float(args[2])
		y      = float(args[3])
		z      = float(args[4])
		range  = float(args[5])
		cmd    = str(args[6])

		for user in getUseridList(id):
			x1,y1,z1 = getplayerlocation(user)
			if ((x1 - x) ** 2 + (y1 - y) ** 2 + (z1 - z) ** 2) ** 0.5 <= range:
				server.insertcmd('es_xset '+var+' '+str(user)+';'+cmd)
