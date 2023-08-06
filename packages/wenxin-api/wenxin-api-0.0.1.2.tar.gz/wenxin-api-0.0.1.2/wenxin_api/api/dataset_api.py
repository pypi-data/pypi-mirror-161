import json
import os
import time
from typing import cast

import wenxin_api
from wenxin_api import requestor, util, error, log
from wenxin_api.api import CreatableAPIObject, ListableAPIObject, DeletableAPIObject
from wenxin_api.error import TimeOutError, NotReady, MissingRequestArgumentError
from wenxin_api.const import CMD_UPLOAD_DATA, CMD_QUERY_DATA, CMD_DELETE_DATA
from wenxin_api.variable import REQUEST_SLEEP_TIME
logger = log.get_logger()


class Dataset(CreatableAPIObject, ListableAPIObject, DeletableAPIObject):
    OBJECT_NAME = "dataset"
    @classmethod
    def create(
        cls,
        local_file_path,
        ak=None,
        sk=None,
        api_type=0,
        **params
    ):
        timeout = params.pop("timeout", None)
        http_requestor = requestor.HTTPRequestor(ak, sk)
        files = {"file": ("file", open(local_file_path, 'rb'))}
        wenxin_response = cls.default_request(ak=ak,
                                              sk=sk,
                                              api_type=api_type, 
                                              request_id=CMD_UPLOAD_DATA, 
                                              files=files)
        dataset_id = wenxin_response.id
        while True:
            try:
                return cls.retrieve(data_id=dataset_id, ak=ak, sk=sk, api_type=api_type)
            except NotReady as e:
                if timeout is not None and time.time() > start + timeout:
                    raise TimeOutError
                logger.info("please wait while the dataset is uploading, msg: {}".format(e))
                time.sleep(REQUEST_SLEEP_TIME)

        return response

    @classmethod
    def retrieve(cls, *args, **params):
        request_id = CMD_QUERY_DATA
        params["type"] = "data"
        api_type = 0
        if "data_id" not in params:
            raise MissingRequestArgumentError("data_id is not provided")
        return super().retrieve(args, api_type=api_type, request_id=CMD_QUERY_DATA, **params)

    @classmethod
    def list(cls, *args, **params):
        request_id = CMD_QUERY_DATA
        params["type"] = "data"
        api_type = 0
        return super().list(args, api_type=api_type, request_id=CMD_QUERY_DATA, **params)

    @classmethod
    def delete(cls, *args, **params):
        request_id = CMD_DELETE_DATA
        params["type"] = "data"
        api_type = 0
        if "data_id" not in params:
            raise MissingRequestArgumentError("data_id is not provided")
        return super().retrieve(args, api_type=api_type, request_id=CMD_DELETE_DATA, **params)

