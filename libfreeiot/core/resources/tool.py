#!/usr/bin/env python
# -*- coding: utf-8 -*-
import uuid

from bson import json_util
from flask import Response
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_

from models import *



def getUuid():
    uuid_obj = uuid.uuid1()
    uuid_str = str(uuid_obj)
    return "".join(uuid_str.split("-"))

def adminQuery(name,password):
    print(name)
    print(password)
    admin = session.query(Admin).filter(Admin.name == name).first()
    if admin is None:
        return {"result":False, "reason":"No such admin"}
    elif admin.password != password:
        return {"result":False, "reason":"password error"}
    else:
        new_uuid = getUuid()
        admin_json = admin.to_json()
        admin_json["uuid"] = new_uuid
        return {"result":True,"data":admin_json}


def ownerQuery():
    owners = session.query(Owner).all()
    owner_list = []
    for owner in owners:
        owner_list.append(owner.to_json())
    return {"result":True, "data":owner_list}

def equipmentQuery():
    session.commit()
    eqps = session.query(Equipment).all()
    eqp_list = []
    for eqp in eqps:
        print(eqp.to_json())
        eqp_list.append(eqp.to_json())
    print(len(eqp_list))
    return {"result": True, "data": eqp_list}

def addEqm(data):
    try:
        print(data)
        eqm = Equipment(_id=data["eqm_id"], name=data["eqm_name"], max_t=data["max_t"], min_t=data["min_t"], create_date=None, status=data["is_valid"])
        owner_ids = data["selected_owners"]
        for owner_id in owner_ids:
            print(owner_id)
            owner = session.query(Owner).filter(Owner.id == owner_id).first()
            if owner is not None:
                eqm.owners.append(owner)
        session.add(eqm)
        session.commit()
        return {"result":True, "data":eqm.to_json()}
    except SQLAlchemyError  as e:
        print("添加设备异常")
        print(str(e))
        return {"result":False}

def addOwner(data):
    try:
        print(data)
        owner = Owner(name=data['name'],password=data['password'],_id=data['id'], telephone = data['telephone'])
        session.add(owner)
        session.commit()
        return {"result":True}
    except SQLAlchemyError as e:
        print('添加操作员异常')
        print(str(e))
        return {"result": False}

def  editEqm(data):
    try:
        eqm_id = data["id"]
        eqm = session.query(Equipment).filter(Equipment.id==eqm_id).first()
        eqm.status = data["status"]
        eqm.name = data["name"]
        owners = data['owners']
        tmp_owners = []
        for owner_id in owners:
            owner = session.query(Owner).filter(Owner.id == owner_id).first()
            tmp_owners.append(owner)
        eqm.owners = tmp_owners
        session.commit()
        return {"result":True, "data":eqm.to_json()}
    except SQLAlchemyError as e:
        print("修改设备异常")
        print(str(e))
        return {"result": False}

def editOwner(data):
    try:
        print(data)
        owner_id = data['id']
        owner = session.query(Owner).filter(Owner.id == owner_id).first()
        owner.name = data['name']
        owner.password = data['password']
        owner.telephone = data['telephone']
        eqps = data['eqp_list']
        tmp_eqps = []
        for eqp_id in eqps:
            eqp = session.query(Equipment).filter(Equipment.id == eqp_id).first()
            tmp_eqps.append(eqp)
        owner.equipments = tmp_eqps
        session.commit()
        return {"result": True, "data": owner.to_json()}
    except SQLAlchemyError as e:
        print("修改用户异常")
        print(str(e))
        return {"result": False}


def deleteEqm(data):
    try:
        eqm_id = data["id"]
        session.query(Equipment).filter(Equipment.id==eqm_id).delete()
        session.commit()
        return {"result": True}
    except SQLAlchemyError as e:
        print("删除设备异常")
        print(str(e))
        return {"result": False}

def deleteOwner(data):
    try:
        print(data)
        owner_id = data["id"]
        session.query(Owner).filter(Owner.id == owner_id).delete()
        session.commit()
        return {"result": True}
    except SQLAlchemyError as e:
        print('删除用户异常')
        print(str(e))
        return {"result": False}


def normalInfo(data):
    try:
        eqp_id= data["id"]
        eqp = session.query(Equipment).filter(Equipment.id==eqp_id).first()
        tdata = getTHistory(data)
        owners = getOwnersByEqpId2(data)
        res_json = {"result": True,'data':eqp.to_json(),'tdata':tdata,'select_owners':owners[0],'owners':owners[1]}
        return res_json
    #     else:
    #         return {"result": True,'data':eqp.to_json(),'tdata':tdata,'select_owners':owners['select_owners_list'],'owners':owners['all_owner_list']}
    except SQLAlchemyError as e:
        print('获取设备基本信息异常')
        print(str(e))
        return {"result": False}

def getOwnersByEqpId2(data):
    try:
        eqp_id = data["id"]
        eqp = session.query(Equipment).filter(Equipment.id == eqp_id).first()
        all_owners = session.query(Owner).all()
        all_owner_list = []
        for owner in all_owners:
            all_owner_list.append({'label': owner.name, 'value': owner.id})
        if eqp is None:
            return ( [],  all_owner_list)
        else:
            select_owners = list(eqp.owners)
            select_owners_list = []
            for owner in select_owners:
                select_owners_list.append({'label': owner.name, 'value': owner.id})
            return ( select_owners_list,  all_owner_list)
    except SQLAlchemyError as e:
        print('根据设备id 获取owners失败')
        print(str(e))
        return ([],[])

