from players.entity import Player
from players.helpers import index_from_userid, playerinfo_from_userid, index_from_playerinfo, userid_from_index
from menus import SimpleMenu
from menus import SimpleOption
from menus import PagedOption
from menus import Text
from messages import SayText2
from engines.server import queue_command_string,execute_server_command
import wcs
from commands.say import SayCommand
from commands.client import ClientCommand
from wcs.extensions import PagedMenu
import wcs.events
from events import Event
from listeners import OnLevelInit
from filters.players import PlayerIter
import random
import core
from cvars import ConVar



popups = []
items = {}
money = {}
maxitems = {}

for player in PlayerIter('all'):
	if player.userid not in items:
		items[player.userid] = {}



def canBuy(userid, item, pay=True):
	userid = int(userid)
	player = wcs.wcs.getPlayer(userid)
	level = player.race.level
	iteminfo = wcs.wcs.itemdb.getItem(item)
	player_entity = Player(index_from_userid(userid))
	if player_entity.dead:
		is_dead = 0
	else:
		is_dead = 1

	if is_dead == int(iteminfo['dab']) or int(iteminfo['dab']) == 2:
		section = wcs.wcs.itemdb.getSectionFromItem(item)
		if not userid in maxitems:
			maxitems[userid] = {}

		if not section in maxitems[userid]:
			maxitems[userid][section] = 0

		if maxitems[userid][section] and int(wcs.wcs.itemdb[section]['maxitems']) <= maxitems[userid][section]:
			return 4
			
		if int(iteminfo['level']) and level < int(iteminfo['level']):
			return 6

		v = wcs.wcs.getPlayer(userid).race.racedb['restrictitem'].split('|')
		if (item in v) or ('ITEMS' in v):
			return 3

		cfg = iteminfo['cfg']
		if cfg in items[userid]:
			if item in items[userid][cfg]:
				if int(iteminfo['max']) and items[userid][cfg][item] >= int(iteminfo['max']):
					return 1
			
		payment = player_entity.cash

		if payment >= int(iteminfo['cost']) or not pay:
			return 0
		return 2
	return 5
	
def shopmenu_menu_cats_build(menu, index):
	menu.clear()
	allitems = wcs.wcs.itemdb.getSections()
	for item in allitems:
		option = PagedOption('%s' % str(item), item)
		menu.append(option)

def shopmenu_menu_cats_select(menu, index, choice):
	userid = userid_from_index(index)
	doCommand1(userid, choice.value)		
		
shopmenu_menu_cats = PagedMenu(title='Shopmenu Menu', build_callback=shopmenu_menu_cats_build, select_callback=shopmenu_menu_cats_select)
		
def doCommand(userid):
	index = index_from_userid(userid)
	allitems = wcs.wcs.itemdb.getSections()
	if len(allitems):
		shopmenu_menu_cats.send(index)
		




item_names = []
	
def shopmenu_menu_subcats_build(menu, index):
	menu.clear()
	userid = userid_from_index(index)
	section = menu.title
	shopmenu_menu_subcats.previous_menu = shopmenu_menu_cats
	items_all = wcs.wcs.ini.getItems
	items_all.walk(gather_subsection)
	for item in item_names:
		item_sec = wcs.wcs.itemdb.getSectionFromItem(item)
		if item_sec == section:
			iteminfo = wcs.wcs.itemdb.getItem(item)
			option = PagedOption('%s - %s$' % (str(iteminfo['name']), str(iteminfo['cost'])), item)
			menu.append(option)
				
	
def gather_subsection(section, key):
	if section.depth > 1:
		if section.name not in item_names:
			item_names.append(section.name)
			
def shopmenu_menu_subcats_select(menu, index, choice):
	userid = userid_from_index(index)
	addItem(userid, choice.value)

shopmenu_menu_subcats = PagedMenu(build_callback=shopmenu_menu_subcats_build, select_callback=shopmenu_menu_subcats_select,display_page_info=True)

			
def doCommand1(userid, value):
	index = index_from_userid(userid)
	itemkeys = wcs.wcs.ini.getItems
	shopmenu_menu_subcats.title = value
	shopmenu_menu_subcats.send(index)

