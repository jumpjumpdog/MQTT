#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import request
from flask_restful import Resource,reqparse
from libfreeiot.core import mysql
from libfreeiot.core.resources.tool import  adminQuery,  ownerQuery, addEqm, equipmentQuery,editEqm, deleteEqm, addOwner, \
    getOwnersByEqpId, normalInfo, getEqpsByOwnerId, deleteOwner, editOwner, getTHistory, generateExceptions, \
    queryExceptions, handleException, getFixHisory, addException, login, arrangeException

parser = reqparse.RequestParser()

class Mysql(Resource):
    def get(self):
        return "get mysql"
    def post(self):
        args = request.get_json(force=True)
        action = args["action"]
        print(action)
        if "adminAuth"==action:
            print("adminAuth function")
            return adminQuery(args["name"], args["password"])
        elif "owners" == action:
            print("owner function")
            return ownerQuery()
        elif "createEqm" == action:
            print("createEqm Function")
            return addEqm(data=args)
        elif "createOwner" == action:
            print("create owner function")
            return addOwner(data=args)
        elif "equipments" == action:
            print("equipments Function")
            return equipmentQuery()
        elif 'deleteOwner' == action:
            print("delete owner Function")
            return deleteOwner(data=args)
        elif "editEqp" == action:
            print("edit equipment Function")
            return  editEqm(data=args)
        elif "deleteEqp"==action:
            print("delete equipment Function")
            return deleteEqm(data=args)
        elif 'normalInfo'==action:
            print("normalInfo"==action)
            return normalInfo(data=args)
        elif 'getOwnersByEqpId'==action:
            print('getOwnersByEqpId function')
            return getOwnersByEqpId(data=args)
        elif 'getEqpsByOwnerId' == action:
            print('getEqpsByOwnerId')
            return getEqpsByOwnerId(data=args)
        elif 'editOwner' == action:
            print('editOwner function')
            return editOwner(data=args)
        elif 'getTHistory' == action:
            print('getTHistory function')
            return getTHistory(data=args)
        elif 'generateExceptions' == action:
            print('generateExceptions function')
            return generateExceptions(data=args)
        elif 'queryException' == action:
            print('queryException function')
            return queryExceptions()
        elif 'handleException' == action:
            print('handleException function')
            return handleException(data=args)
        elif 'getFixHisory' == action:
            print('getFixHisory function')
            return getFixHisory(data=args)
        elif 'addException' == action:
            print(args)
            return addException(data=args)
            print('addException function')
        elif 'login' == action:
            print(args)
            print('login function')
            return login(data=args)
        elif 'arrangeException'== action:
            print(args)
            print('arrange exception')
            return arrangeException(data=args)

        else:
            print("other function")
            return {}