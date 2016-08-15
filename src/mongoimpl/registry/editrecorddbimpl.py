# -*- coding: utf-8 -*-
# Copyright (c) 20016-2016 The i65535.
# See LICENSE for details.
"""
Implement Order data manage
"""

import threading

from common.guard import LockGuard
from common.util import NowMilli
from frame.Logger import Log
from mongodb.dbbase import DBBase
from mongodb.dbconst import MAIN_DB_NAME, EDITRECORD_TABLE


class EditRecordDBImpl(DBBase):
    db = MAIN_DB_NAME
    collection = EDITRECORD_TABLE
    __lock = threading.Lock()

    @classmethod
    def instance(cls):
        with LockGuard(cls.__lock):
            if not hasattr(cls, "_instance"):
                cls._instance = cls()
        return cls._instance

    def __init__(self):
        DBBase.__init__(self, self.db, self.collection)

    def create_edit_record(self, _id, user_id, msg):
        record = {}
        record['tag_id'] = int(_id)
        record['edit_time'] = NowMilli()
        record['edit_user'] = user_id
        record['edit_message'] = msg
        rlt = self.create(record)
        if not rlt.success:
            Log(1, 'create_edit_record fail, as[%s]%(rlt.message)')

        return rlt

    def get_edit_info(self, tag_id):
        return self.read_record_list({'tag_id': int(tag_id)})

