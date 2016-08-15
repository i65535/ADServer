# -*- coding: utf-8 -*-
# Copyright (c) 20016-2016 The i65535.
# See LICENSE for details.
"""
Implement event data manage
"""

import threading

from common.guard import LockGuard
from common.util import NowMilli
from frame.Logger import Log
from mongodb.dbbase import DBBase
from mongodb.dbconst import MAIN_DB_NAME, PULL_EVENT_TABLE, ID, PUSH_EVENT_TABLE


class PullEventDBImpl(DBBase):
    db = MAIN_DB_NAME
    collection = PULL_EVENT_TABLE
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
        
    def new_pull_event(self, event):
        if ID not in event:
            Log(1, 'new_pull_event fail,as must save to db first')
            return
        
        data = {}
        data['event_id'] = event[ID]
        data['repository'] = event['target']['repository']
        data['digest'] = event['target']['digest']
        data['tag'] = event['target']['tag']
        data['user_id'] = event.get('actor', {}).get('name', '')
        data['pull_time'] = NowMilli()
        return self.create(data)


class PushEventDBImpl(DBBase):
    db = MAIN_DB_NAME
    collection = PUSH_EVENT_TABLE
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
        
    def new_push_event(self, event):
        if ID not in event:
            Log(1, 'new_pull_event fail,as must save to db first')
            return
        
        repository = event['target']['repository']
        digest = event['target']['digest']
        tag = event['target']['tag']
        
        data = {}
        data['event_id'] = event[ID]
        data['repository'] = repository
        data['digest'] = digest
        data['tag'] = tag
        data['user_id'] = event.get('actor', {}).get('name', '')
        data['push_time'] = NowMilli()
        return self.create(data)
    
