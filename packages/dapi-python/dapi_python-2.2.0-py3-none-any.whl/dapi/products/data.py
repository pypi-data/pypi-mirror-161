from dapi.dapi_request import DapiRequest


class Data(DapiRequest):

    def getIdentity(self, access_token, user_secret, user_inputs=[], operation_id=""):
        '''
        Return the user's identity details.
        (`HTTP docs <https://docs.dapi.com/docs/get-identity>`__)

        :param  str     access_token:    From the exchangeToken method.

        :param  str     user_secret:     From the connect JS response after the user logs in 
        '''
        resource_path = '/data/identity/get'
        post_data = {
            "userInputs": user_inputs,
            "operationID": operation_id
        }
        return self.authenticated_request(access_token=access_token, user_secret=user_secret, resource_path=resource_path,
                                          post_data=post_data)

    def getAccounts(self, access_token, user_secret, user_inputs=[], operation_id=""):
        '''
        Returns all accounts for the user.
        (`HTTP docs <https://docs.dapi.com/docs/get-accounts>`__)

        :param  str     access_token:    From the exchangeToken method.

        :param  str     user_secret:     From the connect JS response after the user logs in 
        '''
        resource_path = '/data/accounts/get'

        post_data = {
            "userInputs": user_inputs,
            "operationID": operation_id
        }

        return self.authenticated_request(access_token=access_token, user_secret=user_secret, resource_path=resource_path,
                                          post_data=post_data)

    def getBalance(self, access_token, user_secret, account_id, user_inputs=[], operation_id=""):
        '''
        Return the account balance for a specific account
        (`HTTP docs <https://docs.dapi.com/docs/get-balance>`__)

        :param  str     access_token:    From the exchangeToken method.

        :param  str     user_secret:     From the connect JS response after the user logs in

        :param  str     account_id:      ID from the getAccounts method 
        '''
        resource_path = '/data/balance/get'
        post_data = {
            "accountID": account_id,
            "userInputs": user_inputs,
            "operationID": operation_id
        }
        return self.authenticated_request(access_token=access_token, user_secret=user_secret, resource_path=resource_path,
                                          post_data=post_data)

    def getTransactions(self, access_token, user_secret, account_id, from_date, to_date, user_inputs=[], operation_id=""):
        '''
        Return the transactions for a specific account
        (`HTTP docs <https://docs.dapi.com/docs/get-transactions>`__)

        :param  str     access_token:    From the exchangeToken method.

        :param  str     user_secret:     From the connect JS response after the user logs in

        :param  str     account_id:      ID from the getAccounts method

        :param  str     from_date:       Format YYYY-MM-DD

        :param  str     to_date:         Format YYYY-MM-DD 
        '''
        resource_path = '/data/transactions/get'
        post_data = {
            "accountID": account_id,
            "fromDate": from_date,
            "toDate": to_date,
            "userInputs": user_inputs,
            "operationID": operation_id
        }
        return self.authenticated_request(access_token=access_token, user_secret=user_secret, resource_path=resource_path,
                                          post_data=post_data)
