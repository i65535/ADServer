# -*- coding: utf-8 -*-
# Copyright (c) 20016-2016 The i65535.
# See LICENSE for details.
import base64
import json

from api.emailmgr import EmailMgr
from common.timer import Timer
from common.util import Result
from frame.Logger import Log, WebLog
from frame.authen import ring0, ring3, ring5
from frame.configmgr import GetSysConfig
from frame.errcode import INVALID_JSON_DATA_ERR, TEST_LDAP_AUTH_FAIL_ERR, \
    LDAP_SERVER_INFO_INVALID_ERR, LDAP_TEST_ACCOUNT_INVALID_ERR, \
    INVALID_AUTH_METHOD_ERR
from frame.generalmgr import GeneralMgr
from frame.ldapclient import LDAPClient
from mongodb.dbconst import AUTH_LOCAL, AUTH_LDAP, LOCAL_FILE_SYSTEM, ID
from mongoimpl.setting.configdbimpl import ConfigDBImpl
from mongoimpl.setting.emaildbimpl import EmailDBImpl
from mongoimpl.setting.ldapdbimpl import LDAPDBImpl
from mongoimpl.setting.smtpdbimpl import SMTPDBImpl
from mongoimpl.setting.storagedbimpl import StorageDBImpl


class SettingMgr(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.timer = None
        self.emailmgr = None
        self.init_email()
        
            
    def init_email(self):
        self.emailmgr = EmailMgr.new_email_manager()
        if not self.emailmgr:
            WebLog(1, 'init email manager fail.')
            return
        
        if self.timer is None:
            self.timer = Timer(45, self.emailmgr, 'SendEmail')
            self.timer.start()
    
    
    def reload_general(self, info):
        """
        # domain_name: '',
        # http_port: 80,
        # https_port: 443,
        # ssl_crt: '',
        # ssl_key: '',
        """         
        rlt = GeneralMgr.instance().set_general(info)
        if not rlt:
            Log(1, 'set general info file fail.')
        
        return rlt 

    @ring0
    def storages(self):
        rlt = StorageDBImpl.instance().all_storage_type()
        if not rlt.success:
            Log(1, 'Storage.read_record_list fail,as[%s]'%(rlt.message))
            return rlt

        storage_type = ConfigDBImpl.instance().get_storage_type(LOCAL_FILE_SYSTEM)
        for store in rlt.content:
            if storage_type == store.get('_id',''):
                store['active'] = True
            else:
                store['active'] = False
        return rlt
    
    @ring0
    def update_storage(self, post_data):
        try:
            store = json.loads(post_data.replace("'", '"'))
        except Exception,e:
            Log(1,"update_storage.parse data to json fail,input[%s]"%(post_data))
            return Result('',INVALID_JSON_DATA_ERR,str(e))
        
        rlt = StorageDBImpl.instance().update_store(store)
        if rlt.success:
            ConfigDBImpl.instance().set_storage_type(rlt.content)
        return rlt
        
    
    @ring0
    def smtp(self):
        rlt = SMTPDBImpl.instance().default_smtp()
        if not rlt.success:
            Log(1, 'smtp.read_record_list fail,as[%s]'%(rlt.message))

        return rlt
        
    
    @ring0
    def update_smtp(self, post_data):
        try:
            smtp = json.loads(post_data.replace("'", '"'))
        except Exception,e:
            Log(1,"update_smtp.parse data to json fail,input[%s]"%(post_data))
            return Result('',INVALID_JSON_DATA_ERR,str(e))
        
        rlt = SMTPDBImpl.instance().update_smtp_info(smtp)
        if rlt.success:
            WebLog(3, 'Admin updated the email setting.')
            self.init_email()
        else:
            Log(1, 'update_smtp fail,as[%s]'%(rlt.message))
        return rlt

    @ring0
    def update_generalsetting(self, post_data):
        try:
            info = json.loads(post_data.replace("'", '"'))
        except Exception,e:
            Log(1,"update_general.parse data to json fail,input[%s]"%(post_data))
            return Result('',INVALID_JSON_DATA_ERR,str(e))
        
        rlt = ConfigDBImpl.instance().set_general_info(info)
        if rlt.success:
            self.reload_general(info)
            WebLog(3, 'Admin updated the general setting!')
        else:
            Log(1, 'update general setting fail,as[%s]'%(rlt.message))
        return rlt

    @ring0
    def generalsetting(self):
        rlt = ConfigDBImpl.instance().get_general_info()
        if rlt.success:
            rlt.content.pop(ID, '')
            return rlt

        info = GeneralMgr.instance().init_general_setting()
        if info:
            return Result(info)
        else:
            Log(1, 'get_general fail,as[%s]'%(rlt.message))
        return rlt
                        
    @ring0
    def authorize(self):
        method = ConfigDBImpl.instance().get_auth_method(AUTH_LOCAL)
        
        rlt = LDAPDBImpl.instance().default_ldap()
        if not rlt.success:
            Log(1, 'ldap.read_record_list fail,as[%s]'%(rlt.message))
            return rlt
        
        WebLog(3, 'Admin updated the auth type to %s.'%(method))
        rlt.content['auth'] = method
        return rlt
    
    @ring0
    def update_authorize(self, post_data):
        try:
            info = json.loads(post_data.replace("'", '"'))
        except Exception,e:
            Log(1,"update_ldap.parse data to json fail,input[%s]"%(post_data))
            return Result('',INVALID_JSON_DATA_ERR,str(e))
        
        method = info.get('auth', AUTH_LOCAL)
        if method not in [AUTH_LOCAL, AUTH_LDAP]:
            return Result('', INVALID_AUTH_METHOD_ERR, 'invalid auth method')
        
        rlt = ConfigDBImpl.instance().set_auth_method(method)
        if not rlt.success:
            return rlt
        
        if method == AUTH_LOCAL:
            return rlt
        
        info.pop('test_user_name', '')
        info.pop('test_password', '')
        rlt = LDAPDBImpl.instance().update_ldap_info(info)
        if not rlt.success:
            Log(1, 'update_ldap fail,as[%s]'%(rlt.message))
        return rlt

    @ring0
    def update_ldap(self, post_data):
        try:
            ldap = json.loads(post_data.replace("'", '"'))
        except Exception,e:
            Log(1,"update_ldap.parse data to json fail,input[%s]"%(post_data))
            return Result('',INVALID_JSON_DATA_ERR,str(e))
        
        rlt = LDAPDBImpl.instance().update_ldap_info(ldap)
        if not rlt.success:
            Log(1, 'update_ldap fail,as[%s]'%(rlt.message))
        return rlt
    
    @ring0
    def test_ldap_connect(self, post_data):
        try:
            user_info = json.loads(post_data.replace("'", '"'))
        except Exception,e:
            Log(1,"test_ldap_connect.parse data to json fail,input[%s]"%(post_data))
            return Result('',INVALID_JSON_DATA_ERR,str(e))
        if 'password' in user_info:
            user_info['password'] = base64.decodestring(user_info['password'])
        client = LDAPClient.new_ladp_client(**user_info)
        if not client:
            return Result('', LDAP_SERVER_INFO_INVALID_ERR, 'LDAP server info invalid')
        
        username = user_info.get('test_user_name', '')
        password = user_info.get('test_password', '')
        if not (username and password):
            return Result('', LDAP_TEST_ACCOUNT_INVALID_ERR, 'Test parameter invalid')
        
        if client.verify_user(username, base64.decodestring(password)):
            WebLog(3, 'user[%s]login LDAP success.'%(username))
            return Result('ok')
        else:
            WebLog(3, 'user[%s]login LDAP fail.'%(username))
            return Result('', TEST_LDAP_AUTH_FAIL_ERR, 'user name not exist or password invalid.')
    
    @ring0
    def emails(self):
        return EmailDBImpl.instance().read_record_list()
    
    @ring0
    def update_email(self, post_data):
        try:
            email_list = json.loads(post_data.replace("'", '"'))
        except Exception,e:
            Log(1,"update_email.parse data to json fail,input[%s]"%(post_data))
            return Result('',INVALID_JSON_DATA_ERR,str(e))
        
        rlt = EmailDBImpl.instance().update_email_list('admin', email_list)
        if rlt.success:
            if self.emailmgr:
                self.emailmgr.load_email()
        else:
            WebLog(2, 'set admin email fail')
            
        return rlt
    
    @ring0
    @ring3
    @ring5
    def domain(self):
        dm = GetSysConfig('common_name')
        return Result({'domain': dm})
    
    @ring0
    @ring3
    @ring5
    def version(self):
        pro = GetSysConfig('pro_version')
        dev = GetSysConfig('dev_version')
        return Result({'pro_version': pro, 'dev_version': dev})
    
    
    
    
    