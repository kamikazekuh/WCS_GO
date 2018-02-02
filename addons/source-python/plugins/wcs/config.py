from config.manager import ConfigManager
from core import SOURCE_ENGINE_BRANCH
from paths import PLUGIN_DATA_PATH, GAME_PATH
import os

WCS_DATA_PATH = PLUGIN_DATA_PATH / 'wcs'
if not os.path.exists(WCS_DATA_PATH):
    os.makedirs(WCS_DATA_PATH)
LEVELBANK_DB_PATH = WCS_DATA_PATH / 'levelbank.db'
CORE_DB_PATH = WCS_DATA_PATH / 'players.db'
CORE_DB_REL_PATH = CORE_DB_PATH.relpath(GAME_PATH.parent)
LEVELBANK_DB_REL_PATH = LEVELBANK_DB_PATH.relpath(GAME_PATH.parent)

core_config = ConfigManager('wcs/wcs_core')

saving = core_config.cvar('wcs_save_mode', 0)

save_time = core_config.cvar('wcs_save_delay', 5)

xpsaver = core_config.cvar('wcs_cfg_savexponround', 5)

db_string = core_config.cvar('wcs_database_connectstring',f'sqlite:///{CORE_DB_REL_PATH}')

lvl_string = core_config.cvar('wcs_levelbank_connectstring',f'sqlite:///{LEVELBANK_DB_REL_PATH}')

racecategories = core_config.cvar('wcs_racecats', 0)

defaultcategory	= core_config.cvar('wcs_racecats_defaultcategory',	'Default category')

showracelevel = core_config.cvar('wcs_cfg_showracelevel', 1)

keyinfo = core_config.cvar('wcs_activate_keymenu', 0)

categories = core_config.cvar('wcs_activate_categories', 0)

unassigned_cat = core_config.cvar('wcs_unassigned_category', 1)

changerace_racename	= core_config.cvar('wcs_changerace_racename',1)

race_in_tag = core_config.cvar('wcs_activate_clantag_races', 1)

logging = core_config.cvar('wcs_logging',1)

core_config.write()
core_config.execute()

coredata = {'saving':				saving.get_int(),
		   'save_time':				save_time.get_int(),
		   'xpsaver':				xpsaver.get_int(),
		   'racecategories':		racecategories.get_int(),
		   'defaultcategory':		defaultcategory.get_string(),
		   'showracelevel':			showracelevel.get_int(),
		   'keyinfo':				keyinfo.get_int(),
		   'categories':			categories.get_int(),
		   'unassigned_cat':		unassigned_cat.get_int(),
		   'changerace_racename':	changerace_racename.get_int(),
		   'race_in_tag':			race_in_tag.get_int(),
		   'logging':				logging.get_int()}
		   


cmd_config = ConfigManager('wcs/wcs_commands')
showxp_cmd = cmd_config.cvar('showxp_commands','showxp')
wcsmenu_cmd = cmd_config.cvar('wcsmenu_commands','wcsmenu;wcs')
raceinfo_cmd = cmd_config.cvar('raceinfo_commands','raceinfo')
shopinfo_cmd = cmd_config.cvar('shopinfo_commands','shopinfo')
spendskills_cmd = cmd_config.cvar('spendskills_commands','spendskills')
changerace_cmd = cmd_config.cvar('changerace_commands','changerace')
resetskills_cmd = cmd_config.cvar('resetskills_commands','resetskills')
savexp_cmd = cmd_config.cvar('savexp_commands','savexp')
showskills_cmd = cmd_config.cvar('showskills_commands','showskills')
wcshelp_cmd = cmd_config.cvar('wcshelp_commands','wcshelp')
shopmenu_cmd = cmd_config.cvar('shopmenu_commands','shopmenu')
playerinfo_cmd = cmd_config.cvar('playerinfo_commands','playerinfo')
wcsbuyitem_cmd = cmd_config.cvar('wcsbuyitem_commands','wcsbuyitem;shopitem')
wcsrank_cmd = cmd_config.cvar('wcsrank_commands','wcsrank')
wcstop_cmd = cmd_config.cvar('wcstop_commands','wcstop')
ultimate_cmd = cmd_config.cvar('ultimate_commands','ultimate')
ability_cmd = cmd_config.cvar('ability_commands','ability')
cmd_config.write()
cmd_config.execute()

showxp_list = []
showxp_string = showxp_cmd.get_string().split(';')
for x in showxp_string:
	showxp_list.append(x)
	
wcsmenu_list = []
wcsmenu_string = wcsmenu_cmd.get_string().split(';')
for x in wcsmenu_string:
	wcsmenu_list.append(x)
	
raceinfo_list = []
raceinfo_string = raceinfo_cmd.get_string().split(';')
for x in raceinfo_string:
	raceinfo_list.append(x)
	
shopinfo_list = []
shopinfo_string = shopinfo_cmd.get_string().split(';')
for x in shopinfo_string:
	shopinfo_list.append(x)
	
