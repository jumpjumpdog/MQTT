"""
    FreeIOT Parse Package Initial Script

    Author: Noah Gao
    Updated at: 2018-02-23
"""
import os
from pymongo import MongoClient

mongo = MongoClient(host="localhost", port=27017)
mongo.db = mongo[os.environ.get("MONGO_DBNAME") or "test"]
