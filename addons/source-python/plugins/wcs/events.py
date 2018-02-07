from events.custom import CustomEvent
from events.variable import FloatVariable
from events.variable import ShortVariable
from events.variable import StringVariable

from events.resource import ResourceFile
from path import Path
import os
import sys


	
# Create the event's class
class wcs_changerace(CustomEvent):
    # Declare the variables with their type
    userid = ShortVariable('The userid of the player involved in the event.')
    oldrace = StringVariable('The old race of the user.')
    newrace = StringVariable('The new race of the user.')

class wcs_gainxp(CustomEvent):
	userid = ShortVariable('The userid of the player involved in the event.')
	amount = ShortVariable('Amount of xp.')
	levels = ShortVariable('Amount of Levels.')
	currentxp = ShortVariable('Current XP.')
	reason = StringVariable('reason for xp gain.')

class wcs_levelup(CustomEvent):
	userid = ShortVariable('The userid of the player involved in the event.')
	race = StringVariable('Race on level up.')
	oldlevel = ShortVariable('oldlevel')
	newlevel = ShortVariable('newlevel')
	amount = ShortVariable('Amount of levels.')
	
class wcs_itembought(CustomEvent):
	userid = ShortVariable('The userid of the player involved in the event.')
	item = StringVariable('Item that was bought')
	cost = ShortVariable('Cost of the item')
	
class wcs_player_spawn(CustomEvent):
	userid = ShortVariable('The userid of the player involved in the event.')
	
def get_addon_path():
    path = os.path.dirname(os.path.abspath(__file__))
    return path
	
path = get_addon_path()
res_path = os.path.join(path, 'resources', 'events')
resource_file = ResourceFile(res_path, wcs_changerace, wcs_gainxp, wcs_levelup, wcs_itembought,wcs_player_spawn)
resource_file.write()
resource_file.load_events()