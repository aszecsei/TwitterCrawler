import re
import sqlite3
import os  
import botornot
import requests
import urllib
import base64
import time
import difflib
import datetime
import csv

import tweepy


twitter_app_auth = {
    'consumer_key': '5Ef1eDVXx6pLsXsC1CSPzMuSz',
    'consumer_secret': 'XvX96j82NFPnA74Wrdc8vTpHRi9Il4xAYlVIHw0qIZbUqEwp3L',
    'access_token': '800791486228877313-z8tgC5j7rPdK18CBRGtBT2ZBL9aW1xN',
    'access_token_secret': 'DzKW4y3odgDpfMN6Dd6ixgebRdlzstuzNHbLoNj9j0AUg',
  }
bon = botornot.BotOrNot(**twitter_app_auth)
#def getAllTweets(sqlfile):
   
#def getBotTweets(sqlfile):
    
#def getUserTweets(sqlfile):
   
#def getVerifiedTweets(sqlfile):
    
#def getAllAtTweets(sqlfile):
   
#def getBotAtTweets(sqlfile):
    
#def getUserAtTweets(sqlfile):
    
#def getVerifiedAtTweets(sqlfile):
    
#def getAllAtNTweets(sqlfile,N,o=""):
      
#def getBotAtNTweets(sqlfile,N,o=""):
    
#def getUserAtNTweets(sqlfile,N,o=""):
    
#def getVerifiedAtNTweets(sqlfile,N,o=""):
   
#def getAllNAtTweets(sqlfile):
    
#def getBotNAtTweets(sqlfile):
    
#def getUserNAtTweets(sqlfile):
   
#def getVerifiedNAtTweets(sqlfile):
   
#def getAll(sqlfile):
    
#def getBot(sqlfile):
    
#def getVerified(sqlfile):
   
#def getUser(sqlfile):
    
#def getFollowers(sqlfile,followee):
   
#def getFollowing(sqlfile,follower):
   
#def nbotAtVnUserAtV_Ratio(sqlfile,N,o=""):
  
#def getAllFollowersNam(sqlfile):
conn=sqlite3.connect("udataf.sqlite")
   
def getUlist(sqlfile):
    conn=sqlite3.connect(sqlfile)
    cur=conn.cursor()
    cur.execute("select sname from udata;")
    uli=cur.fetchall()
    Ulist=[]
    for u in uli:
        Ulist.append(u[0])
    return Ulist
    
def useBotOrNot(Ulist):
    cur=conn.cursor()
    try:
        cur.execute("create table botornotscore(sname varchar(50) primary key, score float);")
        conn.commit()
    except:
        conn.rollback()
    results=bon.check_accounts_in(Ulist)
    sc={}
    for i in results:
        try:
            sc.update({i[0]:i[1]['score']})
            try:
                cur=conn.cursor()
                cur.execute("insert into botornotscore values(?,?);",(i[0],i[1]['score']))
                conn.commit()
            except:
                conn.rollback()
        except:
            print(i)
    return sc
def binBotOrNotScore(scoreDict):
    bin={0:{},10:{},20:{},30:{},40:{},50:{},60:{},70:{},80:{},90:{},100:{}}
    cnts=[0,0,0,0,0,0,0,0,0,0,0]
    for x in scoreDict:
        i=scoreDict[x]
        print(x)
        print(i)
        print(bin[int(i*10)*10])
        bin[int(i*10)*10].update({x:i})
        ii=int(i*10)
        cnts[ii]+=1
    for i in range(0,11):
        bin[i*10].update({"#count#":cnts[i]})
    return bin

api_key = urllib.quote_plus("5Ef1eDVXx6pLsXsC1CSPzMuSz")
#api_key = urllib.quote_plus("vJAZyChsolI3ZnHrgW1gJjEx6")
api_secret = urllib.quote_plus("XvX96j82NFPnA74Wrdc8vTpHRi9Il4xAYlVIHw0qIZbUqEwp3L")
#api_secret = urllib.quote_plus("fpHFdjgG8hN72M9mKJigLHAZXYXfWqEVDf0LfIPrI4gEGMAj1w")

# Generate the credentials
auth = tweepy.OAuthHandler(api_key, api_secret)
auth.set_access_token("800791486228877313-z8tgC5j7rPdK18CBRGtBT2ZBL9aW1xN", "DzKW4y3odgDpfMN6Dd6ixgebRdlzstuzNHbLoNj9j0AUg")
#auth.set_access_token("796463566840688640-Zj0sSWU7Hu7JmjvaTC5RZhhqy7oyesG", "S7cYtJwbcGTR4J7sY6z83I1o3Mm3XLKM8LxqZPuVNnBzo")
api = tweepy.API(auth, wait_on_rate_limit=True)

limitTweets = True

def getats(text):
    ind=text.find("@")
    ats=""
    while ind!=-1:
        #print(text[ind:])
        found=re.match("@[a-zA-Z0-9_]+",text[ind:])
        if(found!=None):
            #print(text[ind:found.end()+ind])
            ats=ats+text[ind:found.end()+ind]
        ind=text.find("@",ind+1)
    return ats
def regrabtweets(ulist):
    for user in ulist:
        getData(user)
