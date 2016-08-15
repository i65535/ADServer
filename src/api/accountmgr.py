# -*- coding: utf-8 -*-
# Copyright (c) 20016-2016 The i65535.
# See LICENSE for details.

#import bcrypt

import base64
import json
import uuid

from api.accessmgr import AccessMgr
from api.apiauthen import APIAuthen
from common.util import Result, IsValidNamespace
from frame.Logger import Log, WebLog
from frame.authen import ring8, ring0, ring3, ring5
from frame.errcode import INVALID_PARAM_ERR, INVALID_JSON_DATA_ERR, NO_SUCH_USER_ERR, \
    PARAME_IS_INVALID_ERR, USER_INFO_INVALID_ERR, \
    ABNORMAL_CALL_ERR, OLD_PASSWORD_INVALID_ERR, \
    USER_NAME_INVALID_ERR, CAN_NOT_ADD_LOCAL_USER_ERR
from mongodb.dbconst import ID, AUTH_LOCAL
from mongoimpl.registry.groupdbimpl import GroupDBImpl
from mongoimpl.registry.groupnamespcdbimpl import GroupNamespcDBImpl
from mongoimpl.registry.userdbimpl import UserDBImpl
from mongoimpl.registry.usergroupdbimpl import UserGroupDBImpl


_ALL = "All"

