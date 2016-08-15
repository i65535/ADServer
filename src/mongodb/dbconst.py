# -*- coding: utf-8 -*-
# Copyright (c) 20016-2016 The i65535.
# See LICENSE for details.


MAIN_DB_NAME   = "i65535"
ID             = "_id"

IDENTITY_TABLE         = "identity"

USER_TABLE             = "User"
GROUP_TABLE            = "Group"
REPOSITORY_TABLE       = "Repository"
NAMESPACE_TABLE        = "Namespace" 
COMMENT_TABLE          = "Comment"
TAG_TABLE              = "Tags"
IMAGE_TABLE            = "Image"
LAYER_TABLE            = "Layer"
LAYER_IMAGE_TABLE      = "Layer_Image"
USER_GROUP_TABLE       = "User_Group"
GROUP_NAMESPACE_TABLE  = "Group_Namespace"
EDITRECORD_TABLE       = "Edit_Record"

STORAGE_TABLE          = "Storage"
SMTP_TABLE             = "SMTP"
EMAIL_TABLE            = "Email"
LOG_TABLE              = "Logs"
LDAP_TABLE             = "LDAP"
EXTENSTION_TABLE       = "Extension"


NOTIFICATION_TABLE     = "Notification"
PULL_EVENT_TABLE       = "PullEvent"
PUSH_EVENT_TABLE       = "PushEvent"


SCHEDULE_TABLE         = "Schedule"     # 调度任务信息
SCHEDULE_JOB_TABLE     = "Jobs"         # Scheduler 库使用的私有的数据表

OPERATE_TABLE          = "Operates"
TASK_TABLE             = "Task"
SUB_TASK_TABLE         = "SubTask"      # 存放子任务，子任务是任务计划的一部分， 不能单独恢复 
SYNCTASK               = "SyncTask"
WORK_DATA_TABLE        = "WorkInfo"
CONFIG_TABLE           = "Configure"




PERMISSION_PUBLIC = 'public'
PERMISSION_PRIVATE = 'private'
DEFAULT_NAMESPACE = 'library'

AUTH_LOCAL = 'local'
AUTH_LDAP = 'ldap'

NAMESPACE_TYPE_PERSONAL = 'P'
NAMESPACE_TYPE_ORGANIZATION = 'ORG'

LOCAL_FILE_SYSTEM = 'Local'
GLUSTERFS = 'GlusterFS'
APP_HOUSE_VERSION = '1.0.2.R2'

PERMISSION_ADMIN = 4
PERMISSION_PUSH = 2
PERMISSION_PULL = 1

