import requests
import urllib
import base64

# API keys
api_key = urllib.quote_plus("ePEtVRPmUDQFqqQ5X7iJQENdO")
api_secret = urllib.quote_plus("NoYoe49MQlnyZA7cxcWcb5G3clOrF1ekeqFxPvke1FSygA6PHQ")

# Generate the credentials
combinedKey = api_key + ":" + api_secret
base64Key = base64.b64encode(combinedKey)
print(base64Key)

response = requests.post("https://api.twitter.com/oauth2/token", headers={"Authorization": "Basic " + base64Key, "Content-Type":"application/x-www-form-urlencoded;charset=UTF-8"}, data="grant_type=client_credentials")

responseJSON = response.json()

assert responseJSON[u'token_type'] == u'bearer'
bearerToken = responseJSON[u'access_token']

authHeader = {"Authorization" : "Bearer " + bearerToken}