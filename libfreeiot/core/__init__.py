"""
    FreeIOT Core Package Initial Script

    Author: Noah Gao
    Updated at: 2018-02-23
"""
from flask import Flask
from flask_cors import CORS
from flask_pymongo import PyMongo
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit

from libfreeiot.config import CONFIG
from libfreeiot.core.resources.tool import  getUuid
mongo = None
mysql = None

def create_app(config_name, scope = None):
    """
        Function for create Flask App instance
    """
    global mongo
    if scope is None:
        scope = dict()
    app = Flask(__name__) # Initialize app

    CORS(app, supports_credentials=True);

    app.config['SECRET_KEY'] = 'secret!'
    socketio = SocketIO(app)
    # Import project config
    app.config.from_object(CONFIG[config_name])
    CONFIG[config_name].init_app(app)

    app.config["MONGO_URI"] = "mongodb://" + app.config["MONGO_HOST"] + ":" + str(app.config["MONGO_PORT"]) + "/" + app.config["MONGO_DBNAME"]

    # Init MongoDB Ext
    mongo = PyMongo(app)

    from libfreeiot.core.routes import create_routes
    app, api= create_routes(app, scope) # Initialize api services with Routes definition

    # Init MysqlDB
    app.config['SECRET_KEY'] = '123'
    # 这里登陆的是root用户，要填上自己的密码，MySQL的默认端口是3306，填上之前创建的数据库名,连接方式参考 \
    # http://docs.sqlalchemy.org/en/latest/dialects/mysql.html
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8'.format("root", "123","localhost", "3306","mqttdb")
    # 设置这一项是每次请求结束后都会自动提交数据库中的变动
    app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
    # 实例化
    mysql = SQLAlchemy(app)
    scope['db'] = mysql
    # add_data(scope)

    return app

def add_data(scope):
    from models import Admin,Owner,THistory,HHistory,Equipment
    # 创建表
    db = scope['db']

    admin = Admin('sjw','123')
    db.session.add(admin)
    db.session.commit()

    owner = Owner('李强','123')
    db.session.add(owner)
    db.session.commit()

    owner2 = Owner('王建林','123')
    db.session.add(owner2)
    db.session.commit()

    eqp_name = '设备2'
    eqp_uuid = getUuid()
    print(eqp_uuid)
    eqp = Equipment(_id=eqp_uuid,name=eqp_name,max_t=40,min_t=0,max_h=50,min_h=10,owner_id=owner.id,create_date=None)
    db.session.add(eqp)
    db.session.commit()
