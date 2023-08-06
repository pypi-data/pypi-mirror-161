# -*- coding: utf-8 -*-
import os,json
DB_URL = {'sly': 'mysql+mysqlconnector://quant:quant@192.168.199.137/quant' if 'SYL_DB' not in os.environ else os.environ['SYL_DB']}
MONGO_DB =  {'host':'192.168.199.137','port':37017, 'user':'seleya','password':'123456!','db':'seleya'} if 'MONGO_DB' not in os.environ else json.loads(os.environ['MONGO_DB'])
SERVER_URL = 'app.portageb.com' if 'SERVER_URL' not in os.environ else os.environ['SERVER_URL']
server = (SERVER_URL, 50008, SERVER_URL, 443)