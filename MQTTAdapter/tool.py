#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy.exc import SQLAlchemyError

from model import *


def equipmentQuery():
    eqps = session.query(Equipment).filter(Equipment.status=='正常运行').all()
    eqp_list = []
    for eqp in eqps:
        print(eqp.to_json())
        eqp_list.append(eqp.to_json())
    return eqp_list

def getEqpByID(eqpId):
    eqp = session.query(Equipment).filter(Equipment.id==eqpId).first()
    return eqp


def online(eqpId):
    try:
        session.commit()
        eqp = session.query(Equipment).filter(Equipment.id == eqpId).first()
        eqp.status = '正常运行'
        session.commit()
    except SQLAlchemyError as e:
        print("online err")
