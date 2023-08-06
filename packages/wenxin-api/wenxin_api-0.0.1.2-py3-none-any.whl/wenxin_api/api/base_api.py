import wenxin_api
from wenxin_api import requestor, error, util
from typing import Optional
from wenxin_api.error import IlleagalRequestArgumentError

class BaseObject(dict):
    api_base_override = None

    def __init__(
        self,
        id=None,
        ak=None,
        sk=None,
        api_type=None,
        base_model=None,
        **params,
    ):
        super(BaseObject, self).__init__()

        self._retrieve_params = params

        object.__setattr__(self, "ak", ak)
        object.__setattr__(self, "sk", sk)
        object.__setattr__(self, "api_type", api_type)
        object.__setattr__(self, "base_model", engine)

        if id:
            self["id"] = id

    def __setattr__(self, k, v):
        if k[0] == "_" or k in self.__dict__:
            return super(BaseObject, self).__setattr__(k, v)

        self[k] = v
        return None

    def __getattr__(self, k):
        if k[0] == "_":
            raise AttributeError(k)
        try:
            return self[k]
        except KeyError as err:
            raise AttributeError(*err.args)

    def __delattr__(self, k):
        if k[0] == "_" or k in self.__dict__:
            return super(BaseObject, self).__delattr__(k)
        else:
            del self[k]

    def __setitem__(self, k, v):
        if v == "":
            raise ValueError(
                "You cannot set %s to an empty string. "
                "We interpret empty strings as None in requests."
                "You may set %s.%s = None to delete the property" % (k, str(self), k)
            )
        super(BaseObject, self).__setitem__(k, v)

    def __delitem__(self, k):
        raise NotImplementedError("del is not supported")

    # Custom unpickling method that uses `update` to update the dictionary
    # without calling __setitem__, which would fail if any value is an empty
    # string
    def __setstate__(self, state):
        self.update(state)

    # Custom pickling method to ensure the instance is pickled as a custom
    # class and not as a dict, otherwise __setstate__ would not be called when
    # unpickling.
    def __reduce__(self):
        reduce_value = (
            type(self),  # callable
            (  # args
                self.get("id", None),
                self.api_key,
                self.api_version,
                self.api_type,
                self.organization,
            ),
            dict(self),  # state
        )
        return reduce_value

    @classmethod
    def construct_from(
        cls,
        values,
        api_key: Optional[str] = None,
        api_version=None,
        organization=None,
        engine=None,
        response_ms: Optional[int] = None,
    ):
        instance = cls(
            values.get("id"),
            api_key=api_key,
            api_version=api_version,
            organization=organization,
            engine=engine,
            response_ms=response_ms,
        )
        instance.refresh_from(
            values,
            api_key=api_key,
            api_version=api_version,
            organization=organization,
            response_ms=response_ms,
        )
        return instance

    def refresh_from(
        self,
        values,
        api_key=None,
        api_version=None,
        api_type=None,
        organization=None,
        response_ms: Optional[int] = None,
    ):
        self.api_key = api_key or getattr(values, "api_key", None)
        self.api_version = api_version or getattr(values, "api_version", None)
        self.api_type = api_type or getattr(values, "api_type", None)
        self.organization = organization or getattr(values, "organization", None)
        self._response_ms = response_ms or getattr(values, "_response_ms", None)

        # Wipe old state before setting new.
        self.clear()
        for k, v in values.items():
            super(BaseObject, self).__setitem__(
                k, util.convert_to_wenxin_object(v, api_key, api_version, organization)
            )

        self._previous = values

    @classmethod
    def api_base(cls):
        return None

    def request(
        self,
        url,
        method="post",
        params=None,
        headers=None,
        stream=False,
        plain_old_data=False,
        request_id: Optional[str] = None,
    ):
        if params is None:
            params = self._retrieve_params
        requestor = requestor.HTTPRequestor(ak=ak, sk=sk, api_type=self.api_type)
        response = requestor.request(url, params=params, request_id=request_id,)

        return response

    def __repr__(self):
        ident_parts = [type(self).__name__]

        obj = self.get("object")
        if isinstance(obj, str):
            ident_parts.append(obj)

        if isinstance(self.get("id"), str):
            ident_parts.append("id=%s" % (self.get("id"),))

        unicode_repr = "<%s at %s> JSON: %s" % (
            " ".join(ident_parts),
            hex(id(self)),
            str(self),
        )

        return unicode_repr

    def __str__(self):
        obj = self.to_dict_recursive()
        return json.dumps(obj, sort_keys=True, indent=2)

    def to_dict(self):
        return dict(self)

    def to_dict_recursive(self):
        d = dict(self)
        for k, v in d.items():
            if isinstance(v, BaseObject):
                d[k] = v.to_dict_recursive()
            elif isinstance(v, list):
                d[k] = [
                    e.to_dict_recursive() if isinstance(e, BaseObject) else e
                    for e in v
                ]
        return d


    # This class overrides __setitem__ to throw exceptions on inputs that it
    # doesn't like. This can cause problems when we try to copy an object
    # wholesale because some data that's returned from the API may not be valid
    # if it was set to be set manually. Here we override the class' copy
    # arguments so that we can bypass these possible exceptions on __setitem__.
    def __copy__(self):
        copied = BaseObject(
            self.get("id"),
            self.api_key,
            api_version=self.api_version,
            api_type=self.api_type,
            organization=self.organization,
        )

        copied._retrieve_params = self._retrieve_params

        for k, v in self.items():
            # Call parent's __setitem__ to avoid checks that we've added in the
            # overridden version that can throw exceptions.
            super(BaseObject, copied).__setitem__(k, v)

        return copied

    # This class overrides __setitem__ to throw exceptions on inputs that it
    # doesn't like. This can cause problems when we try to copy an object
    # wholesale because some data that's returned from the API may not be valid
    # if it was set to be set manually. Here we override the class' copy
    # arguments so that we can bypass these possible exceptions on __setitem__.
    def __deepcopy__(self, memo):
        copied = self.__copy__()
        memo[id(self)] = copied

        for k, v in self.items():
            # Call parent's __setitem__ to avoid checks that we've added in the
            # overridden version that can throw exceptions.
            super(BaseObject, copied).__setitem__(k, deepcopy(v, memo))

        return 