spendskills_list = []
spendskills_string = spendskills_cmd.get_string().split(';')
for x in spendskills_string:
	spendskills_list.append(x)	
	
changerace_list = []
changerace_string = changerace_cmd.get_string().split(';')
for x in changerace_string:
	changerace_list.append(x)	
	
resetskills_list = []
resetskills_string = resetskills_cmd.get_string().split(';')
for x in resetskills_string:
	resetskills_list.append(x)


savexp_list = []
savexp_string = savexp_cmd.get_string().split(';')
for x in savexp_string:
	savexp_list.append(x)

showskills_list = []
showskills_string = showskills_cmd.get_string().split(';')
for x in showskills_string:
	showskills_list.append(x)

wcshelp_list = []
wcshelp_string = wcshelp_cmd.get_string().split(';')
for x in wcshelp_string:
	wcshelp_list.append(x)

shopmenu_list = []
shopmenu_string = shopmenu_cmd.get_string().split(';')
for x in shopmenu_string:
	shopmenu_list.append(x)

playerinfo_list = []
playerinfo_string = playerinfo_cmd.get_string().split(';')
for x in playerinfo_string:
	playerinfo_list.append(x)

wcsbuyitem_list = []
wcsbuyitem_string = wcsbuyitem_cmd.get_string().split(';')
for x in wcsbuyitem_string:
	wcsbuyitem_list.append(x)

wcsrank_list = []
wcsrank_string = wcsrank_cmd.get_string().split(';')
for x in wcsrank_string:
	wcsrank_list.append(x)
	
wcstop_list = []
wcstop_string = wcstop_cmd.get_string().split(';')
for x in wcstop_string:
	wcstop_list.append(x)
	
ultimate_list = []
ultimate_string = ultimate_cmd.get_string().split(';')
for x in ultimate_string:
	ultimate_list.append(x)
	
ability_list = []
ability_string = ability_cmd.get_string().split(';')
for x in ability_string:
	ability_list.append(x)
	
xp_config = ConfigManager('wcs/wcs_xp')
experience_system = xp_config.cvar('experience_system', 1) #done
standard_experience_system = xp_config.cvar('standard_experience_system', 5) #done
custom_experience_system = xp_config.cvar('custom_experience_system', "8,12,16,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100,108,116,124,132,140,150,160,170,180,190,200") #done
race_maximum_level = xp_config.cvar('race_maximum_level', 10000) #done
player_kill_exp  = xp_config.cvar('player_kill_exp', 20) #done
player_headshot_exp  = xp_config.cvar('player_headshot_exp', 5) #done
player_knife_exp = xp_config.cvar('player_knife_exp', 15) #done
player_grenade_he_exp = xp_config.cvar('player_grenade_he_exp',10)  #done
player_grenade_smoke_exp = xp_config.cvar('player_grenade_smoke_exp',25)  #done
player_grenade_flashbang_exp = xp_config.cvar('player_grenade_flashbang_exp', 25)  #done
if SOURCE_ENGINE_BRANCH == 'csgo':
	player_grenade_molotov_exp = xp_config.cvar('player_grenade_molotov_exp', 15)  #done
	bot_grenade_molotov_exp = xp_config.cvar('bot_grenade_molotov_exp', 10) #done
	player_assist_exp = xp_config.cvar('player_assist_exp',12)
	bot_assist_exp = xp_config.cvar('bot_assist_exp', 6)
player_level_difference_exp = xp_config.cvar('player_level_difference_exp', 2) #done
player_level_exp = xp_config.cvar('player_level_experience_limit', 0)
player_round_survival_exp = xp_config.cvar('player_round_survival_experience', 5) #done
player_round_win_exp = xp_config.cvar('player_round_win_experience',10) #done
player_plant_exp = xp_config.cvar('player_bomb_plant_experience', 10) #done
player_defuse_exp = xp_config.cvar('player_bomb_defuse_experience',10) #done
player_explode_exp = xp_config.cvar('player_bomb_explode_experience',10) #done
player_rescue_exp = xp_config.cvar('player_rescue_experience',10) #done
bot_kill_exp = xp_config.cvar('bot_kill_exp', 10) #done
bot_headshot_exp = xp_config.cvar('bot_headshot_exp', 3) #done
bot_knife_exp = xp_config.cvar('bot_knife_exp', 10) #done
bot_grenade_he_exp = xp_config.cvar('bot_grenade_he_exp', 5) #done
bot_grenade_smoke_exp = xp_config.cvar('bot_grenade_smoke_exp', 25) #done
bot_grenade_flashbang_exp = xp_config.cvar('bot_grenade_flashbang_exp', 25) #done
bot_level_difference_exp = xp_config.cvar('bot_level_difference_exp', 1) #done
bot_level_exp_limit = xp_config.cvar('bot_level_experience_limit', 0)
bot_round_survival_exp = xp_config.cvar('bot_round_survival_experience', 0) #done
bot_round_win_exp = xp_config.cvar('bot_round_win_experience', 0) #done
bot_plant_exp = xp_config.cvar('bot_plant_experience', 0) #done
bot_explode_exp = xp_config.cvar('bot_explode_experience', 0) #done
bot_defuse_exp = xp_config.cvar('bot_defuse_experience', 0) #done
bot_rescue_exp = xp_config.cvar('bot_rescue_experience',0) #done
xp_config.write()
xp_config.execute()

