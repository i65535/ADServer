# -*- coding: utf-8 -*-
# Copyright (c) 20016-2016 The i65535.
# See LICENSE for details.

"""
"""

COLLECTOR = 10000

SUCCESS = 0
FAIL = COLLECTOR
MAX_ERROR_CODE = COLLECTOR +10000


UNCAUGHT_EXCEPTION_ERR = COLLECTOR + 1


AUTHEN_ERROR = COLLECTOR + 100
INVALID_TOKEN_ERR      = AUTHEN_ERROR + 1                # 无效的token
ERR_LOGIN_TIMEOUT      = AUTHEN_ERROR + 2                # 登录超时
USER_UN_LOGIN_ERR      = AUTHEN_ERROR + 3                # 用户未登录
ERR_ACCESS_IDNOTEXIST  = AUTHEN_ERROR + 4                # access_uuid不存在
ERR_NO_TOKEN_PARAM     = AUTHEN_ERROR + 5                # 缺少token
ERR_TIME_MISMATCH      = AUTHEN_ERROR + 6                # 时间偏移超过限制范围

ERR_TIMESTAMP_REPEAT   = AUTHEN_ERROR + 7                # 时间戳重复，调用太频繁或非法调用 

PERMISSION_DENIED_ERR  = AUTHEN_ERROR + 8                # 用户权限不够
ERR_UNDEFINED_RING     = AUTHEN_ERROR + 9                # 未定义的ring
NO_SUCH_GROUP_ERR      = AUTHEN_ERROR + 10               # 分组不存在
NO_SUCH_USER_ERR       = AUTHEN_ERROR + 11               # 用户不存在
INVALID_PASSWORD_ERR   = AUTHEN_ERROR + 12               # 密码错误
ERR_ACCESS_AUTHENFAIL  = AUTHEN_ERROR + 13               # 密钥未通过验证




COMMON_ERR = COLLECTOR + 200
FILE_OPERATE_ERR = COMMON_ERR + 1
CALL_REMOTE_METHOD_ERR = COMMON_ERR + 2
REMOTE_SERVICE_ABNORMAL_ERR = COMMON_ERR + 3
SERVER_IS_DISCONNECT_ERR = COMMON_ERR + 4     # 服务器连接断开

ERR_SERVICE_INACTIVE = COMMON_ERR + 5
INTERNAL_OPERATE_ERR = COMMON_ERR + 6
INTERNAL_EXCEPT_ERR = COMMON_ERR + 7
PERMISSION_DENIED_ERR = COMMON_ERR + 8
ERR_METHOD_CONFLICT = COMMON_ERR + 10
RESULT_FORMAT_INVALID = COMMON_ERR + 11
INVALID_PARAM_ERR = COMMON_ERR + 12
INVALID_RESULT_DATA_ERR = COMMON_ERR + 13
INVALID_JSON_DATA_ERR = COMMON_ERR + 14



CONFIG_OUT_OF_LIMIT_ERR = COMMON_ERR + 50                # 用户输入超出配置限制
DATE_FAMAT_IS_INVALID = COMMON_ERR + 51                  # 日期格式不合法
PARAME_IS_INVALID_ERR = COMMON_ERR + 52                  # 参数不合法
CERT_NOT_EXIST_ERR = COMMON_ERR + 53                     # 参数不合法
  

DB_ERROR               = COLLECTOR + 500
DATABASE_EXCEPT_ERR    = DB_ERROR + 1                    # 数据库异常
NO_SUCH_RECORD_ERR     = DB_ERROR + 3                    # 记录不存在
IDENTITY_KEY_NOT_EXIST_ERR = DB_ERROR + 9                # 记录信息中没有ID
FILTER_IS_INVALID_ERR = DB_ERROR + 10                    # 过滤条件不合法


CONSOLE_ERROR = COLLECTOR + 1000

INVALID_PARAMETERS_ERR = CONSOLE_ERROR + 1               # 
NO_IMPLEMENT_INTERFACE_ERR = CONSOLE_ERROR + 2           # 没有实现对应的接口



API_ERR = COLLECTOR + 2000
INVALID_USER_INFO_ERR = API_ERR + 1
USER_EXIST_ALREADY_ERR = API_ERR + 2
INVALID_GROUP_INFO_ERR = API_ERR + 3
GROUP_EXIST_ALREADY_ERR = API_ERR + 4
INVALID_NAMESPACE_INFO_ERR = API_ERR + 5
NAMESPACE_EXIST_ALREADY_ERR = API_ERR + 6
LOG_FILE_NOT_EXIST_ERR = API_ERR + 7
TAG_NOT_EXIST_ERR = API_ERR + 8
TAG_NAME_INVALID_ERR = API_ERR + 9
USER_INFO_INVALID_ERR = API_ERR + 10

