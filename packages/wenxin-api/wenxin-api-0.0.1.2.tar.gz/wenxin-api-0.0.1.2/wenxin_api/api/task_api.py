from wenxin_api.api.base_api import CreatableAPIObject, DeletableAPIObject, ListableAPIObject


class Task(CreatableAPIObject, ListableAPIObject, DeletableAPIObject):
    """ task class """
    OBJECT_NAME = "tasks"