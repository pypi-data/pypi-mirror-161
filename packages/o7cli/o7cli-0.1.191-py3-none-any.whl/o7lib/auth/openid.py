
# Where to find Open Id configuration
# https://[base-server-url]/.well-known/openid-configuration
# example: https://accounts.google.com/.well-known/openid-configuration
# example: https://cognito-idp.ca-central-1.amazonaws.com/ca-central-1_vdyge4T9V/.well-known/openid-configuration


import json
import requests
import os
import logging
import jwt
import pprint
import uuid
import urllib

# Key Pair of JWKS url for each known iss
urlJwksForIss = {}
urlConfigForIss = {}

#*************************************************
#
#*************************************************
class OpenIdError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return "Open Id Error: %s" % self.value


#*************************************************
#
#*************************************************
class OpenId():

    #*************************************************
    #
    #*************************************************
    def __init__(self,
        provider = None,
        clientId = None,
        clientSecret = None,
        callback = None,
        providerConfig=None,
        scope = 'openid',
        nonce = 'nonce'
    ):

        self.provider = provider
        if self.provider is None: self.provider = os.getenv('OIDC_PROVIDER', default=None)
        if self.provider is None: raise OpenIdError('No OIDC_PROVIDER found')

        self.clientId = clientId
        if self.clientId is None: self.clientId = os.getenv('OIDC_CLIENT_ID', default=None)
        if self.clientId is None: raise OpenIdError('No OIDC_CLIENT_ID found')

        self.clientSecret = clientSecret
        if self.clientSecret is None: self.clientSecret = os.getenv('OIDC_CLIENT_SECRET', default=None)
        if self.clientSecret is None: raise OpenIdError('No OIDC_CLIENT_SECRET found')

        self.callback = callback
        if self.callback is None: self.callback = os.getenv('OIDC_CALLBACK', default=None)
        if self.callback is None: raise OpenIdError('No OIDC_CALLBACK found')

        self.providerConfig = providerConfig
        if self.providerConfig is None: self.discover()

        self.scope = scope
        self.nonce = nonce

        self.verifyConfig()


    #*************************************************
    #  Ensure we have all required
    #*************************************************
    def verifyConfig(self):

        if 'authorization_endpoint' not in self.providerConfig:
            raise OpenIdError('Provider Config is missing: authorization_endpoint')

        if 'token_endpoint' not in self.providerConfig:
            raise OpenIdError('Provider Config is missing: authorization_endpoint')


    #*************************************************
    #
    #*************************************************
    def discover(self):
        url = f'https://{self.provider}/.well-known/openid-configuration'
        print(f'discover: url -> {url}')

        r = requests.get(url=url)

        if r.status_code != 200 :
            print(f'Got Error Status Code: {r.status_code}')
            print(f'Error Message: {r.text}')
            raise OpenIdError('Discovery endpoint is not reponding')

        self.providerConfig = r.json()
        print(f'discover Rx Info: ->')
        pprint.pprint(self.providerConfig)


    #*************************************************
    #
    #*************************************************
    def loginUrl(self):


        # Generate random cookie
        nonce = str(uuid.uuid4())
        print(f'{self.nonce}: {nonce}')

        authEndpoint = self.providerConfig['authorization_endpoint']
        query = {
            'response_mode' : 'query',  # or form_post
            'response_type' : 'code', # or id_token
            'scope' : self.scope,
            'client_id' : self.clientId,
            'redirect_uri' : self.callback,
            self.nonce : nonce
        }

        qs = urllib.parse.urlencode(query)
        url = f'{authEndpoint}?{qs}'

        print(f'url: {url}')

        return url, nonce

    #*************************************************
    #  Exchanges code for tokens using backend secured channel
    # Ref : https://auth0.com/docs/api/authentication#authorization-code-flow45
    #*************************************************
    def getTokens(self, code):

        headers = {
            'content-type' : 'application/x-www-form-urlencoded',
            'accept' : 'application/json'
        }

        params = {
            'grant_type' : 'authorization_code',
            'client_id' : self.clientId,
            'client_secret' : self.clientSecret,
            'redirect_uri' : self.callback,
            'code' : code
        }

        auth = requests.auth.HTTPBasicAuth(self.clientId, self.clientSecret)

        print("TX headers -> ", headers)
        print("TX params -> ", params)
        req = requests.post(
            url=self.providerConfig['token_endpoint'],
            data=params,
            params=params,
            headers=headers,
            auth = auth
        )
        print("req.url -> ", req.url)
        print("req.headers -> ", req.headers)
        print("RX test -> ", req.text)

        if req.status_code != 200 :
            print(f'Got Error Status Code: {req.status_code}')
            print(f'Error Message: {req.text}')
            raise OpenIdError('Token endpoint error')

        tokens = req.json()
        print(f'<------ TOKENS ------------------->')
        pprint.pprint(tokens)
        print(f'<--------------------------------->')

        return tokens

    #*************************************************
    #  Validate Id Tokens and returns claims
    #*************************************************
    def validateIdToken(self, idToken, nonce):

        jwksClient = jwt.PyJWKClient(self.providerConfig['jwks_uri'])
        pubKey = jwksClient.get_signing_key_from_jwt(idToken)
        claims = jwt.decode(
            idToken,
            pubKey.key,
            algorithms=["RS256"],
            audience=self.clientId,
            issuer = self.providerConfig['issuer'],
            require = ['exp', 'iat', 'aud', 'iss'],
            verify_signature = True,
            verify_aud = True,
            verify_iss = True,
            verify_exp = True,
            verify_iat = True
        )

        print(f'<------ TOKEN CLAIMS ------------------->')
        pprint.pprint(claims)
        print(f'<--------------------------------->')

        # Verify nonce
        if claims['nonce'] != nonce: raise OpenIdError('Nonce is not matching')

        return claims


#*************************************************
#
#*************************************************
if __name__ == "__main__":

    # Usage Example

    logging.basicConfig(level=logging.DEBUG)
