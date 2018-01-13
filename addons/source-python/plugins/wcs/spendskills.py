from players.entity import Player
from players.helpers import index_from_userid, playerinfo_from_userid, index_from_playerinfo, userid_from_index
from menus import SimpleMenu
from menus import SimpleOption
from menus import Text
import wcs


def doCommand(userid):
	player = wcs.wcs.getPlayer(userid)
	unused = player.race.unused
	index = index_from_userid(userid)
	if unused:
		race = player.player.currace
		skills = player.race.skills.split('|')
		db = wcs.wcs.racedb.getRace(race)
		nol = int(db['numberoflevels'])
		filter_thingy = list(filter(lambda x: int(x) < nol, skills))
		if len(filter_thingy):
			spendskills = SimpleMenu()
			spendskills.append(Text('Available '+race+' skills:'))
			spendskills.append(Text('------------------------------'))
			
			skillnames = db['skillnames'].split('|')
			skillneeded = db['skillneeded'].split('|')
			
			added = 0
			for number, skill in enumerate(skills):
				added += 1
				if int(skill) >= nol:
					spendskills.append(SimpleOption(number+1, ''+str(skillnames[number])+' (maxed)', number+1, highlight=False))
				else:
					if int(skillneeded[number]) > player.race.level:
						spendskills.append(SimpleOption(number+1, ''+str(skillnames[number])+' (need level '+skillneeded[number]+')',  number+1, highlight=False))
					else:
						spendskills.append(SimpleOption(number+1, ''+str(skillnames[number])+': '+str(skills[number])+' > '+str(int(skills[number])+1), number+1, highlight=True))
			
			#while added < 8:
				#spendskills.append(Text(' '))
				#added += 1
			spendskills.append(Text('------------------------------'))
			spendskills.append(Text('Unused Points: '+str(player.race.unused)))
			spendskills.append(Text('------------------------------'))
			spendskills.append(SimpleOption(8, 'Back', highlight=True,selectable=True))
			spendskills.append(SimpleOption(9, 'Close', highlight=False))
			spendskills.send(index)
					
			spendskills.select_callback = popupHandler
		
		else:
			wcs.wcs.tell(userid, '\x04[WCS] \x05You have reached the \x04maximum level \x05for this race.')
	else:
		wcs.wcs.tell(userid, '\x04[WCS] \x05No unused points.')
			

def popupHandler(menu, index, choice):
	if choice.choice_index == 8:
		player=Player(index)
		player.client_command('wcs',server_side=True)		
	if choice.choice_index < 8:
		userid = userid_from_index(index)
		player = wcs.wcs.getPlayer(userid)
		race   = player.player.currace
		db     = wcs.wcs.racedb.getRace(race)
		nos    = int(db['numberofskills'])
		nol    = int(db['numberoflevels'])
		needed = db['skillneeded'].split('|')
		if nos >= choice.value:
			skills = player.race.skills.split('|')
			if int(skills[choice.value-1]) < nol and int(needed[choice.value-1]) <= player.race.level:
				level = player.race.addPoint(choice.value)
				if level != None:
					wcs.wcs.tell(userid, '\x04[WCS] \x05Your skill \x04%s \x05is now on level \x04%s.' % (db['skillnames'].split('|')[choice.value-1], level))

				if player.race.unused:
					doCommand(userid)