class APIBaseObject(BaseObject):
    # hard code
    base_api_urls = ["http://10.255.132.22:8080/task/deal_requests"]
    api_type_id = 0

    @classmethod
    def default_request(
        cls,
        ak=None,
        sk=None,
        method="post",
        api_type=None,
        request_id=None,
        files=None,
        **params,
    ):
        try:
            api_type = int(api_type)
            url = cls.base_api_urls[api_type]
        except:
            raise IlleagalRequestArgumentError()
        http_requestor = requestor.HTTPRequestor(ak, sk, request_type)
        response = http_requestor.request(url, method, files=files, request_id=request_id, **params)
        return response
    
    @classmethod
    def get_url(cls, api_type=0):
        try:
            api_type = int(api_type)
            url = cls.base_api_urls[api_type]
        except:
            raise IlleagalRequestArgumentError()
        return url

class CreatableAPIObject(APIBaseObject):
    """ creatable api object """
    @classmethod
    def create(cls, ak=None, sk=None, api_type=None, request_id=None, **params):
        if isinstance(cls, APIBaseObject):
            raise ValueError(".create may only be called as a class method now.")
        return cls.default_request(ak, sk, api_type=api_type, request_id=request_id, **params)

class DeletableAPIObject(APIBaseObject):
    """ deletable api object """
    @classmethod
    def delete(cls, ak=None, sk=None, api_type=None, request_id=None, **params):
        if isinstance(cls, APIBaseObject):
            raise ValueError(".delete may only be called as a class method now.")
        return cls.default_request(ak, sk, api_type=api_type, request_id=request_id, **params)

class ListableAPIObject(APIBaseObject):
    """ listable api object """
    @classmethod
    def list(cls, ak=None, sk=None, api_type=None, request_id=None, **params):
        request_type = params.pop("type", None)
        http_requestor = requestor.HTTPRequestor(ak, sk, request_type)
        method = params.pop("method", "post")
        url = cls.get_url(api_type)
        response = http_requestor.request(url, method, request_id=request_id, **params)
        return response

    @classmethod
    def retrieve(cls, ak=None, sk=None, api_type=None, request_id=None, **params):
        print("retrieve params:", params)
        if "type" not in params or "{}_id".format(params["type"]) not in params:
            raise IlleagalRequestArgumentError("type or $\{type\}_id is not provided")
        request_type = params.pop("type", None)
        http_requestor = requestor.HTTPRequestor(ak, sk, request_type)
        method = params.pop("method", "post")
        url = cls.get_url(api_type)
        response = http_requestor.request(url, method, request_id=request_id, **params)
        return response