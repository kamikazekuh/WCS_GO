from players.entity import Player
from players.helpers import index_from_userid, playerinfo_from_userid, index_from_playerinfo, userid_from_index
from menus import SimpleMenu
from menus import SimpleOption
from menus import PagedOption
from menus import Text
import wcs
from menus import PagedMenu

#2
def shopinfo_menu_cats_build(menu, index):
	menu.clear()
	allitems = wcs.wcs.itemdb.getSections()
	for item in allitems:
		option = PagedOption('%s' % str(item), item)
		menu.append(option)
		
#3
def shopinfo_menu_cats_select(menu, index, choice):
	userid = userid_from_index(index)
	doCommand1(userid, choice.value)		
		
shopinfo_menu_cats = PagedMenu(title='Shopinfo Menu', build_callback=shopinfo_menu_cats_build, select_callback=shopinfo_menu_cats_select)

#1	
def doCommand(userid):
	index = index_from_userid(userid)
	allitems = wcs.wcs.itemdb.getSections()
	if len(allitems):
		shopinfo_menu_cats.send(index)		



item_names = []

#5
def shopinfo_menu_subcats_build(menu, index):
	menu.clear()
	userid = userid_from_index(index)
	section = menu.title
	shopinfo_menu_subcats.parent_menu = shopinfo_menu_cats
	items_all = wcs.wcs.ini.getItems
	items_all.walk(gather_subsection)
	for item in item_names:
		item_sec = wcs.wcs.itemdb.getSectionFromItem(item)
		if item_sec == section:
			iteminfo = wcs.wcs.itemdb.getItem(item)
			option = PagedOption('%s' % str(iteminfo['name']), item)
			menu.append(option)
				
	
def gather_subsection(section, key):
	if section.depth > 1:
		if section.name not in item_names:
			item_names.append(section.name)
#6			
def shopinfo_menu_subcats_select(menu, index, choice):
	userid = userid_from_index(index)
	item = choice.value
	iteminfo = wcs.wcs.itemdb.getItem(item)
	desc = iteminfo['desc']
	cost = int(iteminfo['cost'])
	required = int(iteminfo['level'])
	required_status = int(iteminfo['dab'])
	if required_status == 1:
		required_status = '<alive>'
	if required_status == 0:
		required_status = '<dead>'
	if required_status == 2:
		required_status = '<always>'
	duration = int(iteminfo['duration'])
	if duration == 1:
		duration = '<Until death>'
	if duration == 0:
		duration = '<One round>'
	maximum = int(iteminfo['max'])
	shopinfo_race_menu = PagedMenu(title='%s' % iteminfo['name'],parent_menu=menu)
	shopinfo_race_menu.append(Text('o %s' % desc))
	shopinfo_race_menu.append(Text('Required level: %s' % required))
	shopinfo_race_menu.append(Text('Cost: %s' % cost))
	shopinfo_race_menu.append(Text('Buyable when: %s' % required_status))
	shopinfo_race_menu.append(Text('Duration: %s' % duration))
	shopinfo_race_menu.send(index)

shopinfo_menu_subcats = PagedMenu(build_callback=shopinfo_menu_subcats_build, select_callback=shopinfo_menu_subcats_select)

#4			
def doCommand1(userid, value):
	index = index_from_userid(userid)
	itemkeys = wcs.wcs.ini.getItems
	shopinfo_menu_subcats.title = '%s' % value
	shopinfo_menu_subcats.send(index)