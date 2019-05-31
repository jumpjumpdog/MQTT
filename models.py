#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json

import time

import uuid
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Table
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import scoped_session


Base = declarative_base()

class Admin(Base):
    # 定义表名
    __tablename__ = 'admin'
    # 定义列对象
    id = Column(Integer, primary_key=True)
    name = Column(String(64), unique=True)
    password = Column(String(64))

    def __repr__(self):
        return "<Admin {}>".format(self.name)

    def __init__(self, name, password):
        self.name = name
        self.password = password

    def to_json(self):
        dict = self.__dict__
        if "_sa_instance_state" in dict:
            del dict["_sa_instance_state"]
        return dict

from datetime import datetime, date, timedelta

from sqlalchemy.orm import sessionmaker

def getUuid():
    uuid_obj = uuid.uuid1()
    uuid_str = str(uuid_obj)
    return "".join(uuid_str.split("-"))

engine = create_engine("mysql+pymysql://root:123@localhost:3306/mqttdb", pool_size=100, pool_recycle=5, pool_timeout=30)
session_factory = sessionmaker(bind=engine)
session = scoped_session(session_factory)


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, DateTime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime("%Y-%m-%d")
        else:
            return json.JSONEncoder.default(self, obj)


Owner_Equipment = Table(
    'owner_equipment',
    Base.metadata,
    Column("owner_id",String(32),ForeignKey('owner.id',ondelete='CASCADE',onupdate='CASCADE'),nullable=False, primary_key=True),
    Column("equipment_id", String(32), ForeignKey('equipment.id',ondelete='CASCADE',onupdate='CASCADE'), nullable=False, primary_key=True)
)

class Owner(Base):
    # 定义表名
    __tablename__ = 'owner'
    # 定义列对象
    id = Column(String(32), primary_key=True)
    name = Column(String(64), unique=True)
    password = Column(String(64))
    telephone =Column(String(32))
    equipments = relationship('Equipment', secondary=Owner_Equipment)


    def __init__(self,name, password,_id, telephone):
        self.name = name
        self.password = password
        self.id = _id
        self.telephone = telephone

    def to_json(self):
        dict = self.__dict__
        if "_sa_instance_state" in dict:
            del dict["_sa_instance_state"]
        return dict

class Equipment(Base):
    # 定义表名
    __tablename__ = 'equipment'
    # 定义列对象
    id = Column(String(32), primary_key=True)
    name = Column(String(64), unique=True)
    status = Column(String(64))
    max_t = Column(Float)
    min_t = Column(Float)
    create_date = Column(DateTime)
    url = Column(String(128))


    t_history = relationship('THistory', backref='equipment', lazy='dynamic')
    h_history = relationship('HHistory', backref='equipment', lazy='dynamic')
    owners = relationship("Owner",secondary=Owner_Equipment)

    def __init__(self, _id, name, max_t, min_t,create_date,url, status='success'):
        self.id = _id
        self.name = name
        self.status = status
        self.max_t = max_t
        self.min_t = min_t
        self.url = url
        if create_date is None:
            create_date = datetime.utcnow()
        self.create_date = create_date

    def to_json(self):
        dict = self.__dict__
        mydict = {}
        for key in dict.keys():
            if key == "_sa_instance_state" or key == "create_date"  or key == 'owners' :
                continue
            mydict[key] = dict[key]
        # if "_sa_instance_state" in dict:
        #     del dict["_sa_instance_state"]
        mydict["create_date"] = json.dumps(self.create_date,cls=DateEncoder)
        return mydict

class THistory(Base):
    # 定义表名
    __tablename__ = 't_history'
    # 定义列对象
    id = Column(Integer, primary_key=True)
    create_date = Column(String(32))
    max_t = Column(Float)
    min_t = Column(Float)

    equipment_id = Column(String(32),ForeignKey('equipment.id'))

    def __init__(self,create_date, max_t, min_t, equipment_id):
        if create_date is None:
            create_date = ""
        self.create_date = create_date
        self.equipment_id = equipment_id
        self.max_t = max_t
        self.min_t = min_t
    def to_json(self):
        dict = self.__dict__
        return dict


