# wenxin api python bindings.

import os
from typing import Optional

from wenxin_api.api import Task, Dataset, Train, Model
from wenxin_api.error import WenxinError, APIError, InvalidRequestError
from wenxin_api.requestor import WenxinAPIResponse
from wenxin_api import const, log, version

ak = os.environ.get("WENXINAPI_AK", None)
sk = os.environ.get("WENXINAPI_SK", None)
access_token = os.environ.get("WENXINAPI_ACCESS_TOKEN", None)
debug = False
proxy=None

__all__ = [
    "Task"
    "Dataset",
    "Train",
    "Model",
    "APIError",
    "WenxinError",
    "InvalidRequestError",
    "ak",
    "sk",
    "access_token",
    "api_type",
    "log",
    "const",
    "version",
]