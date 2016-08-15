#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 20016-2016 The i65535.
# See LICENSE for details.
"""
initialize database ,create table and insert some system info
"""

from base64 import b32encode
import codecs
import hashlib
import imp
import json
import os
import shutil
import time

from common.util import Result
from frame.Logger import SysLog, PrintStack
from frame.errcode import BACKUP_DATA_FILE_INVALID_ERR, BACKUP_DATABASE_FAIL_ERR, \
    CLEAR_DATABASE_FAIL_ERR, DATABASE_NOT_EXIST_ERR, RESTORE_DATABASE_FAIL_ERR
from mongodb.dbconst import ID, CONFIG_TABLE, \
    USER_TABLE, IDENTITY_TABLE, USER_GROUP_TABLE, REPOSITORY_TABLE, \
    NAMESPACE_TABLE, COMMENT_TABLE, TAG_TABLE, IMAGE_TABLE, \
    LAYER_TABLE, GROUP_NAMESPACE_TABLE, NOTIFICATION_TABLE, GROUP_TABLE, \
    EDITRECORD_TABLE, STORAGE_TABLE, SMTP_TABLE, EMAIL_TABLE, LOG_TABLE, \
    SCHEDULE_TABLE, MAIN_DB_NAME, LAYER_IMAGE_TABLE, LDAP_TABLE, \
    PULL_EVENT_TABLE, PUSH_EVENT_TABLE, TASK_TABLE, \
    SUB_TASK_TABLE, SYNCTASK, WORK_DATA_TABLE, EXTENSTION_TABLE
from mongodb.dbmgr import DBMgr


Tables = {
    CONFIG_TABLE:'CFG',                  # 存放支持修改的配置项    
    USER_TABLE:None,                     # 存放用户信息
    GROUP_TABLE:None,
    USER_GROUP_TABLE:None,               # 用户组
    REPOSITORY_TABLE:None,               # 仓库
    NAMESPACE_TABLE:None,                # 命名空间
    COMMENT_TABLE:None,                  # 评论 
    TAG_TABLE:None,                      # 标签
    IMAGE_TABLE:None,                    # 
    LAYER_TABLE:None,                    # 层 
    USER_GROUP_TABLE:None,               # 用户与组的关系表
    GROUP_NAMESPACE_TABLE:None,          # 用户组与命名空间的关系    
    NOTIFICATION_TABLE:None,             # Registry 的通知消息
    EDITRECORD_TABLE:None,               # Registry 的通知消息
    STORAGE_TABLE:None,                  # Registry 的通知消息
    SMTP_TABLE:None,                     # Registry 的通知消息
    EMAIL_TABLE:None,                    # Registry 的通知消息
    LOG_TABLE:None,                      # Registry 的通知消息
    SCHEDULE_TABLE:None,                 # 计划任务
    TASK_TABLE:None,
    SUB_TASK_TABLE:None,
    SYNCTASK:None,
    WORK_DATA_TABLE:None,
    EXTENSTION_TABLE:None
}



