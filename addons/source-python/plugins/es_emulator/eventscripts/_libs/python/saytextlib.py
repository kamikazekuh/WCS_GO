# ..addons/eventscripts/_libs/python/saytextlib.py

import es
import playerlib
import usermsg

_gamename = es.getGameName()

_supported_games = ('ageofchivalry', 'cstrike', 'empires', 'gesource', 'hl1mp', 'hl2mp', 'Jailbreak', 'left4dead', 'left4dead2', 'pvkii', 'smashball', 'synergy', 'tf', 'zps')

_colors = ('#blue', '#grey', '#red', '#team')

class _SayTextHandler:
    def __init__(self):
        self.colors = {
            '#default':self._getDefaultColor(),
            '#lightgreen':self._getLightGreenColor(),
            '#green':self._getGreenColor()
                      }
        self.teamcolor = self._getTeamColor()
        self.extracolor = self._getExtraColor()
        self.player_filters = self._getPlayerFilters()
   
    def _sendMessage(self, users, index, message):
        if str(users)[0] in ('#', '!'):
            users = playerlib.getUseridList(users)
        elif not hasattr(users, '__iter__'):
            users = (users,)
        if _gamename in _supported_games:
            self._sendSayText(users, index, message)
        else:
            self._sendTellText(users, message)
   
    def _sendSayText(self, users, index, message):
        index, team = self._getIndexTeam(index, message)
        for color in self.colors:
            change_color = self.colors[color] if isinstance(self.colors[color], str) else self.colors[color](message)
            message = message.replace(color, change_color)
        team_color = self.teamcolor if isinstance(self.teamcolor, str) else self.teamcolor(team)
        for color in _colors:
            message = message.replace(color, team_color)
        usermsg.saytext2(users, index, message)
   
    def _getLightGreenColor(self):
        if _gamename in ('ageofchivalry', 'empires', 'Jailbreak', 'pvkii', 'smashball', 'synergy', 'zps'): return '\x05'
        if _gamename in ('left4dead', 'left4dead2'): return '\x01'
        if _gamename in ('hl2mp'): return '\x04'
        return self._checkLightGreenColor
   
    def _checkLightGreenColor(self, message):
        for color in _colors:
            if color in message: return self.extracolor
        return '\x03'
   
    def _getTeamColor(self):
        if _gamename in ('synergy'): return '\x05'
        if _gamename in ('cstrike', 'gesource', 'hl1mp', 'left4dead', 'left4dead2', 'tf'): return '\x03'
        return self._checkTeamColor
   
    def _checkTeamColor(self, team):
        if _gamename in ('ageofchivalry','empires', 'hl2mp', 'Jailbreak', 'smashball', 'zps') and team in (2, 3): return '\x03'
        if _gamename in ('pvkii') and team in (2, 3, 4): return '\x03'
        return self.extracolor
   
    def _getIndexTeam(self, index, message):
        if '#team' in message: return (index, es.getindexprop(index, 'CBaseEntity.m_iTeamNum'))
        for color in self.player_filters:
            if color in message:
                players = playerlib.getPlayerList(self.player_filters[color])
                if players: return (players[0].index, players[0].team)
        if '#grey' in message: return (-1, 1)
        return (0, 0)
   
    @staticmethod
    def _getDefaultColor():
        if _gamename in ('left4dead', 'left4dead2'): return '\x04'
        return '\x01'
   
    @staticmethod
    def _getGreenColor():
        if _gamename in ('gesource', 'left4dead', 'left4dead2'): return '\x05'
        return '\x04'
   
    @staticmethod
    def _getExtraColor():
        if _gamename in ('gesource', 'hl1mp', 'hl2mp', 'left4dead', 'left4dead2'): return '\x04'
        return '\x05'
   
    @staticmethod
    def _getPlayerFilters():
        if _gamename in ('left4dead', 'left4dead2'):
            return {'#red':'#ct', '#blue':'#t'}
        return {'#red':'#t', '#blue':'#ct'}
   
    @staticmethod
    def _sendTellText(users, message):
        for color in _colors:
            message = message.replace(color, '#lightgreen')
        for userid in users:
            es.tell(userid, '#multi', message)

_saytext = _SayTextHandler()

def sayText2(users, index=0, message=''):
    _saytext._sendMessage(users, index, message)