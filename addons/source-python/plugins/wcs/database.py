import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.expression import insert
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, desc
Base = declarative_base()
from configobj import ConfigObj

import core
from path import Path
import time
from cvars import ConVar

def get_addon_path():
	path = os.path.dirname(os.path.abspath(__file__))
	return path

standardrace = ConVar('wcs_default_race').get_string()
db_method = ConVar('wcs_database_connectstring').get_string()

engine = create_engine(db_method)


class Races(Base):
	__tablename__ = 'Races'
	RaceID = Column(Integer, nullable=False, primary_key=True)
	UserID = Column(Integer, nullable=False)
	name = Column(String(50),nullable=False)
	skills = Column(String(50),nullable=False)
	level = Column(Integer,default=0)
	xp = Column(Integer,default=0)
	unused = Column(Integer,default=0)
	Index('racesIndex',UserID)
 
class Players(Base):
	__tablename__ = 'Players'
	UserID = Column(Integer,nullable=False,primary_key=True)
	steamid = Column(String(30),nullable=False)
	currace = Column(String(30),nullable=False)
	name = Column(String(30),nullable=False)
	totallevel = Column(Integer,default=0)
	lastconnect = Column(Integer)
	Index('playersIndex', steamid)

if not engine.dialect.has_table(engine, 'Players'):
	Base.metadata.create_all(engine)

	
class SQLManager(object):
	def __init__(self):

		self.engine = engine
		self.DBSession = sessionmaker()
		self.DBSession.configure(bind=self.engine)
		self.session = self.DBSession()

	def __len__(self):
		return self.session.query(Players).count()
		
	def __contains__(self, user):
		if not isinstance(user, str): #Tha Pwned
			player = self.session.query(Players).filter(Players.UserID==user).all()
			if player.steamid:
				return 1
			else:
				return 0
		else:
			player = self.session.query(Players).filter(Players.steamid==user).all()
			if player.steamid:
				return 1
			else:
				return 0
				
			
	def getUserIdFromSteamId(self, steamid):
		try:
			player = self.session.query(Players).filter(Players.steamid==steamid).one()
		except:
			return None
		
		if player.UserID == None:
			return None

		return player.UserID
		
	def save(self):
		self.session.commit()
		
	def close(self):
		self.session.commit()
		self.session.close()
		
	def getRaceIdFromUserIdAndRace(self, userid, race):
		if isinstance(userid, str):
			userid = self.getUserIdFromSteamId(userid)
			
		try:
			race = self.session.query(Races).filter(Races.UserID==userid,Races.name==race).one()
		except:
			return None
		if race.RaceID is None:
			return None

		return race.RaceID

		
	def addRaceIntoPlayer(self, userid, name):
		if isinstance(userid, str): #Tha Pwned
			userid = self.getUserIdFromSteamId(userid)
			
		new_race_player = Races(UserID=userid,name=name,skills='')
		self.session.add(new_race_player)
		self.session.commit()
		return self.session.query(Races).filter(Races.UserID==userid,Races.name==name).one().RaceID
		
	def delRace(self,UserID,race):
		deleteRace = self.session.query(Races).filter(Races.UserID==UserID,Races.name==race).one()
		self.session.delete(deleteRace)
		self.session.commit()
		
	def delPlayer(self,UserID):
		deleteRace = self.session.query(Races).filter(Races.UserID==UserID).all()
		deletePlayer = self.session.query(Players).filter(Players.UserID==UserID).one()
		for x in deleteRace:
			self.session.delete(x)
		self.session.delete(deletePlayer)
		self.session.commit()
		
	def updateRank(self):
		all_players = self.session.query(Players).order_by(desc(Players.totallevel)).all()
		self.ranks = []
		for x in all_players:
			self.ranks.append(x.steamid)
		
	def getRank(self, steamid):
		self.updateRank()
		if steamid in self.ranks:
			return self.ranks.index(steamid) + 1
		return self.__len__()
		
	def getInfoRace(self,what,UserID,RaceID):
		all = self.session.query(Races).filter(Races.UserID==UserID,Races.RaceID==RaceID).one()
		if all != None:
			return (all.name,all.skills,all.level,all.xp,all.unused)
		else:
			return None
			
	def getInfoPlayer(self,what,UserID):
		all = self.session.query(Players).filter(Players.UserID==UserID).one()
		if all != None:
			return (all.steamid,all.currace,all.name,all.totallevel,all.lastconnect)
		else:
			return None
			
	def setInfoPlayer(self,options,UserID):
		user = self.session.query(Players).filter(Players.UserID==UserID).one()
		user.steamid = options[0]
		user.currace = options[1]
		user.name = options[2]
		user.totallevel = options[3]
		user.lastconnect = options[4]
		self.session.commit()
		
	def setInfoRace(self,options,UserID,RaceID):
		user = self.session.query(Races).filter(Races.UserID==UserID,Races.RaceID==RaceID).one()
		user.name = options[0]
		user.skills = options[1]
		user.level = options[2]
		user.xp = options[3]
		user.unused = options[4]
		self.session.commit()
		
		
	def addPlayer(self, steamid, name):
		new_player = Players(steamid=steamid,currace=standardrace,name=self.removeWarnings(name),lastconnect=time.time())
		self.session.add(new_player)
		self.session.commit()
		return self.session.query(Players).filter(Players.steamid==steamid).one().UserID

	def removeWarnings(self, value):
		return str(value).replace("'", "").replace('"', '')

database = SQLManager()