def addItem(userid, item, pay=True, tell=True):
	section = wcs.wcs.itemdb.getSectionFromItem(item)
	itemsa = wcs.wcs.ini.getItems
	userid = int(userid)
	player_entity = Player(index_from_userid(userid))
	if not userid in items:
		items[userid] = {}
	c = canBuy(userid, item, pay)

	if not c:
		if pay:
			player_entity.cash -= int(itemsa[section][item]['cost'])
		if tell:
			wcs.wcs.tell(userid, '\x04[WCS] \x04You have purchased: \x05%s' % itemsa[section][item]['name'])

		cfg = itemsa[section][item]['cfg']
		if not cfg in items[userid]:
			items[userid][cfg] = {}

		if not item in items[userid][cfg]:
			items[userid][cfg][item] = 0

		items[userid][cfg][item] += 1

		if not userid in maxitems:
			maxitems[userid] = {}

		if not section in maxitems[userid]:
			maxitems[userid][section] = 0

		maxitems[userid][section] += 1

		checkBuy(userid, item)
		event_instance = wcs.events.wcs_itembought(userid=userid, item=item, cost=int(wcs.wcs.itemdb.getItem(item)['cost']))
		event_instance.fire()	

	elif c == 1:
		doCommand1(userid, section)
		if tell:
			wcs.wcs.tell(userid, '\x04[WCS] \x05Item \x04%s \x05is out of stock.' % itemsa[section][item]['name'])
	elif c == 2:
		doCommand1(userid, section)
		if tell:
			payment = player_entity.cash
			wcs.wcs.tell(userid, '\x04[WCS] \x05You need \x04%s \05to buy \x04%s.' % (int(itemsa[section][item]['cost'])-payment, itemsa[section][item]['name']))
	elif c == 3:
		doCommand1(userid, section)
		if tell:
			wcs.wcs.tell(userid, "\x04[WCS] \x05You can't buy \x04%s\x05, it's restricted from your current race." % itemsa[section][item]['name'])
	elif c == 4:
		doCommand1(userid, section)
		if tell:
			wcs.wcs.tell(userid, "\x04[WCS] \x05You can't buy the item \x04%s\x05 because you've bought too many items in the section \x04%s" % (itemsa[section][item]['name'], section))
	elif c == 5:
		doCommand1(userid, section)
		if tell:
			wcs.wcs.tell(userid, "\x04[WCS] \x05You can't buy \x04%s\x05, you need to be \x04%s." % (itemsa[section][item]['name'], ['<death>','<alive>','<death or alive>'][int(itemsa[section][item]['dab'])]))
	elif c == 6:
		doCommand1(userid, section)
		iteminfo = wcs.wcs.itemdb.getItem(item)
		player = wcs.wcs.getPlayer(userid)
		diffience = int(iteminfo['level']) - int(player.race.level)
		if tell:
			wcs.wcs.tell(userid, "\x04[WCS] \x05Sorry, you have not the required level, difference is \x04%s." % diffience)
			

							
def checkEvent(userid, event):
	userid = int(userid)
	player = Player.from_userid(userid)
	if player.team > 1:
		if userid in items:
			if event in items[userid]:
				for item in items[userid][event]:
					v = items[userid][event][item]
					item, section = item, wcs.wcs.itemdb.getSectionFromItem(item)
					iteminfo = wcs.wcs.ini.getItems[section][item]

					ConVar('wcs_userid').set_int(userid)
					ConVar('wcs_dice').set_int(random.randint(0, 100))

					while v > 0:
						if (iteminfo['cfg'] == 'player_buy' or event == 'player_buy') and iteminfo['cmdbuy']:
							settings = str(iteminfo['cmdbuy'])
							if ';' in settings:
								sub_settings = settings.split(';')
								for com in sub_settings:
									execute_server_command('es', com)
							else:
								execute_server_command('es', settings)

						elif iteminfo['cmdactivate']:
							settings = str(iteminfo['cmdactivate'])
							if ';' in settings:
								core.console_message('testtesttest')
								sub_settings = settings.split(';')
								for com in sub_settings:
									execute_server_command('es', com)
							else:
								execute_server_command('es', settings)						

						v -= 1
							
							
