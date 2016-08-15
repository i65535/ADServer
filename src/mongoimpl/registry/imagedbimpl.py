# -*- coding: utf-8 -*-
# Copyright (c) 20016-2016 The i65535.
# See LICENSE for details.
"""
Implement Order data manage
"""

import threading

from common.guard import LockGuard
from frame.Logger import Log
from mongodb.dbbase import DBBase
from mongodb.dbconst import MAIN_DB_NAME, IMAGE_TABLE, ID


class ImageDBImpl(DBBase):
    db = MAIN_DB_NAME
    collection = IMAGE_TABLE
    __lock = threading.Lock()
    
    @classmethod
    def instance(cls):
        with LockGuard(cls.__lock):
            if not hasattr(cls, "_instance"):
                cls._instance = cls()
        return cls._instance
    
    
    def __init__(self):
        DBBase.__init__(self, self.db, self.collection)
        
            
    def is_image_exist(self, repository, digest):
        """
        # digest 指向一个文件，和repository无关，只要内容一样，digest值就是一样的
        """
        rlt = self.count({'digest':digest, 'repository':repository})
        if rlt.success and rlt.content>0:
            return True
        return False       
            
    def create_image(self, repository, image, user_id, digest, tag_name):
        size = 0
        for layer in image['fsLayers']:
            if 'size' in layer:
                size += layer['size']
        
        data = {'repository':repository, 
                'digest':digest, 
                'user_id': user_id, 
                'size': size, 
                'config': image['config'].get('digest',''), 
                'tag': tag_name,
                'pull_num':0}
        rlt = self.create(data)
        if not rlt.success:
            Log(1, 'create_image repository[%s]digest[%s]fail'%(repository, digest))
        return rlt
            
            
    def add_pull_num(self, repository, digest):
        return self.find_and_modify_num({'digest':digest, 'repository':repository}, {'pull_num':1})
        
            
            
    def get_image_info(self, repository, digest):
        rlt = self.read_record_data({'repository':repository, 'digest':digest})
        if rlt.success:
            return rlt.content
        else:
            Log(1, 'get_image_info[%s] fail,as[%s]'%(digest, rlt.message))
            return {}
        
        
    def delete_image(self, repository, digest):
        rlt = self.remove({'repository':repository, 'digest':digest})
        if not rlt.success:
            Log(1, 'delete_image[%s][%s]fail,as[%s]'%(repository, digest, rlt.message))
        return rlt
                  
    def update_tag_name(self, image_id, tag_name):
        rlt = self.update({ID:image_id}, {'tag':tag_name})
        if not rlt.success:
            Log(1, 'update_tag_name[%s][%s]fail,as[%s]'%(image_id, tag_name, rlt.message))
        return rlt
        
        