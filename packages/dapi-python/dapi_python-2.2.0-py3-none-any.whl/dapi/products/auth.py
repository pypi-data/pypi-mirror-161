from dapi.dapi_request import DapiRequest


class Auth(DapiRequest):
    def exchangeToken(self, access_code, connection_id):
        '''
        Exchange connect access code for an acccess Token.
        (`HTTP docs <https://docs.dapi.com/docs/exchange-token>`__)

        :param  str     access_code:     From the connect JS response after the user logs in

        :param  str     connection_id:     From the connect JS response after the user logs in
        '''
        resource_path = '/auth/ExchangeToken'
        post_data = {
            "appSecret": self.client.app_secret,
            "accessCode": access_code,
            "connectionID": connection_id,
        }

        return self.post(resource_path=resource_path, post_data=post_data)

    def delinkUser(self, access_token, user_secret):
        '''
        Unlink or remove a user from Dapi
        (`HTTP docs <https://docs.dapi.com/docs/delink>`__)

        :param  str     access_token:    From the exchangeToken method.

        :param  str     user_secret:     From the connect JS response after the user logs in
        '''
        resource_path = '/users/DelinkUser'
        return self.authenticated_request(access_token=access_token, user_secret=user_secret, resource_path=resource_path)