def checkBuy(userid, item):
	userid = int(userid)
	iteminfo = wcs.wcs.ini.getItems[wcs.wcs.itemdb.getSectionFromItem(item)][item]
	player_entity = Player(index_from_userid(userid))
	if player_entity.dead:
		is_dead = 0
	else:
		is_dead = 1
	if is_dead == int(iteminfo['dab']) or int(iteminfo['dab']) == 2:
		ConVar('wcs_userid').set_int(userid)
		ConVar('wcs_dice').set_int(random.randint(0, 100))
		if iteminfo['cfg'] == 'player_buy' and iteminfo['cmdactivate']:
			settings = iteminfo['cmdactivate']
			if ';' in settings:
				sub_settings = settings.split(';')
				for com in sub_settings:
					execute_server_command('es', com)
			else:
				execute_server_command('es', settings)
		elif iteminfo['cmdbuy']:
			settings = iteminfo['cmdbuy']
			if ';' in settings:
				sub_settings = settings.split(';')
				for com in sub_settings:
					execute_server_command('es', com)
			else:
				execute_server_command('es', settings)
	

#Shopmenu Execution Stuff
@Event('player_death')					
def player_death(event):
	victim = event.get_int('userid')
	attacker = event.get_int('attacker')
	weapon = event.get_string('weapon')
	vic_entity = Player(index_from_userid(victim))

	if attacker and victim:
		atk_entity = Player(index_from_userid(attacker))
		if not victim == attacker:
			if not atk_entity.team == vic_entity.team:
				checkEvent(victim,  'player_death')
				checkEvent(attacker, 'player_kill')

	if victim and not attacker:
		checkEvent(victim,  'player_death')
		
	if victim:
		removeItems(victim,1)
		if victim in maxitems:
			maxitems[victim].clear()
		
def removeItems(userid, value):
	if userid in items:
		for x in items[userid]:
			for q in items[userid][x].copy():
				item = wcs.wcs.itemdb.getItem(q)
				if int(item['duration']) == value:
					items[userid][x][q] = 0	
		
@Event('player_hurt')
def player_hurt(event):
	victim = event.get_int('userid')
	attacker = event.get_int('attacker')
	weapon = event.get_string('weapon')
	
	if victim:  
		vic_entity = Player(index_from_userid(victim))
	if attacker:
		atk_entity = Player(index_from_userid(attacker))
	if attacker and victim and not weapon.lower() in ('point_hurt'):
		if not victim == attacker:
			if not atk_entity.team == vic_entity.team:
				checkEvent(victim, 'player_victim')
				checkEvent(attacker, 'player_attacker')
		checkEvent(victim, 'player_hurt')

@Event('player_spawn')
def player_spawn(event):
	userid = event.get_int('userid')
	if userid:
		checkEvent(userid, 'player_spawn')
		
@Event('round_end')
def round_end(event):
	for player in PlayerIter('all'):
		removeItems(player.userid,0)

@Event('player_say')
def player_say(event):
	text = event.get_string('text').lower()
	userid = event.get_int('userid')
	checkEvent(userid, 'player_say')


@Event('player_activate')
def player_activate(event):
	userid = event.get_int('userid')
	if not userid in items:
		items[userid] = {}
		
		
@Event('player_disconnect')
def player_disconnect(event):
	userid = event.get_int('userid')
	if userid in items:
		del items[userid]

	if userid in maxitems:
		del maxitems[userid]


@OnLevelInit
def level_init_listener(mapname):
	items.clear()
	maxitems.clear()



def load():
	for player in PlayerIter():
		items[int(player.userid)] = {}


def unload():
	items.clear()

					
					


					
					
