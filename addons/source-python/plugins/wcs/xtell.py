from es import exists, centertell
import es
from cmdlib import registerServerCommand, unregisterServerCommand
from playerlib import getUseridList, getPlayer
import langlib
from paths import PLUGIN_PATH
import os
import sys
from players.entity import Player

if os.path.isfile(os.path.join(PLUGIN_PATH, 'wcs/strings', 'strings.ini')):
	strings = langlib.Strings(os.path.join(PLUGIN_PATH, 'wcs/strings', 'strings.ini'))
	
	

def reg():
	unregisterServerCommand('wcs_xtell')
	unregisterServerCommand('wcs_xcentertell')
	registerServerCommand('wcs_xtell', register, 'Syntax: wcs_xtell <userid> <text> <[arg]> <[value]>...')
	registerServerCommand('wcs_xcentertell', register_center, 'Syntax: wcs_xcentertell <userid> <text> <[arg]> <[value]>...')


def register(args):
	if len(args) >= 2:
		userid   = str(args[0])
		text     = str(args[1])

		if userid.startswith('#'):
			userid = getUseridList(userid)
		else:
			userid = (userid, )

		hmm = []
		if len(args) >= 4:
			hmm = args[2:]

		tokens = {}
		for x in range(0, len(hmm), 2):
			try:
				tokens[hmm[x]] = hmm[x+1]
			except IndexError:
				return

		for user in userid:
			if exists('userid', user):
				tell(user, text, tokens)
				
def register_center(args):
	if len(args) >= 2:
		userid = str(args[0])
		text = str(args[1])

		if userid.startswith('#'):
			userid = getPlayerList(userid)

		if not hasattr(userid, '__iter__'):
			if not exists('userid', userid):
				return

			userid = (getPlayer(userid), )

		hmm = []
		if len(args) >= 4:
			hmm = args[2:]

		tokens = {}
		for x in range(0, len(hmm), 2):
			try:
				tokens[hmm[x]] = hmm[x+1]
			except IndexError:
				return

		for user in userid:
			if exists('userid', user):
				player = Player.from_userid(int(userid))
				if not player.is_bot():
					centertell(user, strings(text, tokens, langlib.getLangAbbreviation(player.language)))

				
				
def tell(userid, text, tokens={}, extra='', lng=True):
	if str(userid).startswith('#'):
		userid = playerlib.getPlayerList(userid)

	if not userid:
		return
	
	if not hasattr(userid, '__iter__'):
		if not es.exists('userid', userid):
			return

		userid = (userid, )

	for user in userid:
		player = Player.from_userid(int(userid))
		if not player.is_bot():
			if lng:
				try:
					text = strings(text, tokens, langlib.getLangAbbreviation(player.language))
				except:
					sys.excepthook(*sys.exc_info())
					return

			if not text:
				return

			if len(extra):
				if '#darkgreen' in text or '#darkgreen' in extra:
					es.tell(userid, '#multi', str(text%extra).replace('#darkgreen', '\x05'))
				else:
					es.tell(userid, '#multi', str(text%extra))
			else:
				if '%s' in text:
					text = text.replace('%s', '')

				if '#darkgreen' in text:
					es.tell(userid, '#multi', text.replace('#darkgreen', '\x05'))
				else:
					es.tell(userid, '#multi', text)
				
reg()