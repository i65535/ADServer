# -*- coding: utf-8 -*-
#!/usr/bin/env python
# Copyright (c) 20016-2016 The i65535.
# See LICENSE for details.
'''
Created on 2016年6月12日

@author: i65535
'''
"""
Image表数据变化
{
   "_id": "sha256:873c7a51543f4ea492cd6e554e185e36dbe6c7fcfd2267363d0b5be57031edf9",
   "user_id": "tao.li",
   "repository": "u1/centos",
   "pull_num": NumberInt(2),
   "config": "sha256:88676f551fd4e462155093ddc1fe5c97a44e21da6fb0b5ef688a9b294f31a216",
   "size": NumberInt(70541245)
}   

{
   "_id": "sha256:f4906f281b59bdb2860bcfc86f423a89493d9a9dfb5bcc149952e7c3e6c8718f",
   "user_id": "admin",
   "addr": "2d50c28401ca:5002",
   "repository": "test12/ubuntu",
   "pull_num": NumberInt(0),
   "instanceID": "f1385366-cd40-4690-9ff2-492383cdde42",
   "config": "",
   "size": NumberInt(0)
}

now = {
   "_id": NumberInt(1031),
   "user_id": "admin",
   "repository": "jack/gitlab",
   "pull_num": NumberInt(2),
   "tag": "latest",
   "config": "sha256:06fefa4a91835e1482ddd0a34be92048d4f72048d0d80aaaf56a18885eb19684",
   "digest": "sha256:99e221d90aa6f21957652b5f57421ad960405eee98b31b97bbe1abdc0dbb253a",
   "size": NumberInt(377132391)
} 


--------------------------------------------------------------------------------------------
Tag表数据变化
{
   "_id": NumberInt(1062),
   "create_time": NumberLong(1462945548842),
   "digest": "sha256:451eb75f182d72c8cc9279e20b9f74a66cd354932c6315bd6b23df1f1825851e",
   "pull_num": NumberInt(0),
   "repository": "test09/ubuntu",
   "tag_name": "14.04.2"
}    
   

{
   "_id": NumberInt(1009),
   "create_time": NumberLong(1462968114031),
   "delete": NumberInt(0),
   "desc": "",
   "digest": "sha256:c7aa23a3fb0a9566e78b80003b89331d89c1eaad381f00eba7cff925c891b967",
   "docker_file": "",
   "repository": "apphouse/registry_ui",
   "source": "https://index.youruncloud.com/v2/apphouse/registry_ui/manifests/sha256:c7aa23a3fb0a9566e78b80003b89331d89c1eaad381f00eba7cff925c891b967",
   "tag_name": "0.8.6",
   "user_id": "admin"
}    


tags = {
   "_id": NumberInt(253),
   "create_time": NumberLong(1465718070436),
   "delete": NumberInt(0),
   "desc": "",
   "digest": "sha256:99e221d90aa6f21957652b5f57421ad960405eee98b31b97bbe1abdc0dbb253a",
   "docker_file": "",
   "is_new": false,
   "pull_num": NumberInt(2),
   "repository": "jack/gitlab",
   "source": "http://192.168.12.55:5000/v2/jack/gitlab/manifests/sha256:99e221d90aa6f21957652b5f57421ad960405eee98b31b97bbe1abdc0dbb253a",
   "tag_name": "latest",
   "update_time": NumberLong(1465728120343),
   "user_id": "admin"
}    
   

"""

import time

from common.util import NowMilli, RandomNumStr
from frame.Logger import Log
from frame.configmgr import GetSysConfig
from mongodb.dbconst import IMAGE_TABLE, LAYER_IMAGE_TABLE, ID
from mongoimpl.registry.imagedbimpl import ImageDBImpl
from mongoimpl.registry.layerdbimpl import LayerImageDBImpl
from mongoimpl.registry.repositorydbimpl import RepositoryDBImpl
from mongoimpl.registry.tagdbimpl import TagDBImpl


class Tag(object):
    def __init__(self):
        self.domain = GetSysConfig('registry_domain') or '127.0.0.1:5002'
        
        
    def upgrade(self):
        rlt = TagDBImpl.instance().read_record_list(projection=['repository', 'tag_name', 'source', 'digest', 'delete', 'update_time'])
        if not rlt.success:
            Log(1, 'Tag.upgrade fail,as[%s]'%(rlt.message))
            return False
        
        total = len(rlt.content)
        up = 0
        fail = 0
        for tag in rlt.content:
            if self.update_tag(tag):
                up += 1
            else:
                fail += 1
        
        Log(3, 'Tag upgrade success[%s],fail[%s],total[%s]'%(up, fail, total))
        return True
        
    def update_tag(self, tag):
        data = {}
        if 'source' not in tag or tag['source'].find(tag['digest']) == -1:
            data['source'] = "http://" + self.domain + '/v2/%s/manifests/%s'%(tag['repository'], tag['digest'])
        
        if 'delete' not in tag:
            data['delete'] = 0
            
        if 'update_time' not in tag:
            data['update_time'] = NowMilli()
            
        if data:
            rlt = TagDBImpl.instance().update({ID:tag[ID]}, data)
            if rlt.success:
                Log(3, 'update_tag[%s][%s]success.'%(tag['repository'], tag['tag_name']))
                return True
            else:
                Log(3, 'update_tag[%s][%s]fail.'%(tag['repository'], tag['tag_name']))
                return False
            
        return True


class Repository(object):
    '''
    classdocs
    '''
    def __init__(self):
        '''
        Constructor
        '''
        self.key = time.strftime("_%Y%m%d_",time.localtime())
        self.key += RandomNumStr(4)
    
    def backup_data(self):
        if ImageDBImpl.instance().is_exist({}):
            rlt = ImageDBImpl.instance().rename_cn(IMAGE_TABLE + self.key)
            if not rlt.success:
                Log(1, 'backup_data image fail,as[%s]'%(rlt.message))
                return False
            
        if LayerImageDBImpl.instance().is_exist({}):
            rlt = LayerImageDBImpl.instance().rename_cn(LAYER_IMAGE_TABLE + self.key)
            if not rlt.success:
                Log(1, 'backup_data Layer_Image fail,as[%s]'%(rlt.message))
                return False
        Log(3, 'backup_data success')
        
        return True
            
            
    
    def upgrade(self):
        if not self.backup_data():
            Log(1, 'Repository.upgrade fail.')
            return False
        
        self.upgrade_repo_data()
        
        return True
    
    
    def upgrade_repo_data(self):
        rlt = RepositoryDBImpl.instance().read_record_list(projection=[])
        if not rlt.success:
            Log(1, 'Repository.upgrade_repo_data read repository data fail,as[%s]'%(rlt.message))
            return False
        
        for repo in rlt.content:
            self.clear_repo_data(repo[ID])
            
        return True
            
            
    def clear_repo_data(self, repo_id):
        status = TagDBImpl.instance().repository_status(repo_id)
        Log(3,'[%s]status is [%s]'%(repo_id, str(status)))
        if status['total'] == 0:
            RepositoryDBImpl.instance().delete_repository(repo_id, True)
        elif status['normal'] == 0:
            RepositoryDBImpl.instance().delete_repository(repo_id, False)
        else:
            RepositoryDBImpl.instance().update({ID:repo_id}, {'empty':False})
    
    
    
    
    
    
    
    
    
    
    
