from dapi.dapi_request import DapiRequest


class Operation(DapiRequest):

    def getOperationStatus(self, access_token, user_secret, operation_id, app_key):
        '''
        Return the status of an Operation
        (`HTTP docs <https://docs.dapi.com/docs/operation-status>`__)

        :param  str     access_token:    From the exchangeToken method.

        :param  str     user_secret:     From the connect JS response after the user logs in

        :param  str     operation_id:       operationID from any request

        :param  str     app_key:         The appKey of the app which this operation is made from.

        '''
        resource_path = '/operation/get'
        post_data = {
            "operationID": operation_id,
            "appKey": app_key,
        }
        return self.authenticated_request(access_token=access_token, user_secret=user_secret, resource_path=resource_path,
                                          post_data=post_data)
