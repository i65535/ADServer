# -*- coding: utf-8 -*-
'''
Created on 2016年5月16日

@author: i65535
'''
import time

from frame.Logger import Log
from frame.authen import ring0
from mongoimpl.registry.repositorydbimpl import RepositoryDBImpl


class Statistics(object):
    '''
    # 实现统计的功能
    '''

    def __init__(self):
        '''
        Constructor
        '''
    
    @ring0
    def popularTags(self, top=8):
        rlt = RepositoryDBImpl.instance().exec_db_script('popularTags', top)
        if not rlt.success:
            Log(1, 'Statistics.popularTags fail,as[%s]'%(rlt.message))
        
        return rlt
    
    @ring0
    def registryCounter(self, mod='day'):
        now = int(time.time())
        second = 24 * 60 * 60
        if mod == 'day':
            timestamp = now - now%second
        elif mod == 'week':
            timestamp = now - second * 7
        elif mod == 'month':
            timestamp = now - second * 30
        
        timestamp *= 1000
        rlt = RepositoryDBImpl.instance().exec_db_script('registryCounter', timestamp)
        if not rlt.success:
            Log(1, 'Statistics.registryCounter fail,as[%s]'%(rlt.message))
        
        return rlt
    
    
    
    
    
    
    
    
    
    
    
    
