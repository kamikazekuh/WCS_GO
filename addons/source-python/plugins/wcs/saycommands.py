from commands.say import SayFilter
from players.entity import Player

command_list = ['wcsadmin', 'wcsbankadmin', 'wcsbank', 'wcsmenu', 'wcs', 'changerace', 'spendskills', 'shopmenu', 'wcstop', 'wcsrank', 'ultimate', 'ability', 'showxp', 'raceinfo', 'shopinfo', 'resetskills', 'savexp', 'showskills', 'wcshelp', 'playerinfo']

@SayFilter
def _say_command_hook(command, index, team=None):
	player = Player(index)
	if command[0] in command_list:
		player.client_command(command[0])
		return False