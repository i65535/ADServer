# -*- coding: utf-8 -*-
# Copyright (c) 20016-2016 The i65535.
# See LICENSE for details.
"""
Implement Order data manage
"""

import threading

from common.guard import LockGuard
from common.util import NowMilli, Result
from frame.Logger import Log
from frame.errcode import TAG_NOT_EXIST_ERR
from mongodb.dbbase import DBBase
from mongodb.dbconst import MAIN_DB_NAME, TAG_TABLE, ID


class TagDBImpl(DBBase):
    db = MAIN_DB_NAME
    collection = TAG_TABLE
    __lock = threading.Lock()
    
    @classmethod
    def instance(cls):
        '''
        Limits application to single instance
        '''
        with LockGuard(cls.__lock):
            if not hasattr(cls, "_instance"):
                cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        DBBase.__init__(self, self.db, self.collection)
    
    def create_new_tag(self, user_id, repository, tag_name, source, digest):
        """
        """
        # 如果记录已经存在，则直接将记录置为未删除状态
        if self.is_exist({'repository':repository, 'digest':digest, 'tag_name':tag_name}):
            self.update({'repository':repository, 'digest':digest, 'tag_name':tag_name}, {'delete':0, 'create_time':NowMilli()})
            Log(3, 'create_new_tag[%s][%s][%s]fail,as the tag exist already.'%(repository, tag_name, digest))
            return False
        
        # 如果tag已经存在，则说明用户用一个新的image覆盖了原image
        rlt = self.read_record_data({'repository':repository, 'tag_name':tag_name})
        if rlt.success:
            tag = rlt.content
            Log(2, 'recover old image[%s][%s][%s]'%(repository, tag_name, tag['digest']))
            tag['user_id'] = user_id
            tag['digest'] = digest
            tag['source'] = source
            tag['delete'] = 0
            tag['create_time'] = NowMilli()
            tag['is_new'] = True
            _id = tag.pop(ID)
            self.update({ID:_id}, tag)
            tag[ID] = _id
            return tag
        
        """
        # 给Image重复打Tag，最后一个有效
        rlt = self.read_record_data({'repository':repository, 'digest':digest})
        if rlt.success:
            self.update({ID:rlt.content[ID]}, {'delete':0, 'tag_name':tag_name, 'is_new': True, 'create_time':NowMilli()})
            WebLog(3, 'user set tag name[%s]for[%s][%s].'%(tag_name, repository, digest))
            rlt.content['tag_name'] = tag_name
            return rlt.content
        """
        
        # 将is_new设为True，解决读不到size的问题，
        tag = {
            'repository': repository,
            'tag_name': tag_name,
            'is_new': True,
            'user_id': user_id,
            "digest": digest,
            'create_time': NowMilli(),
            'desc': '',
            'docker_file': '',
            'source': source,
            'pull_num': 0,
            'delete': 0}

        rlt = self.create(tag)
        if not rlt.success:
            Log(1, 'create_new_tag fail,as[%s]'%(rlt.message))
            return False
        return tag

    
    def update_tag_by_id(self, _id, info):
        _id = int(_id)
        info.pop(ID, None)
        info['update_time'] = NowMilli()
        rlt = self.update({ID:_id}, info)
        if not rlt.success:
            Log(1, 'update_tag fail,as[%s]'%(rlt.message))

        return rlt
            
    def update_tag(self, _id, info):
        _id = int(_id)
        info.pop(ID, None)
        info['update_time'] = NowMilli()
        rlt = self.update({ID:_id}, info)
        if not rlt.success:
            Log(1, 'update_tag fail,as[%s]'%(rlt.message))

        return rlt
            
    def is_tag_exist(self, repository, tag_name, digest=''):
        """
        # digest 指向一个文件，和repository无关，只要内容一样，digest值就是一样的
        """
        query = {'repository':repository, 'tag_name':tag_name}
        if digest:
            query['digest'] = digest
            
        rlt = self.count(query)
        if rlt.success and rlt.content > 0:
            return True
        return False
        
    def delete_lost_tags(self, repository, tags):
        """
        # 如果tag为空，则删除已有的标签
        # 此处删除，只能删除标记为未删除的tag
        """
        if not tags:
            return self.remove({'repository':repository, 'delete':0})
        
        rlt = self.read_record_list({'repository':repository, 'delete':0}, projection=['tag_name'])
        if not rlt.success:
            Log(1, 'upsert_tags.read_record_list fail,as[%s]'%(rlt.message))
            return rlt
        
        local_tags = []
        lost_tags = []
        for tag in rlt.content:
            local_tags.append(tag['tag_name'])
            if tag['tag_name'] not in tags:
                lost_tags.append(tag[ID])

        if len(lost_tags) > 0:
            rlt = self.remove({ID:{'$in':lost_tags}})
            if rlt.success:
                Log(3, 'upsert_tags update [%s] old record'%(rlt.content) )
            else:
                Log(1, 'upsert_tags update record fail,as[%s]'%(rlt.message) )
                
        return Result(len(lost_tags))
        
    def get_tag_info(self, repo_name, tag_name):
        return self.read_record_data({'repository':repo_name, 'tag_name':tag_name})
    
    
    def get_tag_info_by_id(self, tag_id):
        return self.read_record(tag_id, projection=['repository', 'tag_name', 'digest'])
        

            
    def update_dockfile(self, query, dock_file_ct):
        if not self.is_exist(query):
            return Result('', TAG_NOT_EXIST_ERR, 'Tag not exist')
        
        rlt = self.update(query, {'docker_file':dock_file_ct})
        if not rlt.success:
            Log(1, 'update_dockfile fail,as[%s]'%(rlt.message))

        return rlt
            
    def delete_tag(self, tag_id, force=False):
        if force:
            return self.remove({ID:tag_id})
        else:
            return self.update({ID:tag_id}, {'delete':NowMilli()})
    
    
    def read_all_new_tag(self):
        rlt = self.read_record_list({'is_new':True})
        if rlt.success:
            return rlt.content
        return []
    
    def set_checked(self, tag_id):
        return self.update({ID:tag_id}, {'is_new':False})
        
    def tag_num(self, repository, digest):
        rlt = self.count({'repository':repository, 'digest':digest, 'delete': 0})
        if not rlt.success:
            Log(1, 'tag_num.count fail,as[%s]'%(rlt.message))
            return 0
        return rlt.content
        
    def add_pull_num(self, repository, digest, tag_name):
        return self.find_and_modify_num({'repository':repository, 'tag_name':tag_name, 'digest':digest}, {'pull_num':1})    
            
            
    def get_tag_list(self, tag_id_list):
        rlt = self.read_record_list({ID:{'$in':tag_id_list}, 'delete':{'$ne':0}}, projection=['repository', 'tag_name', 'digest'])
        if not rlt.success:
            Log(1, 'get_tag_list.read_record_list fail,as[%s]'%(rlt.message))
            return []
        else:
            return rlt.content
        
    def get_all_del_tags(self):
        rlt = self.read_record_list({'delete':{'$ne':0}}, projection=['repository', 'tag_name', 'digest'])
        if not rlt.success:
            Log(1, 'get_all_del_tags.read_record_list fail,as[%s]'%(rlt.message))
            return []
        else:
            return rlt.content    
        
    def repository_status(self, repository):
        data = {'total':0, 'normal':0, 'delete':0}
        rlt = self.count({'repository':repository})
        if rlt.success:
            data['total'] = rlt.content
            
        rlt = self.count({'repository':repository, 'delete':0})
        if rlt.success:
            data['normal'] = rlt.content
            
        data['delete'] = data['total'] - data['normal']
        return data
        
    def is_recycle_bin_empty(self):
        rlt = self.count({'delete':{'$ne':0}})
        if not rlt.success:
            Log(1, 'query is_recycle_bin_empty fail,as[%s]'%(rlt.message))
            return False
        
        if rlt.content == 0:
            Log(3, 'recycle bin empty')
            return True
        else:
            Log(2, 'recycle bin not empty [%s]'%(rlt.content))
            return False
        
        
          
        