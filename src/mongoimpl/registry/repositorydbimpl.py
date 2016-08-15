# -*- coding: utf-8 -*-
# Copyright (c) 20016-2016 The i65535.
# See LICENSE for details.
"""
Implement Order data manage
"""

import threading

from common.guard import LockGuard
from common.util import NowMilli, Result, ParseNamespace
from frame.Logger import Log
from mongodb.dbbase import DBBase
from mongodb.dbconst import MAIN_DB_NAME, REPOSITORY_TABLE, ID, \
    PERMISSION_PUBLIC, DEFAULT_NAMESPACE


class RepositoryDBImpl(DBBase):
    db = MAIN_DB_NAME
    collection = REPOSITORY_TABLE
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
        
    def is_repository_exsit(self, repository):
        rlt = self.count({ID: repository})
        if rlt.success and rlt.content>0:
            return True
        return False
    
    def save_repository(self, namespace, repository, user_id):
        rlt = self.count({ID: repository})
        if rlt.success and rlt.content>0:
            self.update({ID: repository}, {'push_time':NowMilli(), 'dirty':True, 'empty':False})
            return rlt
        
        t = NowMilli()
        data = {ID:repository, 
                'create_time':t,
                'push_time':t,
                'permission':PERMISSION_PUBLIC, 
                'delete':0, 
                'desc':'', 
                'namespace':namespace,
                'dirty':True,
                'empty':False,
                'user_id':user_id,
                'pull_num':0}
        rlt = self.insert(data)
        if not rlt.success:
            Log(1, 'save_repository[%s]fail,as[%s]'%(rlt.content))
        return rlt
    
    def read_all_dirty_repo(self):
        rlt = self.read_record_list({'dirty':True}, projection=['user_id'])
        if not rlt.success:
            Log(1, 'read_all_dirty_repo fail,as[%s]'%(rlt.content))
            return []
        return rlt.content
        
    def upsert_repository(self, repositories):
        if len(repositories) == 0:
            return
        
        rlt = self.read_record_list(projection=[])
        if not rlt.success:
            Log(1, 'upsert_repository.read_record_list fail,as[%s]'%(rlt.message))
            return rlt
        
        local_repos = []
        new_repos = []
        lost_repos = []
        for repo in rlt.content:
            local_repos.append(repo[ID])
            if repo[ID] not in repositories:
                lost_repos.append(repo[ID])
        
        for repo in repositories:
            if repo not in local_repos:
                npc = ParseNamespace(repo, DEFAULT_NAMESPACE)
                new_repos.append({ID:repo, 'push_time':NowMilli(), 'create_time':NowMilli(), 'permission':PERMISSION_PUBLIC, 'delete':0, 'desc':'', 'empty':False, 'namespace':npc, 'dirty':True})

        if len(new_repos) > 0:
            rlt = self.batch_insert(new_repos)
            if rlt.success:
                Log(3, 'upsert_repository insert [%s] new record'%(rlt.content) )
            else:
                Log(1, 'upsert_repository insert record fail,as[%s]'%(rlt.message) )
        
        if len(lost_repos) > 0:
            rlt = self.updates({ID:{'$in':lost_repos}}, {'delete':NowMilli()})
            if rlt.success:
                Log(3, 'upsert_repository update [%d] old record'%(rlt.content) )
            else:
                Log(1, 'upsert_repository update record fail,as[%s]'%(rlt.message) )
                
        return Result(len(new_repos) + len(lost_repos))
        
        
    def list_repository(self, namespace='', user_id=''):
        query = {}
        if namespace:
            query['namespace'] = namespace
            #reg = '^%s\/'%(namespace)
            #return self.read_record_list({namespace:{'$regex':reg, '$options': 'i'}})
        if user_id:
            query['user_id'] = user_id
        return self.read_record_list(query)

        
    def read_repo_info(self, repo_name):
        return self.read_record(repo_name)
    
    def get_repo_num(self, namespace):
        rlt = self.count({'namespace':namespace})
        if rlt.success:
            return rlt.content
        return 0
    
    def copy_repository(self, source_repo_id, namespace, target_repo, user_id):
        rlt = self.count({ID: target_repo})
        if rlt.success and rlt.content>0:
            return rlt
        
        rlt = self.read_record(source_repo_id)
        if not rlt.success:
            Log(1, 'copy_repository fail,as find source repository fail.')
            return rlt
        
        new_repo = rlt.content
        new_repo[ID] = target_repo
        new_repo['push_time'] = NowMilli()
        new_repo['create_time'] = NowMilli()
        new_repo['namespace'] = namespace
        new_repo['user_id'] = user_id
        new_repo['dirty'] = True
        new_repo['empty'] = False
        new_repo['pull_num'] = 0

        rlt = self.insert(new_repo)
        if not rlt.success:
            Log(1, 'copy_repository[%s]fail,as[%s]'%(rlt.content))
        return rlt 
            
    def set_clean(self, repository) :
        return self.update({ID:repository},{'dirty':False})
    
    def add_pull_num(self, repository):
        return self.find_and_modify_num({ID:repository}, {'pull_num':1})
    
    def query_repo_ids(self, namespaces):
        if len(namespaces) == 0:
            return []
        rlt = self.read_record_list({'namespace':{'$in':namespaces}}, projection=[])
        if not rlt.success:
            return []
        
        arr = []
        for record in rlt.content:
            arr.append(record[ID])
        
        return arr
    
    def delete_repository(self, repository, force=False):
        if force:
            return self.remove({ID:repository})
        else:
            return self.update({ID:repository}, {'empty':True})
    
    def restore_reposiroty(self, repositories):
        if isinstance(repositories, list):
            return self.update({ID: {'$in':repositories}, 'empty':True}, {'empty':False})
        else:
            return self.update({ID:repositories, 'empty':True}, {'empty':False})
            
        
            
            
            
            
            
            
            
            
        