class EquipmentException(Base):
    # 定义表名
    __tablename__ = 'equipment_exception'
    id = Column(Integer,primary_key=True)
    reason = Column(String(32))
    owner_id = Column(String(32))
    eqp_id = Column(String(32))
    status = Column(String(32))
    create_date =  Column(String(32))
    fix_date = Column(String(32))
    admin_id = Column(String(32))
    t = Column(String(32))
    def __init__(self,eqp_id,reason,create_date,t ,status=None):
        self.eqp_id = eqp_id
        if status == None:
            status ='待分配'
        self.status = status
        self.reason = reason
        self.create_date = create_date
        self.t = t

    def to_json(self):
        dict = self.__dict__
        if "_sa_instance_state" in dict:
            del dict["_sa_instance_state"]
        return dict

class HHistory(Base):
    # 定义表名
    __tablename__ = 'h_history'
    # 定义列对象
    id = Column(Integer, primary_key=True)
    create_date = Column(DateTime)
    humid = Column(Integer)

    equipment_id = Column(String(32), ForeignKey('equipment.id'))

    def __init__(self,create_date, humid, equipment_id):
        if create_date is None:
            create_date = ""
        self.create_date = create_date
        self.equipment_id = equipment_id
        self.humid = humid
    def to_json(self):
        dict = self.__dict__
        if "_sa_instance_state" in dict:
            del dict["_sa_instance_state"]
        return dict
# Base.metadata.drop_all(engine)
# Base.metadata.create_all(engine)


# owner_wjl = Owner(name='王建林',password='123')
# owner_sjw = Owner(name='沈金伟',password='123')
# equipemnt1 = Equipment()

