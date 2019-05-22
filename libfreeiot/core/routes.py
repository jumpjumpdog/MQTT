import os
import datetime
from bson import json_util
from flask import request, jsonify, Response
from flask_restful import Api
from flask_jwt_simple import JWTManager, create_jwt
from .resources.device import Device
from .resources.data import Data
from .resources.mysql import Mysql
from libfreeiot.core import mongo


JWT_EXPIRES = 7 * 24 * 3600

def create_routes(app, scope = None):
    '''
      Function for create routes
    '''
    if scope is None:
        scope = dict()
    app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this!
    app.config['JWT_EXPIRES'] = datetime.timedelta(7)
    app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), '/images')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

    jwt = JWTManager(app)

    @app.route('/hello')
    def say_hello():
        '''
          Index Route
        '''
        return jsonify({"msg": "Hello World!"})

    @app.route('/api/mongo', methods=['POST'])
    def load_charts():
        eqp_id = request.json.get('eqp_id',None)
        res = list(mongo.db.temperature.find({"eqp_id":eqp_id}).sort("create_time",-1).limit(40))
        if len(res) == 0:
            res_json = {'result':False}
            return Response(
                json_util.dumps(res_json),
                mimetype='application/json'
            ), 200
        res.reverse()
        t_average = []
        t_range = []
        for item in res:
            t_average.append([item['create_time'],item['temperature']['t']])
            t_range.append([item['create_time'],item['temperature']['max_t'],item['temperature']['min_t']])
        res_json = {'result':True,'t_average':t_average,'t_range':t_range}
        return Response(
            json_util.dumps(res_json),
            mimetype='application/json'
        ), 200



    @app.route('/api/auth', methods=['POST'])
    def auth():
        '''
          JWT Auth Route
        '''
        username = request.json.get('username', None)
        password = request.json.get('password', None)
        if not username:
            return jsonify({"msg": "Missing username parameter"}), 400
        if not password:
            return jsonify({"msg": "Missing password parameter"}), 400
        if 'auth'in scope.keys():
            authr = scope["auth"].login(username, password)
            if not authr:
                return jsonify({"msg": "Bad username or password"}), 401
        else:
            if username != 'admin' or password != 'admin':
                return jsonify({"msg": "Bad username or password"}), 401
        res = {}
        res["jwt"] = create_jwt(identity=username)
        return Response(
            json_util.dumps(res),
            mimetype='application/json'
        ), 200

    # RESTFul API Routes definition
    api = Api(app)
    api.add_resource(Device, '/api/device', '/api/device/<string:device_id>')
    api.add_resource(Data, '/api/data', '/api/data/<string:data_id>')
    api.add_resource(Mysql, '/api/mysql')

    return (app, api)