class AccountMgr(object):
    def __init__(self):
        self.accessmgr = AccessMgr()
    
    @ring0
    def accounts(self, group_id='', **kw):
        if group_id.isalnum():
            group_id = int(group_id)
        else:
            group_id = -1;
           
        query = {}
        if kw:
            if 'user_id' in kw:
                query['_id'] = {'$regex':kw['user_id'].strip()}
        
        return UserDBImpl.instance().exec_db_script('accounts', group_id, query, 10000, 0)
    
    @ring0
    @ring3
    @ring5
    def account(self, user_id):
        user_id = user_id.strip()
        if user_id=='':
            return Result('', INVALID_PARAM_ERR, 'Invalid user id' )
        
        rlt = UserDBImpl.instance().read_record(user_id, projection={'password': False})
        if not rlt.success:
            Log(1, 'get account[%s]info fail,as[%s]'%(user_id, rlt.content))
        return rlt
    
        
    @ring8
    def login(self, post_data):
        try:
            account = json.loads(post_data.replace("'", '"'))
        except Exception,e:
            Log(1,"save_account.parse data to json fail,input[%s]"%(post_data))
            return Result('',INVALID_JSON_DATA_ERR,str(e))

        user_id = account.get('username')
        user_id = base64.decodestring(user_id)
        if not IsValidNamespace(user_id):
            return Result('', USER_NAME_INVALID_ERR, 'user name invalid')
        
        rlt = UserDBImpl.instance().read_record(user_id)
        if not rlt.success:
            return Result('',NO_SUCH_USER_ERR,'user not exist,or password is invalid')
        
        user_info = rlt.content
        if not self.accessmgr.verify_user_password(user_id, account.get('password',''), user_info):
            return Result('',NO_SUCH_USER_ERR,'user not exist,or password is invalid')
        
        WebLog(3, '[%s] user [%s] login'%(user_info.get('source', AUTH_LOCAL), user_id))
        
        user_info['access_key'] = str(uuid.uuid4())
        user_info['password'] = account.get('password','')
        data = APIAuthen.instance().create_token(user_info)
        return Result(data)
    
    @ring0
    @ring3
    @ring5
    def logout(self, post_data, **args):
        passport = args.get('passport',None)
        if passport is None or 'access_uuid' not in passport:
            return Result('', ABNORMAL_CALL_ERR, 'passport invalid')
        
        WebLog(3, 'user [%s] logout'%(passport['access_uuid']))
        
        return APIAuthen.instance().remove_token(passport['access_uuid'])
    
    
    @ring0
    @ring3
    @ring5
    def is_user_exist(self, user_name=''):
        user_id = user_name.strip()
        if user_id=='':
            return Result('', INVALID_PARAM_ERR, 'Invalid user id' )
        
        if UserDBImpl.instance().is_exist({ID:user_name}):
            return Result(True)
        
        return Result(False)
        
    @ring0
    def delete_account(self, post_data):
        try:
            _filter = json.loads(post_data.replace("'", '"'))
        except Exception,e:
            Log(1,"save_account.parse data to json fail,input[%s]"%(post_data))
            return Result('',INVALID_JSON_DATA_ERR,str(e))
        
        user_id = _filter.get('_id','')
        user_id = user_id.strip()
        if user_id=='':
            return Result('', INVALID_PARAM_ERR, 'Invalid user id' )

        UserGroupDBImpl.instance().rm_relation_by_uid(user_id)
        
        rlt = UserDBImpl.instance().delete_user(user_id)
        if not rlt.success:
            Log(1, 'delete_account[%s] fail,as[%s]'%(user_id, rlt.message))
        return rlt
        
        
    @ring0
    def add_account(self, post_data):
        try:
            account = json.loads(post_data.replace("'", '"'))
        except Exception,e:
            Log(1,"save_account.parse data to json fail,input[%s]"%(post_data))
            return Result('',INVALID_JSON_DATA_ERR,str(e))
        
        if not self.accessmgr.verify_user_info(account):
            WebLog(2, 'invalid user info')
            return Result('', USER_INFO_INVALID_ERR, 'invalid user info')
        
        _id = account.get('_id','')
        _id = str(_id).lower()
        if not IsValidNamespace(_id):
            return Result('', USER_NAME_INVALID_ERR, 'invalid user id')
        
        if not self.accessmgr.is_local_auth():
            WebLog(2, 'add_account fail,as[can not add local user]')
            return Result('', CAN_NOT_ADD_LOCAL_USER_ERR, 'can not add local user.')
        
        account['_id'] = _id
        account['source'] = AUTH_LOCAL
        return UserDBImpl.instance().create_new_user(account)
        
    
    @ring0
    def update_account(self, _id, post_data):
        _id = _id.strip()
        if _id=='':
            return Result('', INVALID_PARAM_ERR, 'Invalid user id' )
        
        try:
            info = json.loads(post_data.replace("'", '"'))
        except Exception,e:
            Log(1,"update_account.parse data to json fail,input[%s]"%(post_data))
            return Result('',INVALID_JSON_DATA_ERR,str(e))
        
        if not self.accessmgr.verify_user_info(info):
            return Result('', USER_INFO_INVALID_ERR, 'invalid user info')
        
        rlt = UserDBImpl.instance().update_user(_id, info)
        if rlt.success:
            WebLog(3, 'Admin edited user [%s]'%(_id))
        else:
            WebLog(3, 'Admin edit user [%s] fail,as [%s]'%(_id, rlt.message))
        return rlt
    
    @ring0
    @ring3
    @ring5
    def groups(self, namespace=None):
        query = {}
        if namespace is not None:
            namespace = namespace.strip()
            if namespace!='':
                query = {'namespace':namespace}
        
        return GroupDBImpl.instance().exec_db_script('groups', query, 10000, 0)
    
    @ring0
    @ring3
    @ring5
    def group(self, group_id):
        if group_id.isalnum():
            group_id = int(group_id)
        else:
            return Result(group_id, PARAME_IS_INVALID_ERR, 'Invalid group id')
        return GroupDBImpl.instance().exec_db_script('groupInfo', group_id)
    
    @ring0
    @ring3
    @ring5
    def is_group_exist(self, namespace, group_name):
        namespace = namespace.strip()
        group_name = group_name.strip()
        
        if not namespace or not group_name:
            return Result('', INVALID_PARAM_ERR, 'Param is invalid.')
        
        return GroupDBImpl.instance().is_exist({'namespace':namespace,'group_name':group_name})
    
    @ring0
    def add_group(self, post_data):
        try:
            group_info = json.loads(post_data.replace("'", '"'))
        except Exception,e:
            Log(1,"add_group.parse data to json fail,input[%s]"%(post_data))
            return Result('',INVALID_JSON_DATA_ERR,str(e))
        else:
            return GroupDBImpl.instance().create_new_group(group_info)
    
    @ring0
    def delete_group(self, post_data):
        try:
            _filter = json.loads(post_data.replace("'", '"'))
        except Exception,e:
            Log(1,"delete_group.parse data to json fail,input[%s]"%(post_data))
            return Result('',INVALID_JSON_DATA_ERR,str(e))
        
        group_id = _filter.get('group_id','')
        if not isinstance(group_id, int):
            return Result(group_id, INVALID_PARAM_ERR, 'Invalid group id' )
        
        UserGroupDBImpl.instance().rm_relation_by_gid(group_id)

        GroupNamespcDBImpl.instance().rm_relation_by_gid(group_id)
        
        rlt = GroupDBImpl.instance().delete_group(group_id)
        if not rlt.success:
            Log(1, 'delete_group[%s] fail,as[%s]'%(group_id, rlt.message))
        return rlt
    
    @ring0
    def update_group(self, _id, post_data):
        try:
            _id = int(_id)
        except:
            return Result(_id, INVALID_PARAM_ERR, 'group id is invalid')
        
        try:
            info = json.loads(post_data.replace("'", '"'))
        except Exception,e:
            Log(1,"update_group.parse data to json fail,input[%s]"%(post_data))
            return Result('',INVALID_JSON_DATA_ERR,str(e))
        
        return GroupDBImpl.instance().update_group(_id, info)
    
    @ring0
    @ring3
    @ring5
    def update_pwd(self, post_data):
        try:
            account = json.loads(post_data.replace("'", '"'))
        except Exception,e:
            Log(1,"save_account.parse data to json fail,input[%s]"%(post_data))
            return Result('',INVALID_JSON_DATA_ERR,str(e))
        else:
            user_id = account.get('username')
            user_id = base64.decodestring(user_id)
            rlt = UserDBImpl.instance().read_record(user_id)
            # if not rlt.success:
            #    return Result('',NO_SUCH_USER_ERR,'user not exist,or password is invalid')
            # if account.get('oldpwd') != getMD5('%s:%s'%(user_id, rlt.content['password'])):
            if account.get('oldpwd') != rlt.content['password']:
                return Result('', OLD_PASSWORD_INVALID_ERR,'old password is invalid')
            
            rlt = UserDBImpl.instance().update_pwd(user_id, account.get('newpwd'))
            if rlt.success:
                WebLog(3, 'user [%s] changed the password'%(user_id))
            else:
                WebLog(2, 'user [%s] change the password fail,as[%s]'%(user_id, rlt.message))
            return rlt
    
    @ring0
    @ring3
    @ring5    
    def accept_disclaimer(self, **args):
        passport = args.get('passport',None)
        if passport is None or 'access_uuid' not in passport:
            return Result('', ABNORMAL_CALL_ERR, 'passport invalid')
        return UserDBImpl.instance().accept_disclaimer(passport['access_uuid'])
    
    