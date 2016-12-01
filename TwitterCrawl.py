import requests
import urllib
import base64
import time
import difflib
import datetime

import tweepy

import numpy
from sklearn import datasets, svm, cluster
import matplotlib.pyplot as plt

import sqlite3

# API keys
api_key = urllib.quote_plus("ePEtVRPmUDQFqqQ5X7iJQENdO")
api_secret = urllib.quote_plus("NoYoe49MQlnyZA7cxcWcb5G3clOrF1ekeqFxPvke1FSygA6PHQ")

# Generate the credentials
auth = tweepy.AppAuthHandler(api_key, api_secret)

api = tweepy.API(auth, wait_on_rate_limit=True, retry_count=5, retry_delay=10, retry_errors=set([401, 404, 500, 503]))

limitTweets = True

epoch = datetime.datetime.utcfromtimestamp(0)

def unix_time_millis(dt):
    return (dt - epoch).total_seconds() * 1000.0

def getData(screenName):
    retweets = 0
    original = 0
    time.sleep(0.25)
    sList = tweepy.Cursor(api.user_timeline,screen_name=screenName,include_rts=True).items(200) if limitTweets else tweepy.Cursor(api.user_timeline,screen_name=screenName,include_rts=True).items()
    for status in sList:
        if status.retweeted or ("RT @" in status.text):
            retweets += 1
        else:
            original += 1
    usr = api.get_user(screenName)
    return [retweets, original, usr.verified, unix_time_millis(usr.created_at), usr.default_profile, usr.default_profile_image, usr.favourites_count, float(usr.followers_count) / float(usr.friends_count), usr.listed_count]

def Similarity(msg1, msg2):
    return difflib.SequenceMatcher(a=seq1.lower(), b=seq2.lower()).ratio()

def TestSimilarity(msg1, msg2):
    fuzz = 0.9
    return Similarity(msg1, msg2) > fuzz

def Cluster(sqlfile, includeScore=True,includeSubScores=True, numClusters=50):
    # Open SQL file
    print "Opening SQL database..."
    conn=sqlite3.connect(sqlfile)
    curs=conn.cursor()
    # Create our clustering table if we don't already have one
    try:
        curs.execute("create table ourcluster" + ("score" if includeScore else "") + ("subscore" if includeSubScores else "") + " (sname varchar(50) primary key, cluster integer);")
        conn.commit()
        print "Created ourcluster table..."
    except:
        pass
    # Grab data for each user
    dset = []
    snameset = []
    curs.execute("select udata.sname, rt, orig, verif, created, def, defi, fac, foc, frc, lic" + (", score" if includeScore else "") + (", content, temporal, network, friend, sentiment, user" if includeSubScores else "") + " from udata, botornotscore on udata.sname=botornotscore.sname where score notnull")
    for row in curs:
        mRow = list(row[1:])
        mRow[3] = unix_time_millis(datetime.datetime.strptime(mRow[3], '%Y-%m-%d %H:%M:%S'))
        dset.append(mRow)
        snameset.append(row[0])
    k_means = cluster.KMeans(n_clusters=numClusters)
    k_means.fit(numpy.array(dset))
    # put cluster into table
    for i in range(0, len(snameset)):
        print "insert into ourcluster values(" + snameset[i] + "," + str(k_means.labels_[i]) + ")"
        try:
            curs.execute("insert into ourcluster" + ("score" if includeScore else "") + ("subscore" if includeSubScores else "") + " values(?,?);",(snameset[i],str(k_means.labels_[i])))
        except:
            pass
    conn.commit()
    conn.close()
'''
def AnalyzeMentions(screenName, forceLinks=False):
    tList = tweepy.Cursor(api.search, q=("@" + screenName + (" filter:links" if forceLinks else ""))).items(200)
    numBots = 0
    numPpl = 0
    for tweet in tList:
        isBot = Classify(tweet.user.screen_name)
        print tweet.user.screen_name + (": BOT" if int(round(isBot)) == 1 else ": PERSON")
        if int(round(isBot)) == 1:
            numBots += 1
        else:
            numPpl += 1
    print "BOTS: " + str(numBots) + " | PPL: " + str(numPpl)

def AnalyzeHashtags(htag, forceLinks=False):
    tList = tweepy.Cursor(api.search, q=("#" + htag + (" filter:links" if forceLinks else ""))).items(200)
    numBots = 0
    numPpl = 0
    for tweet in tList:
        isBot = Classify(tweet.user.screen_name)
        print tweet.user.screen_name + (": BOT" if int(round(isBot)) == 1 else ": PERSON")
        if int(round(isBot)) == 1:
            numBots += 1
        else:
            numPpl += 1
    print "BOTS: " + str(numBots) + " | PPL: " + str(numPpl)
'''

Cluster("udataf3.sqlite")
