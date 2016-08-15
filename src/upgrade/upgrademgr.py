# -*- coding: utf-8 -*-
#!/usr/bin/env python
# Copyright (c) 20016-2016 The i65535.
# See LICENSE for details.
'''
Created on 2016年6月12日

@author: i65535
'''

from common.util import Result, GetDynamicClass
from frame.Logger import SysLog, WebLog
from frame.errcode import UPGRADE_FAIL_ERR
from frame.generalmgr import GeneralMgr
from mongodb.commondb import CommonDB, Tables
from mongodb.dbconst import APP_HOUSE_VERSION, MAIN_DB_NAME
from mongoimpl.setting.configdbimpl import ConfigDBImpl
from upgrade.namespace import Namespace
from upgrade.repository import Tag, Repository


class UpgradeMgr(object):
    '''
    # implement app house upgrade 
    '''


    def __init__(self):
        '''
        Constructor
        '''
    
    def upgrade(self):
        if self.upgrade_to_latest_version():
            ConfigDBImpl.instance().set_version(APP_HOUSE_VERSION)
            WebLog(3, 'upgrade to[latest version]success')
            return Result('upgrade success')
        else:
            WebLog(1, 'upgrade fail.')
            return Result('', UPGRADE_FAIL_ERR, 'upgrade fail')
        
    def is_latest_version(self):
        current = ConfigDBImpl.instance().get_version()
        SysLog(3, 'UpgradeMgr.current version is[%s]'%(current))
        return APP_HOUSE_VERSION == current
    
    def upgrade_to_latest_version(self):
        npc = Namespace()
        if not npc.upgrade():
            SysLog(1, 'upgrade_to_latest_version [Namespace] upgrade fail.')
            return False
        
        tag = Tag()
        if not tag.upgrade():
            SysLog(1, 'upgrade_to_latest_version [Tag] upgrade fail.')
            return False
        
        repo = Repository()
        if not repo.upgrade():
            SysLog(1, 'upgrade_to_latest_version [Repository] upgrade fail.')
            return False
        
        return True

    def upgrade_general_setting(self):
        rlt = ConfigDBImpl.instance().get_general_info()
        if rlt.success:
            SysLog(1,'upgrade_general_setting set general info')
            GeneralMgr.instance().set_general(rlt.content)
        else:
            SysLog(1,'upgrade_general_setting get general info fail.')
           
        # 读取端口号 
        GeneralMgr.instance().init_general_setting()
        
        return True


    
def init_app_house_data(force=False, clear_db=False):
    cloud_db = CommonDB(MAIN_DB_NAME,Tables)
    if force or not cloud_db.is_installed():
        return cloud_db.setup(clear_db)
    
    current = ConfigDBImpl.instance().get_version()
    if APP_HOUSE_VERSION == current:
        SysLog(3, 'UpgradeMgr.current is latest version [%s]'%(current))
        return
    
    if current in ['', '1.0.3']:
        u = UpgradeMgr()
        cloud_db.setup()
        return u.upgrade()
    
    else:
        file_name = 'upgrade' + current.replace('.', '')
        handler = GetDynamicClass('UpgradeHandler', file_name, 'upgrade')
        if handler:
            u = handler()
            return u.upgrade()
        else:
            SysLog(3, 'no support this version[%s] upgrade'%(current))
            return Result(current)
    
    
    
        
    
    
        