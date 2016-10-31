# this contains an interface for the twitter API

import requests
import urllib
import base64
import time

class TwitterAPI(object):
    def __init__(self, api_key, api_secret):
        combinedKey = api_key + ":" + api_secret
        base64Key = base64.b64encode(combinedKey)
        response = requests.post("https://api.twitter.com/oauth2/token", headers={"Authorization": "Basic " + base64Key, "Content-Type":"application/x-www-form-urlencoded;charset=UTF-8"}, data="grant_type=client_credentials")
        responseJSON = response.json()
        assert responseJSON[u'token_type'] == u'bearer'
        bearerToken = responseJSON[u'access_token']
        self.authHeader = {"Authorization" : "Bearer " + bearerToken}
        self.baseURL = "https://api.twitter.com/1.1/"

    def getFollowerList(screenName, cursor=-1, count=20):
        followerURL = baseURL + "followers/list.json?screen_name=" + screenName + "&cursor=" + str(cursor) + "&count=" + str(count)
        response = requests.get(followerURL, headers=authHeader)
        if response.status_code == 429:
            print("Rate limit exceeded; waiting...")
            time.sleep(15 * 60)
            GetFollowerList(screenName, cursor, count)
        else:
            return response.json()

    def getFollowers(screenName, maxPages=2):
        pageCounter = 0
        nextCursor = -1
        followers = []
        while (not nextCursor == 0) and (maxPages > pageCounter):
            pageCounter += 1
            jFollowers = GetFollowerList("aszecsei", nextCursor, 20)
            nextCursor = jFollowers['next_cursor']
            followers += jFollowers['users']
        return followers
