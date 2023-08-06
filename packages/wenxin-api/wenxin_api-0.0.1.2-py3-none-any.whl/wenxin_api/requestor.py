import json
import platform
import threading
import warnings
from json import JSONDecodeError
from typing import Dict, Iterator, Optional, Tuple, Union
from urllib.parse import urlencode, urlsplit, urlunsplit

import requests

import wenxin_api
from wenxin_api import error, util, version, log
from wenxin_api.error import APIConnectionError, InvalidResponseValue, AuthenticationError
from wenxin_api.const import TIMEOUT_SECS, MAX_CONNECTION_RETRIES, BASE_ERNIE_100B_MODEL_ID

# Has one attribute per thread, 'session'.
_thread_context = threading.local()
logger = log.get_logger()

from typing import Optional


class WenxinAPIResponse:
    def __init__(self, data, headers, request_type):
        self._headers = headers
        self.data = data
        self.type = request_type

    @property
    def id(self) -> Optional[str]:
        return self.data.get(f"{self.type}_id", "")

    @property
    def status(self) -> Optional[str]:
        return self.data.get(f"{self.type}_status", None)

    def __str__(self):
        return "WenxinAPIResponse {}:{}\n".format(
                        id(self),
                        json.dumps({"id": self.id, "status": self.status}, ensure_ascii=False)
        )

    def __repr__(self):
        return self.__str__()


def _requests_proxies_arg(proxy) -> Optional[Dict[str, str]]:
    if proxy is None:
        return None
    elif isinstance(proxy, str):
        return {"http": proxy, "https": proxy}
    elif isinstance(proxy, dict):
        return proxy.copy()
    else:
        raise ValueError(
            "'wenxin.proxy' must be url str or dict"
        )


def _make_session() -> requests.Session:
    s = requests.Session()
    proxies = _requests_proxies_arg(wenxin_api.proxy)
    if proxies:
        s.proxies = proxies
    s.mount(
        "https://",
        requests.adapters.HTTPAdapter(max_retries=MAX_CONNECTION_RETRIES),
    )
    return s


class HTTPRequestor:
    """ HTTP Requestor """ 
    def __init__(self, ak=None, sk=None, request_type=None):
        self.ak = ak
        self.sk = sk
        self.request_type = request_type
        self.access_token_post_url = "https://wenxin.baidu.com/younger/portal/api/oauth/token" # hard code
        
    def _get_access_token(self, ak=None, sk=None):
        if ak == None or sk == None:
            ak = wenxin_api.ak
            sk = wenxin_api.sk
        json_data = {
            "grant_type": "client_credentials",
            "client_id": ak,
            "client_secret": sk
        }
        method = "post" # hard code
        result = self._request(self.access_token_post_url, method, data=json_data)
        print("result of access token:", result.json())
        return result.json()["data"]

    def request(self, url, method="post", files=None, request_id=None, **params
    ) -> Union[WenxinAPIResponse, Iterator[WenxinAPIResponse]]:
        print("params:", params)
        if isinstance(params, dict):
            data = params
            base_model = params.get("base_model", BASE_ERNIE_100B_MODEL_ID)
            return_raw = params.pop("return_raw", False)
        else:
            data = {}
            base_model = BASE_ERNIE_100B_MODEL_ID
        data["cmd"] = request_id
        data["base_model"] = base_model
        # try to use default access_token first
        # if auth failed, use dynamically generated access_token instead
        try:
            if wenxin_api.access_token != None:
                data["access_token"] =  wenxin_api.access_token
            else:
                access_token = self._get_access_token(self.ak, self.sk)
                data["access_token"] =  access_token
                wenxin_api.access_token = access_token
            result = self._request(url, method=method, data=data, files=files)
            print("raw rst:", result.status_code)
            if result.status_code == 200:
                print("raw rst content:", result.content)
        except AuthenticationError as e:
            access_token = self._get_access_token(self.ak, self.sk)
            data["access_token"] =  access_token
            wenxin_api.access_token = access_token
            result = self._request(url, method=method, data=data, files=files)

        if return_raw:
            return result
        else:
            resp = self._resolve_response(result.content, result.status_code, result.headers)
            return resp

    def _request(self, url, method="post", data=None, files=None) -> requests.Response:
        headers = {"Content-Type": "application/json"}
        if not hasattr(_thread_context, "session"):
            _thread_context.session = _make_session()
        try:
            result = _thread_context.session.request(
                method,
                url,
                headers=headers,
                json=data,
                files=files,
                timeout=TIMEOUT_SECS,
            )
        except requests.exceptions.RequestException as e:
            raise error.APIConnectionError("error communicating with wenxin api") from e
        logger.info("wenxin api response code of {}:\n{}\n".format(url, result.status_code))
        return result

    def _resolve_response(self, rbody, rcode, rheaders) -> WenxinAPIResponse:
        if rcode == 503:
            raise error.ServiceUnavailableError(
                "The server is overloaded or not ready yet.",
                rbody,
                rcode,
                headers=rheaders,
            )
        try:
            if hasattr(rbody, "decode"):
                rbody = rbody.decode("utf-8")
            data = json.loads(rbody)
        except (JSONDecodeError, UnicodeDecodeError):
            raise error.APIError(
                f"HTTP code {rcode} from API ({rbody})", rbody, rcode, headers=rheaders
            )

        if len(data["result"]) == 0:
            # some method may return null data
            resp = WenxinAPIResponse({}, rheaders, self.request_type)
        elif isinstance(data["result"][self.request_type], dict):
            resp = WenxinAPIResponse(data["result"][self.request_type], rheaders, self.request_type)
        elif isinstance(data["result"][self.request_type], list):
            resp = [
                WenxinAPIResponse(one_data, rheaders, self.request_type) \
                    for one_data in data["result"][self.request_type]
            ]
        else:
            raise ResponseDecodeError(json.dumps(data, ensure_ascii=False, indent=2))

        if rcode not in [0, 200]:
            raise self._error_handling(rbody, rcode, resp.data, rheaders)
        return resp

    def _error_handling(self, rbody, rcode, resp, rheaders):
        try:
            error_data = resp["error"]
        except (KeyError, TypeError):
            raise error.APIError(
                "Invalid response object from API: %r (HTTP response code "
                "was %d)" % (rbody, rcode),
                rbody,
                rcode,
                resp,
            )

        if "internal_message" in error_data:
            error_data["message"] += "\n\n" + error_data["internal_message"]

        util.log_info(
            "Wenxin API error received",
            error_code=error_data.get("code"),
            error_type=error_data.get("type"),
            error_message=error_data.get("message"),
            error_param=error_data.get("param"),
            stream_error=stream_error,
        )

        # Rate limits were previously coded as 400's with code 'rate_limit'
        if rcode == 429:
            return error.RateLimitError(
                error_data.get("message"), rbody, rcode, resp, rheaders
            )
        elif rcode in [400, 404, 415]:
            return error.InvalidRequestError(
                error_data.get("message"),
                error_data.get("param"),
                error_data.get("code"),
                rbody,
                rcode,
                resp,
                rheaders,
            )
        elif rcode == 401:
            return error.AuthenticationError(
                error_data.get("message"), rbody, rcode, resp, rheaders
            )
        elif rcode == 403:
            return error.PermissionError(
                error_data.get("message"), rbody, rcode, resp, rheaders
            )
        elif rcode == 409:
            return error.TryAgain(
                error_data.get("message"), rbody, rcode, resp, rheaders
            )
        else:
            return error.APIError(
                error_data.get("message"), rbody, rcode, resp, rheaders
            )