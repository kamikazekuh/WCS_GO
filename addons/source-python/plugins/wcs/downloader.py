from stringtables.downloads import Downloadables
from paths import GAME_PATH
from os import listdir
from os.path import isfile, join, isdir
from engines.precache import Model

downloads = Downloadables()

paths_to_add = [GAME_PATH+'/materials/sprites', GAME_PATH+'/materials/particle', GAME_PATH+'/materials/effects']

for mypath in paths_to_add:
	if isdir(mypath):
		downloads.add_directory(mypath)
		for mypath in paths_to_add:
			if isdir(mypath):
				files = [f for f in listdir(mypath) if isfile(join(mypath, f))]
				for x in files:
					Model(x,True)
	



