# -*- coding: utf-8 -*-
# Copyright (c) 20016-2016 The i65535.
# See LICENSE for details.


import threading

from common.guard import LockGuard
from common.util import NowMilli, Result
from frame.Logger import Log
from mongodb.dbbase import DBBase
from mongodb.dbconst import MAIN_DB_NAME, LAYER_TABLE, ID, LAYER_IMAGE_TABLE


class LayerDBImpl(DBBase):
    """
    Layer 表仅保存层的信息，层与镜像的关系保存在Layer_Image
    """
    
    db = MAIN_DB_NAME
    collection = LAYER_TABLE
    __lock = threading.Lock()
    
    @classmethod
    def instance(cls):
        with LockGuard(cls.__lock):
            if not hasattr(cls, "_instance"):
                cls._instance = cls()
        return cls._instance
    
    
    def __init__(self):
        DBBase.__init__(self, self.db, self.collection)
        
    def save_layer_info(self, image_info, digest):
        """
        # 这个函数根据完整的layer信息创建，更新记录
        # "fsLayers": [
        #  {
        #     "mediaType": "application/vnd.docker.image.rootfs.diff.tar.gzip",
        #     "size": 674258,
        #     "digest": "sha256:55dc925c23d1ed82551fd018c27ac3ee731377b6bad3963a2a4e76e753d70e57"
        #  }]
        """
        id_list = []
        arr = []
        for layer in image_info['fsLayers']:
            layer[ID] = layer.pop('digest','')
            if layer[ID] in id_list:
                continue
            
            if not self.is_exist({ID:layer[ID]}):
                id_list.append(layer[ID])
                layer['image_id'] = digest
                arr.append(layer)
        if arr:
            rlt = self.batch_insert(arr)
            if not rlt.success:
                Log(1, "LayerDBImpl save_layer_info fail,as[%s]"%(rlt.message))
        
            
    def add_layer_pull_num(self, digest):
        self.find_and_modify_num({ID:digest}, {'pull_num':1}, True)
            
            
            
class LayerImageDBImpl(DBBase):
    db = MAIN_DB_NAME
    collection = LAYER_IMAGE_TABLE
    __lock = threading.Lock()
    
    @classmethod
    def instance(cls):
        with LockGuard(cls.__lock):
            if not hasattr(cls, "_instance"):
                cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        DBBase.__init__(self, self.db, self.collection)       
            
    def save_relation(self, repository, image_digest, layers):
        if self.is_exist({'repository':repository, 'image':image_digest}):
            self.update_relation(repository, image_digest, layers)
        else:
            self.create_relation(repository, image_digest, layers)
                
    def create_relation(self, repository, image_digest, layers):
        tmp = []
        arr = []
        for layer in layers:
            digest = layer.get('digest','')
            if digest and digest not in tmp:
                arr.append({'repository':repository, 'image':image_digest, 'layer':digest})
                tmp.append(digest)
        
        if len(arr) == 0:
            Log(1, 'create_relation insert 0 record')
            return Result(0)
        
        rlt = self.batch_insert(arr)
        if rlt.success:
            Log(1, 'create_relation.batch_insert[%s][%s]record'%(rlt.content, len(arr)))
        else:
            Log(1, 'create_relation.batch_insert fail,as[%s]'%(rlt.message))
        return rlt
            
                
    def update_relation(self, repository, image_digest, layers):
        tmp = []
        for layer in layers:
            digest = layer.get('digest','')
            if digest and digest not in tmp:
                self.update({'repository':repository, 'image':image_digest, 'layer':digest}, {'link_time':NowMilli()}, True)
                tmp.append(digest)
            else:
                Log(1, 'update_relation find invalid layer digest[%s]'%(digest))
        
        return Result('update')
                
        
    def link_number(self, repository, layer_digest):
        rlt = self.count({'repository':repository, 'layer':layer_digest})
        if not rlt.success:
            Log(1, 'tag_num.count fail,as[%s]'%(rlt.message))
            return 0
        return rlt.content
    
    def delete_link(self, repository, image_digest):
        rlt = self.remove({'repository':repository, 'image':image_digest})
        if not rlt.success:
            Log(1, 'delete_link.remove[%s][%s] fail.as[%s]'%(repository, image_digest, rlt.message))
        return rlt
                    
                
    def image_layers(self, repository, image_digest):
        rlt = self.read_record_list({'repository':repository, 'image':image_digest})
        if rlt.success:
            return rlt.content
        Log(1, 'image_layers.read_record_list fail,as[%s]'%(rlt.message))
        return []
            
            
        