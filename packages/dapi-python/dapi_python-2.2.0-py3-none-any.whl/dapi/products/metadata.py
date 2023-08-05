from dapi.dapi_request import DapiRequest


class Metadata(DapiRequest):

    def getAccounts(self, access_token, user_secret, user_inputs=[], operation_id=""):
        '''
        Return the bank's meta data for the user's account
        (`HTTP docs <https://docs.dapi.com/docs/get-accounts-metadata>`__)

        :param  str     access_token:    From the exchangeToken method.

        :param  str     user_secret:     From the connect JS response after the user logs in 
        '''
        resource_path = '/metadata/accounts/get'
        post_data = {
            "userInputs": user_inputs,
            "operationID": operation_id
        }
        return self.authenticated_request(access_token=access_token, user_secret=user_secret, resource_path=resource_path,
                                          post_data=post_data)