class CommonDB(object):
    def __init__(self,db_name,tables):
        self.db = db_name
        self.table_list = tables
        self.dbMgr = DBMgr.instance()

            
    def clear_db(self, db_name):
        if not self.is_db_exist(db_name):
            return True

        try:
            self.dbMgr.drop_db(db_name)
        except Exception,e:
            SysLog(1,"CommonDB.init_db [%s] fail [%s]"%(self.db,str(e)))
            return False
                
        SysLog(3,"CommonDB.clear_db [%s], success"%self.db)
                
        return True
    
    def copy_db(self, src_db_name, new_db_name):
        if not self.is_db_exist(src_db_name):
            SysLog(1, 'copy_db from[%s]to[%s]fail,as the src db not exist.'%(src_db_name, new_db_name))
            return False

        try:
            self.dbMgr.copy_db(src_db_name, new_db_name)
        except Exception,e:
            SysLog(1,"CommonDB.back_db [%s] fail [%s]"%(self.db,str(e)))
            return False
        else:
            return True

    
    def is_db_exist(self, db_name):
        arr = self.dbMgr.get_all_table()
        return True if db_name in arr else False
    
    
    def clean_data(self,cn_list):
        for collection in cn_list:
            self.dbMgr.remove_all(self.db,collection)
    
    
    def add_identity_key(self,id_key,pre_txt = None):
        record = {ID:id_key,"next":1000}
        if pre_txt is not None:
            record["pre"] = pre_txt
            
        return self.insert_record(IDENTITY_TABLE, record)
    
    def add_all_identity_key(self):
        for table_name,prefix in self.table_list.iteritems():
            self.add_identity_key(table_name,prefix)
    
    def del_identity_key(self,id_key):
        try:
            self.dbMgr.delete_record(self.db,IDENTITY_TABLE,{ID:id_key})
        except Exception,e:
            SysLog(1,"CommonDB.del_identity_key fail,[%s]"%str(e))
            return False
        return True
    
    def insert_record(self, cn, record):
        try:
            count = self.dbMgr.get_record_count(self.db, cn, {ID:record[ID]})
            if count:
                SysLog(2, "insert_record[%s]skip,as the record is exist already"%(str(record)))
                return False
            
            self.dbMgr.insert_record(self.db, cn, record)
        except Exception:
            PrintStack()
            return False
        else:
            return True
    
    def insert_records(self, cn, records):
        count = 0
        for record in records:
            if self.insert_record(cn, record):
                count += 1
            
        return len(records)
    
    def batch_insert_records(self, cn, records, step = 100):
        lenth = len(records)
        for index in range(0, lenth, step):
            if not self.real_batch_insert_records(cn, records[index:index + step]):
                return False
        
    def real_batch_insert_records(self, cn, records):
        try:
            self.dbMgr.insert_records(self.db, cn, records)
        except Exception:
            PrintStack()
            SysLog(3,"CommonDB.batch_insert_records fail, cn=[%s]"%(cn))
            return False
        else:
            SysLog(3,"CommonDB.batch_insert_records success, insert [%d] record into[%s]"%(len(records),cn))
            return True
    
    def create_js(self,func_name,func_body):
        return self.dbMgr.create_js(self.db,func_name,func_body)
    
    def loadJs(self,file_path):    
        try:
            fd = open(file_path,"r")
            jsStr = fd.read()
            fd.close()
        except Exception,e:
            SysLog(1,"loadJs [%s] fail. as [%s]"%(file_path,str(e)))
            return False
        else:
            return jsStr
        
    def parse_js(self,js_str):
        index = js_str.find("function")
        if index == -1:
            return
        func_name = js_str[0:index]
        eIndex = func_name.find("=")
        if eIndex == -1:
            return 
        func_name = func_name[0:eIndex]
        
        func_body = js_str[index:]
        self.create_js(func_name.strip(), func_body)
        
    def auto_load_js(self):
        workdir = os.path.dirname(os.path.abspath(__file__))
        workdir = os.path.join(workdir,"javascript")
        
        if not os.path.isdir(workdir):
            SysLog(1, 'auto_load_js fail,as the path[%s]not exist.'%(workdir))
            return
        
        dirs = os.listdir(workdir)
        for file_name in dirs:
            file_path = os.path.join(workdir,file_name)
            if os.path.isfile(file_path) and file_path.endswith(".js") :
                jsStr = self.loadJs(file_path)
                self.parse_js(jsStr)
            else:
                SysLog(3,"%s is not a js file"%file_path)
                
    def auto_import_data(self):
        workroot = os.path.dirname(os.path.abspath(__file__))
        datapath = os.path.join(workroot,"export")
        if not os.path.isdir(datapath):
            SysLog(1, 'auto_import_data fail,as the path[%s]not exist.'%(datapath))
            return
        
        py_arr = []
        pyc_arr = []
        dirs = os.listdir(datapath)
        for file_name in dirs:
            if file_name.endswith('.py'):
                py_arr.append(file_name)
            elif file_name.endswith('.pyc'):
                pyc_arr.append(file_name)
        
        if len(py_arr) == 0:
            py_arr = pyc_arr
            
        for file_name in py_arr:
            file_path = os.path.join(datapath,file_name)
            self.import_data(file_path)
            
    def import_data(self, fullpath):
        mod = self.load_from_file(fullpath)
        
        data = getattr(mod,"data",[])
        for t in data:
            ret = self.insert_records(t, data[t])
            SysLog(1,"CommonDB.auto_import_data success, insert [%d] record into %s"%(ret,t))
    
    def load_from_file(self,filepath):
        mod_name,file_ext = os.path.splitext(os.path.split(filepath)[-1])
        if file_ext.lower() == '.py':
            py_module = imp.load_source(mod_name, filepath)
        elif file_ext.lower() == '.pyc':
            py_module = imp.load_compiled(mod_name, filepath)
                
        return py_module
    
    def is_installed(self):
        if not self.is_db_exist(self.db):
            return False
        
        return True if self.dbMgr.get_record_count(self.db, USER_TABLE) else False

    def setup(self, clear_db=False):
        if clear_db:
            self.clear_db(self.db)
            
        self.add_all_identity_key()
        
        self.auto_import_data()
        self.auto_load_js()
        
        return 'install finished'
    