def getData(screenName):
    print("Pulling data for " + screenName + "...")
    retweets = 0
    original = 0
    sList = tweepy.Cursor(api.user_timeline,screen_name=screenName,include_rts=True).items(100)
    #print(sList)
    b=0
    while b<5:
        try:    
            for status in sList:
                print(status)
                hashes=""
                zz=status._json["entities"]['hashtags']
                for yy in zz:
                    hashes=hashes+"#"+yy["text"]   
                zz=status._json["entities"]['user_mentions']
                ats=""
                for yy in zz:
                    ats=ats+"@"+yy["screen_name"]
                z=xx._json["entities"]['urls']
                urls=""
                for yy in zz:
                    urls=urls+"\n"+yy["expanded_url"]      
                ba=0
                if status.retweeted or ("RT @" in status.text):
                    retweets += 1
                    ba=1
                else:
                    original += 1
                bb=0
                while bb<5:
                    try:
                        conn=sqlite3.connect("udataf.sqlite")
                        curse=conn.cursor()
                        curse.execute("insert into Tweets (sname,tweet,retweet) values(?,?,?,?,?,?);",(screenName,status.text,ba,hashes,ats,urls))
                        conn.commit()
                        conn.close()
                        bb=10
                    except Exception as e:
                        try:
                            conn.rollback()
                            conn.close()
                        except Exception as ee:
                            pass
                        print("woops ",e)
                        bb+=1
                        time.sleep(12)
                    time.sleep(.15)
            b=10
        except Exception as e:
            ind1=ind2
            print("waiting ",e)
            time.sleep(b*4+1)
            b+=1
    return [retweets, original]
def recreatet():
    conn=sqlite3.connect("udataf.sqlite")
    curse=conn.cursor()
    try:
        curse.execute("CREATE TABLE Followers(follower_twid varchar(50) references Accounts(twid), followee_twid varchar(50), primary key(follower_twid, followee_twid));")
    except:
        pass
    try:
        curse.execute("CREATE TABLE Tweets ( twtid INTEGER PRIMARY KEY AUTOINCREMENT, sname varchar(50), tweet TEXT, retweet INTEGER CHECK(retweet=0 or retweet=1),hashtags TEXT,ats TEXT, urls TEXT );")
    except:
        pass
    try:
        cur.execute("create table botornotscore(sname varchar(50) primary key, score float);")    
    except:
        pass
    try:
        curse.execute("CREATE TABLE udata(sname varchar(50) primary key, rt int, orig int, verif boolean, created datetime, def boolean, defi boolean, fac int,foc int, frc int, lic int);")
    except:
        pass
    try:
        cur.execute("create table ourclassify(sname varchar(50) primary key, isbot boolean);")  
    except:
        pass        
    conn.commit()
    conn.close()
def usermantioned(ats,at):
    if at[0]!="@":
        at="@"+at
    fnd=ats.find(at)
    return fnd!=-1
def hashtagused(hashtags,hashtag):
    if hashtag[0]!="#":
        hashtag="#"+hashtag
    fnd=hashtags.find(hashtag)
    return fnd!=-1
def domainused(urls,domain):
    lis=urls.split("\n")
    for ur in lis:
        ind=ur.find("/",ur.find("."))
        fnd=ur[:ind].find(domain)
        if fnd!=-1:
            return True
    return False
def grabtweetstuff(usr):
    stuff=getData(usr.screen_name)
    return (usr.screen_name,stuff[0],stuff[1], usr.verified, usr.created_at, usr.default_profile, usr.default_profile_image, usr.favourites_count, usr.followers_count, usr.friends_count, usr.listed_count)
def getdatafrom(depth,ulist):
    data=[]
    print(depth)
    for user in ulist:
        bb=0
        while bb<10:
            try:
                conn=sqlite3.connect("udataf.sqlite")
                curse=conn.cursor()
                curse.execute("select * from udata where sname=?;",(user.screen_name,))
                data=curse.fetchall()
                conn.commit()
                conn.close()
                bb=10
            except Exception as e:
                try:
                    conn.rollback()
                    conn.close()
                except Exception as ee:
                    pass
                print("woops ",e)
                bb+=1
                time.sleep(12)
        if data==[]:
            try:
                data=grabtweetstuff(user)
            except Exception as e:
                print("oops "+str(user.screen_name)) 
                continue
            bb=0
            while bb<5:
                try:
                    conn=sqlite3.connect("udataf.sqlite")
                    curse=conn.cursor()
                    curse.execute("insert into udata values(?,?,?,?,?,?,?,?,?,?,?);",data)
                    conn.commit()
                    conn.close()
                    bb=10
                except Exception as e:
                    try:
                        conn.rollback()
                        conn.close()
                    except Exception as ee:
                        pass
                    print("woops ",e)
                    bb+=1
                    time.sleep(12)
            if depth>0:
                nl=[]
                sList = tweepy.Cursor(api.followers, screen_name=user.screen_name).items(5)
                b=0
                while b<5:
                    try:                
                        for usr in sList:
                            nl.append(usr)             
                            print(usr.screen_name)
                            bb=0
                            while bb<5:
                                try:
                                    conn=sqlite3.connect("udataf.sqlite")
                                    curse=conn.cursor()
                                    curse.execute("insert into Followers values(?,?);",(usr.screen_name,user.screen_name))
                                    conn.commit()
                                    conn.close()
                                    bb=10
                                except Exception as e:
                                    try:
                                        conn.rollback()
                                        conn.close()
                                    except Exception as ee:
                                        pass
                                    print("woops ",e)
                                    bb+=1
                                    time.sleep(12)
                                time.sleep(.15)
                        b=10
                    except Exception as e:
                        print("waiting ",e)
                        time.sleep(b*4+1)
                        b+=1
                getdatafrom(depth-1,nl)
                    
                

def gather():
    f=open("userstart.txt","r")
    startl=[]
    for l in f:
        l=l[:-1]
        print(l)
        try:
            startl.append(api.get_user(l))
        except:
            print("not found: ",l)
        time.sleep(.2)
    #cur=conn.cursor()
    
    ##udict=useBotOrNot(ourbots)
    ##sc=binBotOrNotScore(udict)
    #print(getData(ourbots[0]))
    getdatafrom(3,startl)
