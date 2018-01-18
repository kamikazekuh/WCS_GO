from commands.client import ClientCommand
from players.entity import Player
from filters.players import PlayerIter
import wcs
from players.helpers import userid_from_index
import core
from commands import CommandReturn
from events import Event
race_counter = {}

race_counter['ct'] = {}
race_counter['t'] = {}


@ClientCommand('jointeam')
def join_test(command,index):
	if len(command) == 1:
		team_to_join = 5 - Player(index).team
	else:
		team_to_join = int(command[1])
	player = wcs.wcs.getPlayer(userid_from_index(index))
	player_race = player.player.currace
	raceinfo = wcs.wcs.racedb.getRace(player_race)
	restrictteam = raceinfo['restrictteam']
	if restrictteam != None:
		restrictteam = int(restrictteam)
	if restrictteam == team_to_join:
		if team_to_join == 2:
			tell_team = "Terrorists"
		if team_to_join == 3:
			tell_team == "Counter-Terrorists"
		wcs.wcs.tell(userid_from_index(index),"\x04[WCS] \x05This race is restricted to \x04%s!" % tell_team)
		return CommandReturn.BLOCK
	teamlimit = raceinfo['teamlimit']
	if teamlimit != None:
		teamlimit = int(teamlimit)
	if teamlimit > 0:
		if team_to_join == 2:
			team_name = 't'
			other_name = 'ct'
			tell_team = "Terrorists"
		if team_to_join == 3:
			team_name = 'ct'
			other_name = 't'
			tell_team = "Counter-Terrorists"
		if team_to_join == 4:
			return CommandReturn.CONTINUE
		for race in race_counter['ct']:
			race_counter['ct'][race] = 0
		for race in race_counter['t']:
			race_counter['t'][race] = 0
		for player_ent in PlayerIter(team_name):
			wcs_player = wcs.wcs.getPlayer(player_ent.userid)
			race = wcs_player.player.currace
			if race not in race_counter[team_name]:
				race_counter[team_name][race] = 0
				race_counter[team_name][race] += 1
			else:
				race_counter[team_name][race] += 1
		if teamlimit <= int(race_counter[team_name][player_race]):
			wcs.wcs.centertell(userid_from_index(index),"%s is taken, there can only be %s on %s" % (player_race,teamlimit,tell_team))
			return CommandReturn.BLOCK			
		