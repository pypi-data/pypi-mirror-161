"""
This is a Python wrapper for interacting with the OpMan HTTP REST API. This module should do nothing other than
facilitate making calls to, and receiving responses from, that API. The OpMan API should be exclusively responsible
for all OpMan related logic.
"""
import urllib3
import json
import time
# import google.auth.crypt
# import google.auth.jwt
from urllib.parse import urlencode
from RecastPy.aws import secrets_manager

OPMAN_API_BASE_URL = "https://ly231vyas0.execute-api.us-east-1.amazonaws.com/staging"


# def _generate_jwt(
#         sa_keyfile,
#         sa_email='recast-opman@recast-opman.iam.gserviceaccount.com',
#         # audience='9590044456-tjbpgdpbpa33goisbjg3q1rlgahfj6tn.apps.googleusercontent.com',
#         audience='https://www.googleapis.com/oauth2/v4/token',
#         scope='openid',
#         expiry_length=3600):
#
#     """Generates a signed JSON Web Token using a Google API Service Account."""
#
#     now = int(time.time())
#
#     keyfile_json = json.loads(sa_keyfile)
#     kid = keyfile_json.get('private_key_id')
#
#     # build payload
#     payload = {
#         'kid': kid,
#         'iat': now,
#         'exp': now + expiry_length,
#         'nbf': now + expiry_length,
#         'iss': sa_email,
#         # 'iss': "https://accounts.google.com",
#         'aud':  audience,
#         'sub': sa_email,
#         'email': sa_email,
#         'scope': 'openid'
#     }
#
#     # sign with keyfile
#     key = json.loads(sa_keyfile)['private_key']
#     signer = google.auth.crypt.RSASigner.from_string(key)
#     jwt = google.auth.jwt.encode(signer, payload)
#
#     return jwt
#
#
# def _get_id_token(jwt):
#     http = urllib3.PoolManager()
#
#     url = f"https://www.googleapis.com/oauth2/v4/token"
#
#     headers = {
#         'Content-Type': 'application/x-www-form-urlencoded'
#     }
#
#     fields = {
#         'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
#         'assertion': jwt
#     }
#
#     response = http.request(
#         method='POST',
#         url=url,
#         headers=headers,
#         body=urlencode(fields)
#     )
#
#     response_data = response.data.decode('utf8').replace("'", '"')
#
#     token_json = json.loads(response_data)
#     print(token_json)
#
#     return token_json.get('access_token').rstrip('.')
#
#
# def _get_auth_token():
#     # get the service account key
#     key = secrets_manager.get_secret_value("prod/google/opman_service_account", "key")
#
#     # generate a jwt with the service account
#     jwt = _generate_jwt(key)
#
#     # get the auth token from the jwt
#     token = _get_id_token(jwt)
#
#     # return the auth token
#     return jwt.decode("utf-8")


# def _get_api_key():
#     # get the service account key
#     key = secrets_manager.get_secret_value("prod/google/opman_service_account", "key")


# def _make_opman_api_request(method, endpoint, fields=None):
#     http = urllib3.PoolManager()
#
#     url = f"{OPMAN_API_BASE_URL}{endpoint}"
#
#     auth = f"Bearer {_get_auth_token()}"
#     print(auth)
#
#     response = http.request(
#         method=method,
#         url=url,
#         headers={
#             'Authorization': auth,
#             'Cache-Control': 'no-cache',
#             'Content-Type': 'application/json',
#             'Accept': 'application/json'
#         },
#         fields=fields
#     )
#
#     return json.loads(response.data.decode('utf-8'))


if __name__ == '__main__':
    pass
    # token = _get_auth_token()
    # print(token)

    # response = _make_opman_api_request('GET', '/jobs')
    # print(response)
