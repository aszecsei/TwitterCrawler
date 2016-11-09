import requests
import urllib
import base64
import time
import difflib
import datetime
import csv

import tweepy

# API keys
api_key = urllib.quote_plus("ePEtVRPmUDQFqqQ5X7iJQENdO")
api_secret = urllib.quote_plus("NoYoe49MQlnyZA7cxcWcb5G3clOrF1ekeqFxPvke1FSygA6PHQ")

# Generate the credentials
auth = tweepy.AppAuthHandler(api_key, api_secret)

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

limitTweets = True

bots = {}

def getData(screenName):
    print("Pulling data for " + screenName + "...")
    retweets = 0
    original = 0
    for status in tweepy.Cursor(api.user_timeline,screen_name=screenName,include_rts=True).items(200):
        if status.retweeted or ("RT @" in status.text):
            retweets += 1
        else:
            original += 1
    usr = api.get_user(screenName)
    return [retweets, original, usr.verified, usr.created_at, usr.default_profile, usr.default_profile_image, usr.favourites_count, usr.followers_count, usr.friends_count, usr.listed_count]

def isBot(screenName):
    return True


def Similarity(msg1, msg2):
    return difflib.SequenceMatcher(a=seq1.lower(), b=seq2.lower()).ratio()

def TestSimilarity(msg1, msg2):
    fuzz = 0.9
    return Similarity(msg1, msg2) > fuzz

def AnalyzeFollowers(screenName):
    bots = 0
    people = 0
    fList = tweepy.Cursor(api.followers, screen_name=screenName).items(200) if limitTweets else tweepy.Cursor(api.followers, screen_name=screenName).items(200)
    for friend in fList:
        if not friend.protected:
            print(getData(friend.screen_name))

def GenerateLearnSet():
    data = []
    with open("bots.txt", 'r') as botFile:
        for line in botFile:
            mData = getData(line)
            mData.append("True")
            data.append(mData)
    with open("people.txt", 'r') as pplFile:
        for line in pplFile:
            mData = getData(line)
            mData.append("False")
            data.append(mData)
    with open("learn.csv", 'w') as csvfile:
        dataWriter = csv.writer(csvfile)
        for row in data:
            dataWriter.writerow(row)
    print(data)

GenerateLearnSet()
