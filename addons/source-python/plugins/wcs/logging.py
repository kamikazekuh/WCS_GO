from cvars import ConVar
from os.path import join, isdir
from os import mkdir
import os
from time import strftime
from commands.server import ServerCommand

def get_addon_path():
	path = os.path.dirname(os.path.abspath(__file__))
	return path

def log(text, level=0):
	if int(ConVar('wcs_logging').get_int()) >= level:
		path = join(get_addon_path(), 'logs')
		if not isdir(path):
			mkdir(path)

		path = join(path, strftime('%m%d.log'))

		file = open(path, 'a+')

		file.write(strftime('L %m/%d/%Y - %H:%M:%S: ')+str(text)+'\n')
		file.close()
		