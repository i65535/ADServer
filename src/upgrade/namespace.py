# -*- coding: utf-8 -*-
#!/usr/bin/env python
# Copyright (c) 20016-2016 The i65535.
# See LICENSE for details.
'''
Created on 2016年6月12日

@author: i65535
'''

from frame.Logger import Log
from mongodb.dbconst import ID, NAMESPACE_TYPE_ORGANIZATION, \
    NAMESPACE_TYPE_PERSONAL
from mongoimpl.registry.namespacedbimpl import NamespaceDBImpl
from mongoimpl.registry.userdbimpl import UserDBImpl


class Namespace(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
    
    def upgrade(self):
        rlt = NamespaceDBImpl.instance().read_record_list()
        if not rlt.success:
            Log(1, 'Namespace.upgrade fail,as[%s]'%(rlt.message))
            return False
        total = len(rlt.content)
        up = 0
        fail = 0
        for npc in rlt.content:
            if 'type' not in npc:
                if self.set_npc_type(npc):
                    up += 1
                else:
                    fail += 1
        
        Log(3, 'namespace upgrade success[%s],fail[%s],total[%s]'%(up, fail, total))
        return True
                
    def set_npc_type(self, npc):
        if UserDBImpl.instance().is_exist({ID:npc[ID]}):
            data = {'type':NAMESPACE_TYPE_PERSONAL, 'owner_id':npc[ID]}
        else:
            data = {'type':NAMESPACE_TYPE_ORGANIZATION, 'owner_id':''}
            
        rlt = NamespaceDBImpl.instance().update({ID:npc[ID]}, data)
        if rlt.success:
            Log(3, 'upgrade namespace[%s]success'%(npc[ID]))
            return True
        else:
            Log(1, 'upgrade namespace[%s]fail'%(npc[ID]))
            return False
            
            
        