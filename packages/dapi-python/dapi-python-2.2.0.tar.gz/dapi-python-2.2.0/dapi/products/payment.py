from dapi.dapi_request import DapiRequest


class Payment(DapiRequest):

    def getBeneficiaries(self, access_token, user_secret, user_inputs=[], operation_id=""):
        '''
        Return the user's transfer beneficiaries.
        (`HTTP docs <https://docs.dapi.com/docs/get-beneficiaries>`__)

        :param  str     access_token:    From the exchangeToken method.

        :param  str     user_secret:     From the connect JS response after the user logs in
        '''

        post_data = {
            "userInputs": user_inputs,
            "operationID": operation_id
        }

        resource_path = '/payment/beneficiaries/get'
        return self.authenticated_request(access_token=access_token, user_secret=user_secret, resource_path=resource_path,
                                          post_data=post_data)

    def createTransfer(self, access_token, user_secret, transfer_data, user_inputs=[], operation_id=""):
        '''
        Initiate a transfer.
        (`HTTP docs <https://docs.dapi.com/docs/create-transfer>`__)

        :param  str     access_token:        From the exchangeToken method.

        :param  str     user_secret:         From the connect JS response after the user logs in

        :param  dict    transfer_data:       Dictionary containing the details for the transfer, senderID, receiverID, amount, remark
        '''
        post_data = {
            **transfer_data,
            "userInputs": user_inputs,
            "operationID": operation_id
        }
        resource_path = '/payment/transfer/create'
        return self.authenticated_request(access_token=access_token, user_secret=user_secret, resource_path=resource_path,
                                          post_data=post_data)

    def transferAutoflow(self, access_token, user_secret, transfer_autoflow_data, user_inputs=[], operation_id=""):
        '''
        Initiate a transfer.
        (`HTTP docs <https://docs.dapi.com/docs/create-transfer>`__)

        :param  str     access_token:        From the exchangeToken method.

        :param  str     user_secret:         From the connect JS response after the user logs in

        :param  dict    transfer_autoflow_data:       Dictionary containing the details for the amount, senderID, amount, remark, and beneficiary
        '''
        post_data = {
            **transfer_autoflow_data,
            "userInputs": user_inputs,
            "operationID": operation_id
        }
        resource_path = '/payment/transfer/autoflow'
        return self.authenticated_request(access_token=access_token, user_secret=user_secret, resource_path=resource_path,
                                          post_data=post_data)

    def createBeneficiary(self, access_token, user_secret, beneficiary_data, user_inputs=[], operation_id=""):
        '''
        Create a beneficiary
        (`HTTP docs <https://docs.dapi.com/docs/create-beneficiaries>`__)

        :param  str     access_token:        From the exchangeToken method.

        :param  str     user_secret:         From the connect JS response after the user logs in

        :param  dict    beneficiary_data:    Dictionary containing the details for the beneficiary to be created
        '''
        post_data = {
            **beneficiary_data,
            "userInputs": user_inputs,
            "operationID": operation_id
        }
        resource_path = '/payment/beneficiaries/create'
        return self.authenticated_request(access_token=access_token, user_secret=user_secret, resource_path=resource_path,
                                          post_data=post_data)
