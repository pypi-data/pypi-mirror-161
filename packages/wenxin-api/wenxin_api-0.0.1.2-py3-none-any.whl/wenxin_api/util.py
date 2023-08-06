import wenxin_api

def convert_to_wenxin_object(resp, return_raw=False):
    # convert wenxin_api response to wenxin_api object.

    response_ms: Optional[int] = None
    if isinstance(resp, wenxin_api.wenxin_response.WenxinResponse):
        resp = resp.data

    if return_raw:
        return resp
    elif isinstance(resp, list):
        return [convert_to_object(one_rst) for one_rst in resp]
    elif isinstance(resp, dict) and not isinstance(
        resp, wenxin.wenxin_object.WenxinObject
    ):
        resp = resp.copy()
        klass_name = resp.get("object")
        if isinstance(klass_name, str):
            klass = get_object_classes().get(
                klass_name, wenxin.wenxin_object.WenxinObject
            )
        else:
            klass = wenxin.wenxin_object.WenxinObject

        return klass.construct_from(
            resp,
            api_key=api_key,
            api_version=api_version,
            organization=organization,
            response_ms=response_ms,
            engine=engine,
        )
    else:
        return 