def getOwnersByEqpId(data):
    try:
        eqp_id = data["id"]
        eqp = session.query(Equipment).filter(Equipment.id == eqp_id).first()
        all_owners  = session.query(Owner).all()
        all_owner_list = []
        print(data)
        for owner in all_owners:
            all_owner_list.append({'label':owner.name,'value':owner.id})
        if eqp is None:
            return {'result':True,'select_owners':[],'owners':all_owner_list}
        else:
            select_owners = list(eqp.owners)
            select_owners_list = []
            for owner in select_owners:
                select_owners_list.append({'label':owner.name,'value':owner.id})
            return {'result':True,'select_owners':select_owners_list,'owners':all_owner_list}
    except SQLAlchemyError as e:
        print('根据设备id 获取owners失败')
        print(str(e))
        return {"result": False}


def getEqpsByOwnerId(data):
    try:
        owner_id = data["id"]
        owner = session.query(Owner).filter(Owner.id == owner_id).first()
        all_eqps  = session.query(Equipment).all()
        all_eqps_list = []
        print(data)
        for eqp in all_eqps:
            all_eqps_list.append({'label':eqp.name,'value':eqp.id})
        if owner is None:
            return {'result':True,'selectedEqpList':[],'eqpList':all_eqps_list}
        else:
            select_eqps = list(owner.equipments)
            select_eqps_list = []
            for eqp in select_eqps:
                select_eqps_list.append({'label':eqp.name,'value':eqp.id})
            return {'result':True,'selectedEqpList':select_eqps_list,'eqpList':all_eqps_list}
    except SQLAlchemyError as e:
        print('根据设备id 获取owners失败')
        print(str(e))
        return {"result": False}

def getTHistory(data):
    eqp_id = data['id']
    print(data)
    ts = session.query(THistory).filter(THistory.equipment_id==eqp_id).order_by(THistory.create_date).all()
    print(len(ts))
    t_list = []
    for item in ts:
        t_list.append([item.create_date,item.min_t,item.max_t])
    return t_list

def generateExceptions(data):
    eqp_id = data['eqp_id']
    print(data)
    t_histroy = session.query(Equipment).fileter(Equipment.id == eqp_id).t_history
    print(t_histroy)
    return {"result": False}

def getEqpById(id):
    eqp = session.query(Equipment).filter(Equipment.id == id).first()
    return eqp

def queryExceptions():
    session.commit()
    exceptions = session.query(EquipmentException).filter(or_(EquipmentException.status=='待处理' , EquipmentException.status=='待分配'))
    exception_list = []
    for exception in exceptions:
        tempJson = exception.to_json()
        exception_list.append(tempJson)
    for (index,exception) in enumerate(exception_list):
        eqp = getEqpById(exception['eqp_id'])
        exception_list[index]['name'] = eqp.name
        exception_list[index]['owner_name'] =''
    print(exception_list)
    return {'data':exception_list}


def handleException(data):
    id = data['id']
    owner_id = data['owner_id']
    admin_id = data['admin_id']
    fix_date = int(round(time.time() * 1000))
    session.query(EquipmentException).filter(EquipmentException.id == id).update({EquipmentException.status : '已处理',EquipmentException.owner_id:owner_id,EquipmentException.admin_id:admin_id,EquipmentException.fix_date:fix_date})
    session.commit()
    return {"result":True}


def getFixHisory(data):
    owner_id  = data['id']
    exceptions =  session.query(EquipmentException).filter(EquipmentException.owner_id==owner_id).filter(EquipmentException.status=='已处理').all()
    eqps = session.query(Owner).filter(Owner.id==owner_id).first().equipments
    fix_list = []
    eqps_list = []
    for excep in exceptions:
        fix_list.append(excep.to_json())
    for eqp in eqps:
        eqps_list.append({'label':eqp.name,'value':eqp.id})
    return {'data':fix_list,'eqps':eqps_list}

def addException(data):
    eqp_id = data['id']
    t = data['message']['temperature']['t']
    create_date = data['create_date']
    reason = data['reason']
    try:
        session.commit()
        exception = EquipmentException(eqp_id=eqp_id, reason=reason, create_date=create_date,t = t)
        session.add(exception)
        session.commit()
        return {"result":True}
    except SQLAlchemyError as e:
        print('添加异常失败')
        print(str(e))
        return {"result": False}

def isNiceEqp(eqp_id):
    eqp = session.query(Equipment).filter(or_(Equipment.status=='正常运行',Equipment.status=='设备异常')).filter(Equipment.id == eqp_id).first()
    return eqp


def isAdmin(data):
    name = data['name']
    password = data['password']
    admin = session.query(Admin).filter(Admin.name == name).filter(Admin.password==password).first()
    return admin

def isOwner(data):
    name = data['name']
    password = data['password']
    owner = session.query(Owner).filter(Owner.name==name).filter(Owner.password==password).first()
    return  owner

def login(data):
    if(isAdmin(data)):
        return {'userType':'admin'}
    else:
        return  {'userType':'owner'}


def getOwnerById(ownerId):
    return session.query(Owner).filter(Owner.id==ownerId).first()

def arrangeException(data):
    id = data['id']
    owner_id = data['owner_id']
    exp = session.query(EquipmentException).filter(EquipmentException.id == id).first()
    exp.status = '待处理'
    exp.owner_id = owner_id
    owner = getOwnerById(owner_id)
    res = {'owner_name':owner.name}
    session.commit()
    return res
