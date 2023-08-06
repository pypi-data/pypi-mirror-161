class ResponseError(Exception):
    def __init__(self, res, errorType):
        code = 0
        Exception.__init__(self, f"{errorType} error: {res['data']['msg']}")


class CCTLDResponseError(ResponseError):
    def __init__(self, res):
        ResponseError.__init__(self, res, "CCTLD")


class NginxForbiddenResponseError(ResponseError):
    def __init__(self, res):
        res = {
            "data": {
                "msg": "403 Forbidden, perhaps the ip address has not been added to the firewall"
            }
        }
        ResponseError.__init__(self, res, "Web Server")