INVALID_STORAGE_TYPE_ERR = API_ERR + 11
INVALID_STORAGE_PATH_ERR = API_ERR + 12
ABNORMAL_CALL_ERR = API_ERR + 13
TAG_EXIST_AlREADY_ERR = API_ERR + 14
OLD_PASSWORD_INVALID_ERR = API_ERR + 15
INVALID_CONTENT_TYPE_ERRR = API_ERR + 16
USER_NAMESPACE_NOT_EMPTY_ERR = API_ERR + 17
DELETE_IMAGE_FAIL_ERR = API_ERR + 18
BACKUP_MANIFEST_FAIL_ERR = API_ERR + 19
SAVE_MANIFEST_FILE_FAIL_ERR = API_ERR + 20
MANIFEST_IS_INVALID_ERR = API_ERR + 21
RECYCLE_BIN_NOT_EMPTY_ERR = API_ERR + 22
DOCKER_CLIENT_INIT_FAIL_ERR = API_ERR + 23
DELETE_LAYER_FAIL_ERR = API_ERR + 24
USER_NAME_INVALID_ERR = API_ERR + 25
NAMESPACE_INVALID_ERR = API_ERR + 26

LDAP_SERVER_INFO_INVALID_ERR = API_ERR + 100
TEST_LDAP_AUTH_FAIL_ERR = API_ERR + 101
LDAP_TEST_ACCOUNT_INVALID_ERR = API_ERR + 102
INVALID_AUTH_METHOD_ERR = API_ERR + 103
LDAP_USER_NOT_EXIST_ERR = API_ERR + 104
LDAP_USER_PWD_INVALID_ERR = API_ERR + 105
LDAP_USER_LOGIN_REFUSE_ERR = API_ERR + 106
CAN_NOT_ADD_LOCAL_USER_ERR = API_ERR + 107


CREATE_CRON_SCHEDULE_FAIL = API_ERR + 500
CREATE_INTERVAL_SCHEDULE_FAIL = API_ERR + 501


SEND_EMAIL_FAIL_ERR = API_ERR + 600




REGISTRY_ERR = COLLECTOR + 3000
INVALID_MANIFEST_URL_ERR = REGISTRY_ERR + 1
READ_MANIFEST_FAIL_ERR = REGISTRY_ERR + 2
INVALID_SCHEMA_VERSION_ERR = REGISTRY_ERR + 3
CALL_DOCKER_INTERFACE_FAIL_ERR = REGISTRY_ERR + 4
TAG_IMAGE_FAIL_ERR = REGISTRY_ERR + 5
LOGIN_TO_REGISTRY_FAIL_ERR = REGISTRY_ERR + 6
LAYER_DIGEST_INVALID_ERR = REGISTRY_ERR + 300



UPGRADE_ERR = COLLECTOR + 4000
UPGRADE_FAIL_ERR = UPGRADE_ERR + 1
DO_NOT_NEED_UPGRADE_ERR = UPGRADE_ERR + 2

BACKUP_DATA_FILE_INVALID_ERR = UPGRADE_ERR + 200
BACKUP_DATABASE_FAIL_ERR = UPGRADE_ERR + 201
CLEAR_DATABASE_FAIL_ERR = UPGRADE_ERR + 202
RESTORE_DATABASE_FAIL_ERR = UPGRADE_ERR + 203
UPLOAD_DATA_FILE_FAIL_ERR = UPGRADE_ERR + 204
EXTRACT_DATA_FILE_FAIL_ERR = UPGRADE_ERR + 205
DROP_DATABASE_FAIL_ERR = UPGRADE_ERR + 206
DATABASE_NOT_EXIST_ERR = UPGRADE_ERR + 207

EXTENTION_ERR = COLLECTOR + 5000
EXTENTION_NOT_EXIST_ERR = EXTENTION_ERR + 1
INIT_DOCKER_CLIENT_FAILERR = EXTENTION_ERR + 2
INVALID_EXTENSION_INFO_ERR = EXTENTION_ERR + 3
EXTENSION_ADDRESS_EXIST_ERR = EXTENTION_ERR + 4
PULL_IMAGE_FAIL_ERR = EXTENTION_ERR + 5
PUSH_IMAGE_FAIL_ERR = EXTENTION_ERR + 6
INIT_DEFAULT_EXTENTION_FAIL_ERR = EXTENTION_ERR + 7

WORK_FLOW_ERR = COLLECTOR + 6000
WORK_INFO_INVALID_ERR = WORK_FLOW_ERR + 1
TASK_TIMEOUT_ERR = WORK_FLOW_ERR + 2
TASK_ALREADY_EXIST_ERR = WORK_FLOW_ERR + 3