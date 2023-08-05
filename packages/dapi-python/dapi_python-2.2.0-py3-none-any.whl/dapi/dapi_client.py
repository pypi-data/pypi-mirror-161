from dapi.dapi_request import DapiRequest

from dapi.products import (
    Auth,
    Operation,
    Payment,
    Data,
    Metadata
)

DEFAULT_TIMEOUT = 300


class DapiClient(object):
    '''
    Dapi Connect Python API client

    API documentation: https://docs.dapi.com.

    :param  str     app_secret:          App Secret Key from Dashboard.
    '''

    def __init__(self, app_secret=None, timeout=DEFAULT_TIMEOUT):
        self.app_secret = app_secret
        self.timeout = timeout

        self.auth = Auth(self)
        self.payment = Payment(self)
        self.operation = Operation(self)
        self.data = Data(self)
        self.metadata = Metadata(self)

    def handleSDKDapiRequests(self, body={}, headers={}):
        request = DapiRequest(self)

        body = {
            **body,
            'appSecret': self.app_secret,
        }

        headers = {
            **headers,
            'host': 'dd.dapi.com',
            'Host': 'dd.dapi.com'
        }

        return request.post("", body, headers, True)