if SOURCE_ENGINE_BRANCH == 'csgo':
	cfgdata = {'interval':			standard_experience_system.get_int(),
		   'player_killxp':			player_kill_exp.get_int(),
		   'player_headshotxp':		player_headshot_exp.get_int(),
		   'player_knifexp':		player_knife_exp.get_int(),
		   'player_hexp':			player_grenade_he_exp.get_int(),
		   'player_smokexp':		player_grenade_smoke_exp.get_int(),
		   'player_flashxp':		player_grenade_flashbang_exp.get_int(),
		   'player_molotovxp':		player_grenade_molotov_exp.get_int(),
		   'player_assistxp':		player_assist_exp.get_int(),
		   'player_difxp':			player_level_difference_exp.get_int(),
		   'player_levellimit':		player_level_exp.get_int(),
		   'player_roundsxp':		player_round_survival_exp.get_int(),
		   'player_roundwxp':		player_round_win_exp.get_int(),
		   'player_plantxp':		player_plant_exp.get_int(),
		   'player_defusexp':		player_defuse_exp.get_int(),
		   'player_explodexp':		player_explode_exp.get_int(),
		   'player_rescuexp':		player_rescue_exp.get_int(),
		   'bot_killxp':			bot_kill_exp.get_int(),
		   'bot_headshotxp':		bot_headshot_exp.get_int(),
		   'bot_knifexp':			bot_knife_exp.get_int(),
		   'bot_hexp':				bot_grenade_he_exp.get_int(),
		   'bot_smokexp':			bot_grenade_smoke_exp.get_int(),
		   'bot_flashxp':			bot_grenade_flashbang_exp.get_int(),
		   'bot_moltovxp':			bot_grenade_molotov_exp.get_int(),
		   'bot_assistxp':			bot_assist_exp.get_int(),
		   'bot_difxp':				bot_level_difference_exp.get_int(),
		   'bot_levellimit':		bot_level_exp_limit.get_int(),
		   'bot_roundsxp':			bot_round_survival_exp.get_int(),
		   'bot_roundwxp':			bot_round_win_exp.get_int(),
		   'bot_plantxp':			bot_plant_exp.get_int(),
		   'bot_explodexp':			bot_explode_exp.get_int(),
		   'bot_defusexp':			bot_defuse_exp.get_int(),
		   'bot_rescuexp':			bot_rescue_exp.get_int(),
		   'maximum_level':			race_maximum_level.get_int(),
		   'custom_system':			custom_experience_system.get_string(),
		   'experience_system':		experience_system.get_int()}
else:
	cfgdata = {'interval':				standard_experience_system.get_int(),
		   'player_killxp':			player_kill_exp.get_int(),
		   'player_headshotxp':		player_headshot_exp.get_int(),
		   'player_knifexp':		player_knife_exp.get_int(),
		   'player_hexp':			player_grenade_he_exp.get_int(),
		   'player_smokexp':		player_grenade_smoke_exp.get_int(),
		   'player_flashxp':		player_grenade_flashbang_exp.get_int(),
		   'player_difxp':			player_level_difference_exp.get_int(),
		   'player_levellimit':		player_level_exp.get_int(),
		   'player_roundsxp':		player_round_survival_exp.get_int(),
		   'player_roundwxp':		player_round_win_exp.get_int(),
		   'player_plantxp':		player_plant_exp.get_int(),
		   'player_defusexp':		player_defuse_exp.get_int(),
		   'player_explodexp':		player_explode_exp.get_int(),
		   'player_rescuexp':		player_rescue_exp.get_int(),
		   'bot_killxp':			bot_kill_exp.get_int(),
		   'bot_headshotxp':		bot_headshot_exp.get_int(),
		   'bot_knifexp':			bot_knife_exp.get_int(),
		   'bot_hexp':				bot_grenade_he_exp.get_int(),
		   'bot_smokexp':			bot_grenade_smoke_exp.get_int(),
		   'bot_flashxp':			bot_grenade_flashbang_exp.get_int(),
		   'bot_difxp':				bot_level_difference_exp.get_int(),
		   'bot_levellimit':		bot_level_exp_limit.get_int(),
		   'bot_roundsxp':			bot_round_survival_exp.get_int(),
		   'bot_roundwxp':			bot_round_win_exp.get_int(),
		   'bot_plantxp':			bot_plant_exp.get_int(),
		   'bot_explodexp':			bot_explode_exp.get_int(),
		   'bot_defusexp':			bot_defuse_exp.get_int(),
		   'bot_rescuexp':			bot_rescue_exp.get_int(),
		   'maximum_level':			race_maximum_level.get_int(),
		   'custom_system':			custom_experience_system.get_string(),
		   'experience_system':		experience_system.get_int()}	
		   
