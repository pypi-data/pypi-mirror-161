from wenxin_api.api.base_api import DeletableAPIObject, ListableAPIObject

class Model(ListableAPIObject, DeletableAPIObject):
    """ model class """
    OBJECT_NAME = "models"