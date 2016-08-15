# -*- coding: utf-8 -*-
#!/usr/bin/env python
# Copyright (c) 20016-2016 The i65535.
# See LICENSE for details.
"""
实现数据库的连接，查询，等功能
"""

import os
import platform
import subprocess
import threading
import time

from pymongo.errors import AutoReconnect
from pymongo.mongo_client import MongoClient

from common.guard import LockGuard
from frame.Logger import Log, PrintStack, Logger
from frame.configmgr import GetSysConfig
from mongodb.dbconst import ID, MAIN_DB_NAME, LOG_TABLE, IDENTITY_TABLE


def lost_connection_retry(func):
    def wappedFun(*args,**kwargs):
        try:
            result = func(*args,**kwargs)
        except AutoReconnect:
            dbmgr = args[0]
            getattr(dbmgr,"autoConnect")
            result = func(*args,**kwargs)
        return result
    return wappedFun


class DBMgr(object):
    __lock = threading.Lock()

    @classmethod
    def instance(cls):
        '''
        Limits application to single instance
        '''
        with LockGuard(cls.__lock):
            if not hasattr(cls, "_instance"):
                cls._instance = cls()
        
        if not cls._instance.isDBRuning():
            cls._instance.startDBserver()
        
        return cls._instance

    def __init__(self,db_host=None,db_port=None):
        self.conn = None

        self.host = db_host or GetSysConfig("db_host")
        self.osname = None
        try:
            self.conn = MongoClient(self.host)
        except Exception,e:
            PrintStack()
            Log(1,"connect to Mongdb fail,as[%s]"%(str(e)))
        else:
            Log(3,"Connect to db success.")
        
    def autoConnect(self):
        self.conn = MongoClient(self.host)
        
    def init_db_config(self):
        if self.osname :
            return True
            
        self.db_work_path = GetSysConfig("db_work_path")
        self.DBConfPath = os.path.join(self.db_work_path,"conf")
        self.MongoPath = GetSysConfig("mongo_db_path")
        osname = platform.system()
        if osname == "Windows":
            self.DBConfPath = os.path.join(self.DBConfPath,"mongodb.conf") 
            self.shell = False
        else:
            self.DBConfPath = os.path.join(self.DBConfPath,"mongodb_linux.conf") 
            self.shell = True
            
        if not os.path.isfile(self.MongoPath):
            Log(1,"startDBserver fail,as[The mongo file not exist.]")
            return False
            
        if not os.path.isfile(self.DBConfPath):
            Log(1,"startDBserver fail,as[The mongo config file not exist.]")
            return False
        
        self.osname = osname
        return True
    
    def db_auto_check(self):
        while True:
            try:
                if not self.isDBRuning():
                    self.startDBserver()
            except:
                PrintStack()
                
            time.sleep(30)

    def init(self):
        '''
        initialize instance,and start database server
        '''
        t = threading.Thread(target=self.db_auto_check,name="db_auto_check")
        t.setDaemon(True)
        t.start()
        

    def startDBserver(self):
        '''
        startDBserver,wait 3 second for check server status
        '''
        index = self.host.find('127.0.0.1')
        index = self.host.find('localhost') if index == -1 else index
        if index == -1:
            Log(1,"Can not start the MongoDB server[%s]"%(self.host))
            return False
    
        if not self.init_db_config():
            Log(1,"startDBserver load MongoDB config fail.")
            return False            
            
        cmd = "%s --config %s"%(self.MongoPath,self.DBConfPath)
        print cmd
        try:
            if self.osname == "Windows":
                subPrc = subprocess.Popen(cmd,shell=self.shell, cwd=self.db_work_path)
            else:#必须加上close_fds=True，否则子进程会一直存在
                subPrc = subprocess.Popen(cmd,shell=self.shell, cwd=self.db_work_path,close_fds=True)
        except Exception,e:
            print str(e)
            return False
        else:
            # wait for 10 second,
            sec = 10
            while sec :
                code = subPrc.poll()
                if code:
                    return False
                elif self.isDBRuning():
                    break;
                sec -= 1
                time.sleep(1)
            return True


    def isDBRuning(self):
        '''
        try to connect to mongo server
        '''
        try:
            if self.conn is None:
                self.conn = MongoClient(self.host)
            self.conn.server_info()
        except Exception,e:
            Log(1,"Get mongodb server info fail,as[%s]"%(str(e)))
            return False
        else:
            return True

        
    
    def get_all_table(self):
        return self.conn.database_names()
    
    def drop_db(self,db_name):
        return self.conn.drop_database(db_name)
    
    def copy_db(self, source_db_name, target_db_name):
        self.conn.admin.command('copydb',
                         fromdb=source_db_name,
                         todb=target_db_name)
    
    def drop_cn(self, db, collection):
        return self.conn[db][collection].drop()
    
    def insert_record(self,db,collection,record):
        '''
        @record :{'key1':'value1',...}
        '''
        return self.conn[db][collection].insert_one(record)
    
    def insert_records(self, db, collection, records, ordered=True):
        '''
        @record :{'key1':'value1',...}
        '''
        return self.conn[db][collection].insert_many(records, ordered)

    def get_collection(self,db,collection):
        return self.conn[db][collection]
    
    def get_records(self,db,collection, query, **kwargs):
        result = self.conn[db][collection].find(query, **kwargs)
        arr = []
        for i in result:
            arr.append(i)
        return arr
    
    def get_record_page(self,db,collection,query,orderby,pageNo,page_size, **kwargs):
        result = None
        count = self.conn[db][collection].find(query, **kwargs).count()
    
        if count < page_size:
            result =  self.conn[db][collection].find(query, **kwargs).sort(orderby.items())
        elif pageNo <= 1:
            result = self.conn[db][collection].find(query, **kwargs).sort(orderby.items()).limit(page_size)
        else:
            skip_count = (pageNo - 1) * page_size
            result = self.conn[db][collection].find(query, **kwargs).sort(orderby.items()).skip(skip_count).limit(page_size)
            
        arr = []
        for i in result:
            arr.append(i)        
            
        return arr,count

    def get_all_record(self,db,collection,**kwargs):
        arr = []
        for i in self.conn[db][collection].find(**kwargs):
            #del i[ID]
            arr.append(i)
        return arr 
    
    def get_all_records_sort(self,db,collection,sort_list, **kwargs):
        records = []
        result = self.conn[db][collection].find(**kwargs).sort(sort_list)
       
        for ret in result:
            records.append(ret)
        return records
    
    def get_record_count(self,db,collection,query=None):
        if query:
            return self.conn[db][collection].count(query)
        return self.conn[db][collection].count()
    
    def get_all_record_page(self,db,collection,orderby,pageNo,page_size, **kwargs):
        result = None
        count = self.conn[db][collection].count()
        if count < page_size:
            result =  self.conn[db][collection].find(**kwargs).sort(orderby.items())
        elif pageNo <= 1:
            result = self.conn[db][collection].find(**kwargs).sort(orderby.items()).limit(page_size)
        else:
            skip_count = (pageNo - 1) * page_size
            result = self.conn[db][collection].find(**kwargs).sort(orderby.items()).skip(skip_count).limit(page_size)
            
        arr = []
        for i in result:
            arr.append(i)
        return arr,count

    def delete_record(self,db,collection,_filter):
        return self.conn[db][collection].delete_many(_filter)

    def update_record(self,db,collection,query,value):
        return self.conn[db][collection].update_one(query,value)
    
    def update_records(self, db, collection, query, value, upsert=False):
        return self.conn[db][collection].update_many(query, {"$set":value}, upsert)

    def find_and_modify(self,db,collection,query,value,upsert=False):
        return self.conn[db][collection].find_one_and_update(query,{'$set':value},upsert=upsert)
    
    def remove_all(self,db,collection):
        return self.conn[db][collection].drop()
    
    def getID(self,db,collection,query,step):
        return self.conn[db][collection].find_one_and_update(query,{"$inc":step},upsert=True)
    
    def find_and_modify_num(self,db,collection,query,value,upsert=False):
        return self.conn[db][collection].find_one_and_update(query,{'$inc':value}, upsert=upsert)
    
    def find_and_modify_nums(self,db,collection,query,value,upsert=False):
        return self.conn[db][collection].update_many(query,{'$inc':value}, upsert=upsert)
    
    def create_js(self,db,func_name,func_body):
        self.del_js(db,func_name)
        func_str = 'self.conn[db].system_js.%s="""%s"""'%(func_name,func_body)
        exec(func_str)
        return True
        
    def check_func_exist(self,db,func_name):
        count = self.conn[db].system.js.count({ID: func_name})
        return 1 == count
    
    def db_exec(self,db,func_name,*args):
        if self.check_func_exist(db, func_name):
            func_str = "self.conn[db].system_js.%s(*args)"%(func_name)
            result = eval(func_str)
            return result
        else:
            return False
    
    def del_js(self,db,func_name):
        func_str = "del self.conn[db].system_js.%s"%(func_name)
        exec(func_str)
        return True
    
    def rename(self, db, collection, new_name):
        return self.conn[db][collection].rename(new_name)

    def log(self, level, msg):
        data = {'level':level, 'content':msg, 'time':time.time() * 1000, 'email':0, 'fail':0}
        try:
            r = self.getID(MAIN_DB_NAME, IDENTITY_TABLE, {"_id":LOG_TABLE},{"next":1})
            data[ID] = r.get('next', 0)
            self.insert_record(MAIN_DB_NAME, LOG_TABLE, data)
        except Exception:
            return False
        return True


DBMgr.instance().init()
Logger.dblogger = DBMgr.instance().log

        
