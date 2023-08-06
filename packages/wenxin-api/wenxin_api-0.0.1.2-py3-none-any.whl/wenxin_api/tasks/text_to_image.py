import time

from wenxin_api import requestor, util, error, log
from wenxin_api.api import Task
from wenxin_api.error import TryAgain

import time
import warnings

from wenxin_api import util
from wenxin_api.api import ListableAPIObject
from wenxin_api.variable import REQUEST_SLEEP_TIME
logger = log.get_logger()

class TextToImage(Task):
    OBJECT_NAME = "text_to_image"

    @classmethod
    def create(cls, *args, **params):
        """ text generation task """
        # hard code
        create_url = "https://wenxin.baidu.com/younger/portal/api/rest/1.0/ernievilg/v1/txt2img"
        retrieve_url = "https://wenxin.baidu.com/younger/portal/api/rest/1.0/ernievilg/v1/getImg"
        start = time.time()
        timeout = params.pop("timeout", None)
        text = params.pop("text", "")
        style = params.pop("style", "")
        http_requestor = requestor.HTTPRequestor()
        resp = http_requestor.request(create_url, text=text, style=style, return_raw=True)
        task_id = resp.json()["data"]["taskId"]
        not_ready = True
        while not_ready:
            resp = http_requestor.request(retrieve_url, taskId=task_id, return_raw=True)
            not_ready = resp.json()["data"]["status"] == 0
            if not not_ready:
                return resp.json()
            logger.info("model is painting now!, msg:{}\n".format(resp.json()))
            time.sleep(REQUEST_SLEEP_TIME)