import time

from wenxin_api import util, error
from wenxin_api.api import Task
from wenxin_api.error import TryAgain

import time
import warnings

from wenxin_api import util
from wenxin_api.api import ListableAPIResource, UpdateableAPIResource
from wenxin_api.error import InvalidAPIType, TryAgain
from wenxin_api.util import ApiType
logger = util.get_logger()

class TextGeneration(Task):
    OBJECT_NAME = "text_generation"

    @classmethod
    def create(cls, *args, **kwargs):
        """ text generation task """
        start = time.time()
        timeout = kwargs.pop("timeout", None)
        kwargs["request_id"] = 0

        while True:
            try:
                return super().create(*args, **kwargs)
            except TryAgain as e:
                if timeout is not None and time.time() > start + timeout:
                    raise

                logger.info("Waiting for model to warm up, msg: {}".format(e))