#创建mysql操作对象
# Session = sessionmaker(bind=engine)
# session = Session()
#
# xinan1id = getUuid()
# eqp = Equipment( _id=xinan1id,name='西南十洗衣房', max_t=30, min_t=-10,create_date=None, status='正常')
# session.add(eqp)
t_data = [[1388538000000, 1.1, 4.7],
[1388624400000, 1.8, 6.4],
[1388710800000, 1.7, 6.9],
[1388797200000, 2.6, 7.4],
[1388883600000, 3.3, 9.3],
[1388970000000, 3.0, 7.9],
[1389056400000, 3.9, 6.0],
[1389142800000, 3.9, 5.5],
[1389229200000, -0.6, 4.5],
[1389315600000, -0.5, 5.3],
[1389402000000, -0.3, 2.4],
[1389488400000, -6.5, -0.4],
[1389574800000, -7.3, -3.4],
[1389661200000, -7.3, -2.3],
[1389747600000, -7.9, -4.2],
[1389834000000, -4.7, 0.9],
[1389920400000, -1.2, 0.4],
[1390006800000, -2.3, -0.1],
[1390093200000, -2.0, 0.3],
[1390179600000, -5.1, -2.0],
[1390266000000, -4.4, -0.5],
[1390352400000, -6.4, -2.7],
[1390438800000, -3.2, -0.5],
[1390525200000, -5.5, -0.8],
[1390611600000, -4.4, 2.4],
[1390698000000, -4.0, 1.1],
[1390784400000, -3.4, 0.8],
[1390870800000, -1.7, 2.6],
[1390957200000, -3.1, 3.9],
[1391043600000, -4.8, -1.9],
[1391130000000, -7.0, -2.8],
[1391216400000, -2.7, 2.6],
[1391302800000, -1.3, 8.2],
[1391389200000, 1.5, 7.7],
[1391475600000, -0.5, 5.3],
[1391562000000, -0.2, 5.2],
[1391648400000, 0.7, 4.8],
[1391734800000, 0.9, 5.7],
[1391821200000, 1.7, 3.9],
[1391907600000, 2.2, 8.8],
[1391994000000, 3.0, 6.6],
[1392080400000, 1.4, 5.4],
[1392166800000, 0.6, 5.1],
[1392253200000, 0.1, 7.8],
[1392339600000, 3.4, 7.3],
[1392426000000, 2.0, 5.9],
[1392512400000, 1.1, 4.7],
[1392598800000, 1.1, 4.4],
[1392685200000, -2.8, 2.6],
[1392771600000, -5.0, 0.1],
[1392858000000, -5.7, 0.2],
[1392944400000, -0.7, 3.9],
[1393030800000, 1.5, 7.8],
[1393117200000, 5.5, 8.8],
[1393203600000, 5.3, 11.7],
[1393290000000, 1.7, 11.1],
[1393376400000, 3.4, 9.3],
[1393462800000, 3.4, 7.3],
[1393549200000, 4.5, 8.0],
[1393635600000, 2.1, 8.9],
[1393722000000, 0.6, 6.1],
[1393808400000, 1.2, 9.4],
[1393894800000, 2.6, 7.3],
[1393981200000, 3.9, 9.5],
[1394067600000, 5.3, 9.9],
[1394154000000, 2.7, 7.1],
[1394240400000, 4.0, 8.6],
[1394326800000, 6.1, 10.7],
[1394413200000, 4.2, 7.6],
[1394499600000, 2.5, 9.0],
[1394586000000, 0.2, 7.0],
[1394672400000, -1.2, 6.9],
[1394758800000, 0.4, 6.7],
[1394845200000, 0.2, 5.1],
[1394931600000, -0.1, 6.0],
[1395018000000, 1.0, 5.6],
[1395104400000, -1.1, 6.3],
[1395190800000, -1.9, 0.3],
[1395277200000, 0.3, 4.5],
[1395363600000, 2.4, 6.7],
[1395450000000, 3.2, 9.2],
[1395536400000, 1.7, 3.6],
[1395622800000, -0.3, 7.9],
[1395709200000, -2.4, 8.6],
[1395795600000, -1.7, 10.3],
[1395882000000, 4.1, 10.0],
[1395968400000, 4.4, 14.0],
[1396054800000, 3.3, 11.0],
[1396141200000, 3.0, 12.5],
[1396224000000, 1.4, 10.4],
[1396310400000, -1.2, 8.8],
[1396396800000, 2.2, 7.6],
[1396483200000, -1.0, 10.1],
[1396569600000, -1.8, 9.5],
[1396656000000, 0.2, 7.7],
[1396742400000, 3.7, 6.4],
[1396828800000, 5.8, 11.4],
[1396915200000, 5.4, 8.7],
[1397001600000, 4.5, 12.2],
[1397088000000, 3.9, 8.4],
[1397174400000, 4.5, 8.0],
[1397260800000, 6.6, 8.4],
[1397347200000, 3.7, 7.3],
[1397433600000, 3.6, 6.7],
[1397520000000, 3.5, 8.3],
[1397606400000, 1.5, 10.2],
[1397692800000, 4.9, 9.4],
[1397779200000, 3.5, 12.0],
[1397865600000, 1.5, 13.1],
[1397952000000, 1.7, 15.6],
[1398038400000, 1.4, 16.0],
[1398124800000, 3.0, 18.4],
[1398211200000, 5.6, 18.8],
[1398297600000, 5.7, 17.2],
[1398384000000, 4.5, 16.4],
[1398470400000, 3.1, 17.6],
[1398556800000, 4.7, 18.9],
[1398643200000, 4.9, 16.6],
[1398729600000, 6.8, 15.6],
[1398816000000, 2.8, 9.2],
[1398902400000, -2.7, 10.5],
[1398988800000, -1.9, 10.9],
[1399075200000, 4.5, 8.5],
[1399161600000, -0.6, 10.4],
[1399248000000, 4.0, 9.7],
[1399334400000, 5.5, 9.5],
[1399420800000, 6.5, 13.2],
[1399507200000, 3.2, 14.5],
[1399593600000, 2.1, 13.5],
[1399680000000, 6.5, 15.6],
[1399766400000, 5.7, 16.2],
[1399852800000, 6.3, 15.3],
[1399939200000, 5.3, 15.3],
[1400025600000, 6.0, 14.1],
[1400112000000, 1.9, 7.7],
[1400198400000, 7.2, 9.8],
[1400284800000, 8.9, 15.2],
[1400371200000, 9.1, 20.5],
[1400457600000, 8.4, 17.9],
[1400544000000, 6.8, 21.5],
[1400630400000, 7.6, 14.1],
[1400716800000, 11.1, 16.5],
[1400803200000, 9.3, 14.3],
[1400889600000, 10.4, 19.3],
[1400976000000, 5.7, 19.4],
[1401062400000, 7.9, 17.9],
[1401148800000, 5.0, 22.5],
[1401235200000, 7.6, 22.0],
[1401321600000, 5.7, 21.9],
[1401408000000, 4.6, 20.0],
[1401494400000, 7.0, 22.0],
[1401580800000, 5.1, 20.6],
[1401667200000, 6.6, 24.6],
[1401753600000, 9.7, 22.2],
[1401840000000, 9.6, 21.6],
[1401926400000, 13.0, 20.0],
[1402012800000, 12.9, 18.2],
[1402099200000, 8.5, 23.2],
[1402185600000, 9.2, 21.4],
[1402272000000, 10.5, 22.0],
[1402358400000, 7.3, 23.4],
[1402444800000, 12.1, 18.2],
[1402531200000, 11.1, 13.3],
[1402617600000, 10.0, 20.7],
[1402704000000, 5.8, 23.4],
[1402790400000, 7.4, 20.1],
[1402876800000, 10.3, 21.9],
[1402963200000, 7.8, 16.8],
[1403049600000, 11.6, 19.7],
[1403136000000, 9.8, 16.0],
[1403222400000, 10.7, 14.4],
[1403308800000, 9.0, 15.5],
[1403395200000, 5.1, 13.3],
[1403481600000, 10.0, 19.3],
[1403568000000, 5.2, 22.1],
[1403654400000, 6.3, 21.3],
[1403740800000, 5.5, 21.1],
[1403827200000, 8.4, 19.7],
[1403913600000, 7.1, 23.3],
[1404000000000, 6.1, 20.8],
[1404086400000, 8.4, 22.6],
[1404172800000, 7.6, 23.3],
[1404259200000, 8.1, 21.5],
[1404345600000, 11.2, 18.1],
[1404432000000, 6.4, 14.9],
[1404518400000, 12.7, 23.1],
[1404604800000, 15.3, 21.7],
[1404691200000, 15.1, 19.4],
[1404777600000, 10.8, 22.8],
[1404864000000, 15.8, 29.7],
[1404950400000, 15.8, 29.0],
[1405036800000, 15.2, 30.5],
[1405123200000, 14.9, 28.1],
[1405209600000, 13.1, 27.4],
[1405296000000, 15.5, 23.5],
[1405382400000, 14.7, 20.1],
[1405468800000, 14.4, 16.8],
[1405555200000, 12.6, 18.5],
[1405641600000, 13.9, 24.4],
[1405728000000, 11.3, 26.9],
[1405814400000, 13.3, 27.4],
[1405900800000, 13.3, 29.7],
[1405987200000, 14.0, 28.8],
[1406073600000, 14.1, 29.8],
[1406160000000, 15.4, 31.1],
[1406246400000, 17.0, 26.5],
[1406332800000, 16.6, 27.1],
[1406419200000, 13.3, 25.6],
[1406505600000, 16.8, 21.9],
[1406592000000, 16.0, 22.8],
[1406678400000, 14.4, 19.0],
[1406764800000, 12.8, 18.1],
[1406851200000, 12.6, 18.0],
[1406937600000, 11.4, 19.7],
[1407024000000, 13.9, 18.9],
[1407110400000, 12.5, 19.9],
[1407196800000, 12.3, 23.4],
[1407283200000, 12.8, 23.3],
[1407369600000, 11.0, 20.4],
[1407456000000, 14.7, 22.4],
[1407542400000, 11.1, 23.6],
[1407628800000, 13.5, 20.7],
[1407715200000, 13.7, 23.1],
[1407801600000, 12.8, 19.6],
[1407888000000, 12.1, 18.7],
[1407974400000, 8.8, 22.4],
[1408060800000, 8.2, 20.1],
[1408147200000, 10.9, 16.3],
[1408233600000, 10.7, 16.1],
[1408320000000, 11.0, 18.9],
[1408406400000, 12.1, 14.7],
[1408492800000, 11.2, 14.4],
[1408579200000, 9.9, 16.6],
[1408665600000, 6.9, 15.7],
[1408752000000, 8.9, 15.3],
[1408838400000, 8.2, 17.6],
[1408924800000, 8.4, 19.5],
[1409011200000, 6.6, 19.9],
[1409097600000, 6.4, 19.7],
[1409184000000, 0, 0],
[1409270400000, 0, 0],
[1409356800000, 0, 0],
[1409443200000, 0, 0],
[1409529600000, 0, 0],
[1409616000000, 0, 0],
[1409702400000, 0, 0],
[1409788800000, 0, 0],
[1409875200000, 0, 0],
[1409961600000, 13.4, 13.4],
[1410048000000, 13.2, 17.1],
[1410134400000, 11.9, 18.9],
[1410220800000, 9.0, 15.9],
[1410307200000, 5.9, 17.5],
[1410393600000, 6.8, 16.2],
[1410480000000, 10.3, 19.9],
[1410566400000, 8.7, 17.9],
[1410652800000, 7.9, 19.1],
[1410739200000, 6.0, 20.1],
[1410825600000, 4.7, 19.9],
[1410912000000, 4.0, 18.8],
[1410998400000, 4.5, 17.9],
[1411084800000, 3.1, 16.1],
[1411171200000, 8.5, 12.2],
[1411257600000, 7.6, 13.8],
[1411344000000, 1.3, 12.6],
[1411430400000, 2.0, 10.9],
[1411516800000, 5.0, 10.8],
[1411603200000, 6.4, 10.1],
[1411689600000, 8.2, 13.3],
[1411776000000, 8.9, 11.8],
[1411862400000, 9.9, 15.9],
[1411948800000, 5.2, 12.5],
[1412035200000, 4.6, 11.7],
[1412121600000, 8.8, 12.1],
[1412208000000, 3.9, 12.3],
[1412294400000, 2.7, 18.1],
[1412380800000, 10.2, 18.2],
[1412467200000, 9.6, 17.9],
[1412553600000, 9.3, 17.5],
[1412640000000, 8.1, 12.7],
[1412726400000, 6.7, 11.2],
[1412812800000, 4.0, 10.0],
[1412899200000, 6.3, 10.2],
[1412985600000, 6.6, 10.7],
[1413072000000, 6.6, 10.3],
[1413158400000, 5.9, 10.4],
[1413244800000, 1.2, 10.6],
[1413331200000, -0.1, 9.2],
[1413417600000, -1.0, 9.4],
[1413504000000, -1.7, 8.3],
[1413590400000, -0.6, 7.5],
[1413676800000, 6.9, 10.1],
[1413763200000, 7.7, 10.5],
[1413849600000, 3.8, 9.7],
[1413936000000, 6.2, 8.6],
[1414022400000, 6.5, 9.2],
[1414108800000, 7.9, 10.7],
[1414195200000, 6.1, 10.9],
[1414281600000, 10.3, 13.1],
[1414371600000, 7.1, 13.3],
[1414458000000, 0.0, 10.1],
[1414544400000, 0.0, 5.7],
[1414630800000, 3.9, 4.6],
[1414717200000, 4.0, 4.8],
[1414803600000, 4.8, 11.2],
[1414890000000, 7.0, 8.5],
[1414976400000, 3.0, 9.8],
[1415062800000, 2.8, 5.9],
[1415149200000, 0.8, 4.8],
[1415235600000, -0.2, 2.9],
[1415322000000, -0.6, 5.5],
[1415408400000, 6.6, 10.3],
[1415494800000, 5.4, 7.3],
[1415581200000, 3.0, 8.4],
[1415667600000, 0.4, 3.2],
[1415754000000, -0.1, 6.8],
[1415840400000, 4.8, 8.8],
[1415926800000, 4.6, 8.5],
[1416013200000, 4.3, 7.7],
[1416099600000, 3.3, 7.5],
[1416186000000, -0.4, 3.2],
[1416272400000, 1.9, 4.7],
[1416358800000, -0.2, 3.7],
[1416445200000, -1.3, 2.1],
[1416531600000, -1.8, 0.9],
[1416618000000, -2.7, 1.3],
[1416704400000, 0.3, 2.5],
[1416790800000, 3.4, 6.5],
[1416877200000, 0.8, 6.1],
[1416963600000, -1.0, 1.3],
[1417050000000, 0.4, 3.1],
[1417136400000, -1.2, 1.9],
[1417222800000, -1.1, 2.8],
[1417309200000, -0.7, 1.8],
[1417395600000, 0.5, 2.5],
[1417482000000, 1.4, 3.2],
[1417568400000, 4.5, 10.2],
[1417654800000, 0.4, 10.0],
[1417741200000, 2.5, 3.7],
[1417827600000, 1.1, 5.0],
[1417914000000, 2.0, 4.4],
[1418000400000, 1.4, 2.2],
[1418086800000, 0.7, 4.6],
[1418173200000, 1.9, 3.9],
[1418259600000, -0.2, 3.7],
[1418346000000, -0.1, 1.7],
[1418432400000, -1.0, 3.8],
[1418518800000, 0.5, 5.4],
[1418605200000, -1.7, 5.6],
[1418691600000, 0.3, 2.8],
[1418778000000, -3.0, 0.4],
[1418864400000, -1.1, 1.5],
[1418950800000, 0.8, 3.4],
[1419037200000, 0.9, 4.4],
[1419123600000, 0.3, 3.9],
[1419210000000, 0.6, 5.3],
[1419296400000, 1.5, 4.4],
[1419382800000, 0, 0],
[1419469200000, 0, 0],
[1419555600000, -4.2, -4.1],
[1419642000000, -10.2, -5.2],
[1419728400000, -8.4, -4.1],
[1419814800000, -5.2, 2.4],
[1419901200000, 1.3, 2.5],
[1419987600000, 1.6, 4.2]
]
# today = datetime.today().date()
# i = 0
# for t in t_data:
#     create_date = today - timedelta(days=i)
#     ts = int(time.mktime(time.strptime(str(create_date), '%Y-%m-%d')))
#     thistory = THistory(create_date=ts*1000, max_t=t[2], min_t=t[1], equipment_id=xinan1id)
#     session.add(thistory)
#     i = i-1
# session.commit()
# eqp = session.query(Equipment).filter(Equipment.id == xinan1id).first()
# big_history = session.query(THistory).filter(THistory.equipment_id == eqp.id).filter(THistory.max_t>eqp.max_t)
# small_history = session.query(THistory).filter(THistory.equipment_id == eqp.id).filter(THistory.min_t<eqp.min_t)
#
# for item in big_history:
#     excep = EquipmentException(eqp_id=eqp.id,create_date=item.create_date,reason='温度过高')
#     session.add(excep)
# for item in small_history:
#     excep = EquipmentException(eqp_id=eqp.id,create_date=item.create_date,reason='温度过低')
#     session.add(excep)
#
# session.commit()
