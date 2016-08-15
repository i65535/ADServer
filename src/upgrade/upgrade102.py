# -*- coding: utf-8 -*-
#!/usr/bin/env python
# Copyright (c) 20016-2016 The i65535.
# See LICENSE for details.
'''
Created on 2016年6月12日

@author: i65535
'''

from common.util import Result
from frame.Logger import SysLog, WebLog
from mongodb.commondb import CommonDB
from mongodb.dbconst import APP_HOUSE_VERSION, MAIN_DB_NAME, EXTENSTION_TABLE, \
    TASK_TABLE, SUB_TASK_TABLE, SYNCTASK, WORK_DATA_TABLE
from mongoimpl.setting.configdbimpl import ConfigDBImpl


class UpgradeHandler(object):
    '''
    # implement upgrade from 1.0.2
    '''


    def __init__(self):
        '''
        Constructor
        '''
    
    def upgrade(self):
        SysLog(3, 'upgrade from 1.0.2')
        tables= {
             EXTENSTION_TABLE:None, 
             TASK_TABLE:None, 
             SUB_TASK_TABLE:None, 
             SYNCTASK:None, 
             WORK_DATA_TABLE:None
        }
        
        cloud_db = CommonDB(MAIN_DB_NAME,tables)
        cloud_db.add_all_identity_key()
        
        ConfigDBImpl.instance().set_version(APP_HOUSE_VERSION)
        WebLog(3, 'upgrade to last version[%s]success'%(APP_HOUSE_VERSION))
        return Result('upgrade success')

        


    
    
    
        
    
    
        