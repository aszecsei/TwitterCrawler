import requests
import urllib
import base64
import time
import difflib
import datetime

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

baseURL = "https://api.twitter.com/1.1/"

isBot = {}

def Similarity(msg1, msg2):
    return difflib.SequenceMatcher(a=seq1.lower(), b=seq2.lower()).ratio()

def TestSimilarity(msg1, msg2):
    fuzz = 0.9
    return Similarity(msg1, msg2) > fuzz

def GetFollowerList(screenName, cursor=-1, count=20):
    followerURL = baseURL + "followers/list.json?screen_name=" + screenName + "&cursor=" + str(cursor) + "&count=" + str(count)
    response = requests.get(followerURL, headers=authHeader)
    if response.status_code == 429:
        print("Rate limit exceeded; waiting...")
        time.sleep(15 * 60)
        GetFollowerList(screenName, cursor, count)
    else:
        return response.json()

def RetrieveFollowers(screenName):
    maxPages = 2
    pageCounter = 0
    nextCursor = -1
    followers = []
    while (not nextCursor == 0) and (maxPages > pageCounter):
        pageCounter += 1
        jFollowers = GetFollowerList("aszecsei", nextCursor, 20)
        nextCursor = jFollowers['next_cursor']
        followers += jFollowers['users']
    return followers

def AnalyzeFollowers(screenName):
    followers = RetrieveFollowers(screenName)
    bots = 0
    people = 0
    for user in followers:
        if user['screen_name'] not in isBot:
            # Determine if they're a bot
            if user['verified'] == True:
                # Assume no verified user is a bot
                isBot[user['screen_name']] = False
                people += 1
            else:
                # Look at ratio of followers to following
                ratio = float(user['friends_count']) / float(user['followers_count'])
                if ratio <= 12:
                    # if you're followed by more people than you follow, you're
                    # probably not a bot
                    isBot[user['screen_name']] = False
                    people += 1
                else:
                    if user['protected'] == True:
                        # if you're a protected account, you're probably not a
                        # bot...hopefully?
                        isBot[user['screen_name']] = False
                    else:
                        isBot[user['screen_name']] = True

AnalyzeFollowers("aszecsei")
print(isBot)