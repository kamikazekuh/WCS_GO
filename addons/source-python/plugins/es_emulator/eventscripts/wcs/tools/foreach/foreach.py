from es import server, ServerVar
from cmdlib import registerServerCommand, unregisterServerCommand
from playerlib import getUseridList
from weaponlib import getWeaponList

def load():
	registerServerCommand('wcs_foreach', register, 'Syntax: wcs_foreach <player/weapon/token> <var> <identifier> <"command">')

def unload():
	unregisterServerCommand('wcs_foreach')

def register(args):
	if len(args) >= 1:
		target = str(args[0]).lower()

		if target == 'player':
			if len(args) >= 4:
				var = str(args[1])
				id  = str(args[2])
				cmd = ' '.join(args[3:])

				if id.startswith('#'):
					for user in getUseridList(id):
						server.insertcmd('es_xset '+var+' '+str(user)+';'+cmd)
				else:
					server.insertcmd('es_xset '+var+' '+id+';'+cmd)

		elif target == 'weapon':
			if len(args) >= 4:
				var = str(args[1])
				id  = str(args[2])
				cmd = ' '.join(args[3:])

				for weapon in getWeaponList(id):
					server.insertcmd('es_xset '+var+' '+str(weapon)+';'+cmd)

		elif target == 'token':
			if len(args) >= 5:
				var    = str(args[1])
				string = str(args[2])
				sep    = str(args[3])
				cmd    = ' '.join(args[3:])

				for token in string.split(sep):
					if len(token):
						server.insertcmd('es_xset '+var+' '+str(token)+';'+cmd)