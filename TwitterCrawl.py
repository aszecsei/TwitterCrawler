import requests
import urllib
import base64
import time
import difflib
import datetime
import csv

import tweepy

import numpy
from sklearn import datasets, svm
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

bots = {}

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

def GenerateLearnSet():
    print "Generating learning set..."
    data = []
    with open("bots.txt", 'r') as botFile:
        for line in botFile:
            try:
                mData = getData(line)
                mData.append(True)
                data.append(mData)
            except:
                pass
    with open("people.txt", 'r') as pplFile:
        for line in pplFile:
            try:
                mData = getData(line)
                mData.append(False)
                data.append(mData)
            except:
                pass
    with open("learn.csv", 'w') as learnFile:
        writer = csv.writer(learnFile)
        for row in data:
            writer.writerow(row)
    return data

# uncomment if generating a learnset
d = GenerateLearnSet()
'''
d = []
t = []
with open("learn.csv", 'r') as learnFile:
    reader = csv.reader(learnFile)
    for row in reader:
        # We have to evaluate everything :(
        md = []
        md.append(int(row[0]))
        md.append(int(row[1]))
        md.append({'True':True}.get(row[2], False))
        md.append(float(row[3]))
        md.append({'True':True}.get(row[4], False))
        md.append({'True':True}.get(row[5], False))
        md.append(int(row[6]))
        md.append(int(row[7]))
        md.append(int(row[8]))
        md.append(int(row[9]))
        d.append(numpy.array(md))
        t.append({'True':1.}.get(row[10], 0.))
'''
dd = numpy.array(d)[:,:-1]
dt = numpy.array(d)[:,-1:]

numRows = len(dd)
numCols = len(dd[0])
for r in dd:
    if not len(r) == numCols:
        raise ValueError("Error! Array is jagged.")
if not numRows == len(dt):
    raise ValueError("Error! Dataset doesn't have the same size as target set.")

clf = svm.SVC()
clf.fit(numpy.array(dd), numpy.array(dt))

def Classify(screenName):
    dd = getData(screenName)
    if not len(dd) == numCols:
        raise ValueError("Error! Classification dataset doesn't have the same size as learning dataset!")
    return clf.predict(numpy.array([dd]))[0]

def AnalyzeFollowers(screenName):
    with open("classified.csv", 'w') as classifyFile:
        cfwriter = csv.writer(classifyFile)
        fList = tweepy.Cursor(api.followers, screen_name=screenName).items(200) if limitTweets else tweepy.Cursor(api.followers, screen_name=screenName).items()
        for friend in fList:
            if not friend.protected:
                isBot = Classify(friend.screen_name)
                print(friend.screen_name + " | " + str(isBot))
                cfwriter.writerow([friend.screen_name, isBot])

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

def AnalyzeSQLTable(sqlfile):
    print "Opening SQL database..."
    conn=sqlite3.connect(sqlfile)
    curse=conn.cursor()
    try:
        curse.execute("create table ourclassify(sname varchar(50) primary key, isbot integer);")
        conn.commit()
        print "Created ourclassify table..."
    except:
        pass
    curse.execute("select * from udata")
    numBot = 0
    numPpl = 0
    for row in curse:
        print "Analyzing @" + row[0] + "..."
        try:
            isBot = Classify(row[0])
            if int(round(isBot)) == 0:
                numPpl += 1
            else:
                numBot += 1
            print row[0] + ": " + ("Bot" if int(round(isBot)) == 1 else "Person")
        except Exception as err:
            print "Error retrieving data for " + row[0] + " | " + str(err)
    print "BOTS: " + str(numBot) + " | PPL: " + str(numPpl)

    '''
        curse2 = conn.cursor()
        # This isn't working for some reason - using Classify instead
        # data = [row[1], row[2], (row[3] == 1), unix_time_millis(datetime.datetime.strptime(row[4], '%Y-%m-%d %H:%M:%S')), (row[5] == 1), (row[6] == 1), row[7], row[8], row[9], row[10]]
        # isBot = clf.predict(numpy.array([data]))[0]
        try:
            isBot = Classify(row[0])
            print "insert into ourclassify values(" + row[0] + "," + str(int(round(isBot))) + ")"
            curse2.execute("insert into ourclassify values(?,?);",(row[0],int(round(isBot))))
            conn.commit()
        except Exception as err:
            print "Error inserting data for " + row[0] + " | " + str(err)
        '''
    conn.close()

# AnalyzeFollowers("uflaz11")
# AnalyzeFollowers("Djawadi_Ramin")
# AnalyzeFollowers("NancyBadillo13")
# AnalyzeSQLTable("udataf.sqlite")
AnalyzeMentions("NathanFillion")
