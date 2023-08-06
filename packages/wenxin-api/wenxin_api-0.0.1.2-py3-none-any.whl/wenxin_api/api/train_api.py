from wenxin_api import requestor, util, error
from wenxin_api.api import CreatableAPIObject, ListableAPIObject, DeletableAPIObject
from wenxin_api.requestor import WenxinAPIResponse


class Train(ListableAPIObject, CreatableAPIObject, DeletableAPIObject):
    OBJECT_NAME = "fine-tunes"

    @classmethod
    def stop(cls, id, ak=None, sk=None, **params) -> WenxinAPIResponse:
        instance = cls(id, ak, sk, **params)
        return instance.request(url, request_id=request_id)