# --------------- data export begin ---------------------------------------- #
    def read_all_record(self,cn):
        return DBMgr.instance().get_all_record(self.db,cn)
            
    def to_string(self,data):
        try:
            return json.dumps(data)
        except Exception:
            PrintStack()
            SysLog(3, "to_string except [%s]"%(str(data)))
            return ''
        
    def parst_data(self,cn):
        arr = self.read_all_record(cn)
        if len(arr) == 0:
            return ''
        
        output = "\ndata['%s'] = ["%(cn)
        data = []
        for r in arr:
            txt = self.to_string(r)
            if txt:
                data.append(txt)
            
        output += ',\n'.join(data)
        output += "]\n\n" 
        
        return output
    
    def calc_hash(self, text):
        sh = hashlib.sha256()
        sh.update(text)

        return b32encode(sh.digest()[:20])
        
    def export_to_file(self, cn, export_folder):
        SysLog(3, "export_to_file in collections=[%s]"%(cn))
        output = self.parst_data(cn)
        if not output:
            return
        
        fileName = "%s%s.py"%(cn, self.calc_hash(output))
        self.save_file(output, export_folder, fileName)
        
            
    def save_file(self, text, export_folder, fileName):
        fullpath = os.path.join(export_folder,fileName)
        if not os.path.isfile(fullpath):
            fullpath = self.get_tmp_file(export_folder,fileName)
            
        if not os.path.isfile(fullpath):
            SysLog(1,"move file fail")
            return
        
        fd = codecs.open(fullpath,'a','utf-8')
        fd.write(text.decode('utf-8'))
        fd.close()
        
    def get_tmp_file(self,tar_dir,filename):
        workroot = os.path.dirname(os.path.abspath(__file__))
        fullpath = os.path.join(workroot,"temp.py")
        
        tarfile = os.path.join(tar_dir,filename)
        shutil.copyfile(fullpath, tarfile)
        return tarfile
    
    def export_data(self, collections, export_folder):
        if os.path.isdir(export_folder):
            shutil.rmtree(export_folder)
            
        os.mkdir(export_folder)
        
        for cn in collections:
            self.export_to_file(cn, export_folder)
            
    def valid_file_hash(self, file_name, full_path):
        if not os.path.isfile(full_path):
            SysLog(1, 'valid_file_hash fail, as the file[%s]not exist.'%(full_path))
            return False
        
        with open(full_path,"r") as fd:
            txt = fd.read()
        
        index = txt.find("data['")
        if index < 1:
            SysLog(1, 'valid_file_hash fail, as the file[%s]format invalid.'%(full_path))
            return False
        

        _hash = self.calc_hash(txt[index-1:])
        return file_name.find(_hash) > 0
        

    def test_data(self, import_folder):
        dirs = os.listdir(import_folder)
        for file_name in dirs:
            if file_name.endswith('.py'):
                fullpath = os.path.join(import_folder, file_name)
                if not self.valid_file_hash(file_name, fullpath):
                    return False

        return True
    
    def import_data_from_folder(self, import_folder):
        if not self.test_data(import_folder):
            SysLog(1, 'import_data_from_folder.test_data fail')
            return Result('', BACKUP_DATA_FILE_INVALID_ERR, 'The import data is invalid.')
        
        new_db_name = self.db + time.strftime("%Y%m%d%H%M%S",time.localtime())
        if not self.copy_db(self.db, new_db_name):
            SysLog(1, 'import_data_from_folder.copy_db fail')
            return Result('', BACKUP_DATABASE_FAIL_ERR, 'backup database fail.')
        
        SysLog(1, 'import_data_from_folder.copy_db from[%s]to[%s]success'%(self.db, new_db_name))
        
        if not self.clear_db(self.db):
            SysLog(1, 'import_data_from_folder.clear_db fail')
            return Result('', CLEAR_DATABASE_FAIL_ERR, 'clear database fail.')
        
        SysLog(1, 'import_data_from_folder.clear_db [%s] success'%(self.db))
        
        self.auto_load_js()
        
        return self.batch_import_data(import_folder)
            
            
    def batch_import_data(self, import_folder):
        dirs = os.listdir(import_folder)
        for file_name in dirs:
            if file_name.endswith('.py'):
                fullpath = os.path.join(import_folder, file_name)
                mod = self.load_from_file(fullpath)
                data = getattr(mod,"data",[])
                for t in data:
                    self.batch_insert_records(t, data[t])
        
        SysLog(1, 'batch_import_data from[%s] success'%(import_folder))
        return Result('finished')
    
    def get_back_up_db(self):
        arr = []
        table_list = self.dbMgr.get_all_table()
        for db_name in table_list:
            if db_name == MAIN_DB_NAME:
                continue
            
            if db_name.find(MAIN_DB_NAME) == 0:
                arr.append(db_name)
                
        return arr
                
    def drop_back_db(self, db_name):
        SysLog(3, 'drop_back_db in with database[%s].'%(db_name))
        if db_name == MAIN_DB_NAME:
            SysLog(1, 'drop_back_db fail,as the database[%s] not allow to drop.'%(db_name))
            return False
        
        return self.clear_db(db_name)
    
    
    def restore_backup(self, db_name):
        SysLog(3, 'restore_backup in with database[%s].'%(db_name))
        if db_name == MAIN_DB_NAME:
            return Result('nothing to do')
        
        if not self.is_db_exist(db_name):
            SysLog(1, 'restore_backup fail, as the database[%s] not exist.'%(db_name))
            return Result('', DATABASE_NOT_EXIST_ERR, 'the database not exit')
        
        new_db_name = MAIN_DB_NAME + time.strftime("%Y%m%d%H%M%S",time.localtime())
        if not self.copy_db(MAIN_DB_NAME, new_db_name):
            SysLog(1, 'restore_backup.copy_db fail')
            return Result('', BACKUP_DATABASE_FAIL_ERR, 'backup database fail.')
        
        SysLog(3, 'restore_backup.copy_db from[%s]to[%s]success'%(MAIN_DB_NAME, new_db_name))
        
        if not self.clear_db(MAIN_DB_NAME):
            SysLog(1, 'restore_backup.clear_db[%s] fail'%(MAIN_DB_NAME))
            return Result('', CLEAR_DATABASE_FAIL_ERR, 'clear database fail.')
        
        SysLog(1, 'restore_backup.clear_db [%s] success'%(MAIN_DB_NAME))
        
        if self.copy_db(db_name, MAIN_DB_NAME):
            SysLog(3, 'restore_backup.copy_db from[%s]to[%s] success'%(db_name, MAIN_DB_NAME))
            return Result('ok')
        else:
            SysLog(1, 'restore_backup.copy_db from[%s]to[%s] fail'%(db_name, MAIN_DB_NAME))
            return Result('', RESTORE_DATABASE_FAIL_ERR, 'restore database fail.')
        
        
            
# --------------- data export begin ---------------------------------------- #

def ExportAllData(export_folder):
    db = CommonDB(MAIN_DB_NAME, [])
    table_list = [
        IDENTITY_TABLE,
        USER_TABLE,
        GROUP_TABLE,
        REPOSITORY_TABLE,
        NAMESPACE_TABLE,
        COMMENT_TABLE,
        TAG_TABLE,
        IMAGE_TABLE,
        LAYER_TABLE,
        LAYER_IMAGE_TABLE,
        USER_GROUP_TABLE,
        GROUP_NAMESPACE_TABLE,
        EDITRECORD_TABLE,
        STORAGE_TABLE,
        SMTP_TABLE,
        EMAIL_TABLE,
        LOG_TABLE,
        LDAP_TABLE,
        NOTIFICATION_TABLE,
        PULL_EVENT_TABLE,
        PUSH_EVENT_TABLE,
        SCHEDULE_TABLE,
        CONFIG_TABLE
    ]
    db.export_data(table_list, export_folder)
    
def ImportData(import_folder):
    db = CommonDB(MAIN_DB_NAME, [])
    return db.import_data_from_folder(import_folder)
    
            
            
            
