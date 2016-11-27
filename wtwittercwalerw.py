#some of these may not be needed, i forget which
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
import matplotlib.pyplot as plt
import numpy as np
import plotly.plotly as py
import tweepy
import random
import networkx as nx     


twitter_app_auth = {
    'consumer_key': 'vyk10RI2aIr0a0oMplmK2Ug5t',
    'consumer_secret': '5GML863VtjeQyAsCsXOfiu2s0ACKbuQn8YoMPwRmeXYTNL6Oez',
    'access_token': '801556602096668673-xSVbUzobLk3mVtfQ4db4nUQZB7HWDXL',
    'access_token_secret': '6JGmYXUpdJyTwCsktUuQaLps2qdU9wmaaaEjiqnt6CNcC',
    'wait_on_ratelimit':True
  }
bon = botornot.BotOrNot(**twitter_app_auth)
#sorts a list of tups by the numerical variable in index i (ascending)
def sorttup(thirds,i):
    l = []
    e = []
    g = []
    if len(thirds) > 1:
        temp = thirds[0][i]
        for tup in thirds:
            if tup[i] > temp:
                l.append(tup)
            if tup[i] == temp:
                e.append(tup)
            if tup[i] < temp:
                g.append(tup)
        return sorttup(g,i)+e+sorttup(l,i)
    else:
        return thirds
#sorts a list of tups by the numerical variable in index i (descending)
def sorttupr(thirds,i):
    l = []
    e = []
    g = []
    if len(thirds) > 1:
        temp = thirds[0][i]
        for tup in thirds:
            if tup[i] < temp:
                l.append(tup)
            if tup[i] == temp:
                e.append(tup)
            if tup[i] > temp:
                g.append(tup)
        return sorttupr(g,i)+e+sorttupr(l,i)
    else:
        return thirds
#makes scatter plot y axis is botornot score and x is a random float in range of [0.0,1.0]. marker is blue if our classifier classified account as not a bot, and red if it classified it as a bot
def scatgraphbotvscore(sqlfile,name):
    conn=sqlite3.connect(sqlfile)
    cur=conn.cursor()
    cur.execute("select s.sname,o.isbot,s.score from ourclassify as o, botornotscore as s where o.sname=s.sname;")
    data=cur.fetchall()
    ourbots=[]
    xb=[]
    #cb=[]
    ournots=[]
    xn=[]
    #cn=[]
    for i in range(0,100):
        print(data[i][0]+":"+str(i)+":"+str(data[i][2])+":"+str(data[i][1]))
        if data[i][1]==0:
            ournots.append(data[i][2])
            xn.append(random.random())
        elif data[i][1]==1:
            ourbots.append(data[i][2])
            xb.append(random.random())
    bg=plt.subplot(191)
    bg.scatter(xn,ournots,s=25,c=(0,0,1,.5),marker="s")
    bg.scatter(xb,ourbots,s=25,c=(1,0,0,.5),marker="o")
    plt.savefig(name+".pdf")
    #plt.close()
#non-directional node graph where nodes are accounts and edges represents a if one account is following the other. nodes are a specta between red and blue based on the botornot score. the RGB formula is (score,0,1.0-score). (ex. if score is .3, the color (in RGB) would be (.3,0,.7)
def nodegraph(sqlfile,name):
    conn=sqlite3.connect(sqlfile)
    cur=conn.cursor()
    cur.execute("select f.followee_twid,f.follower_twid from Followers as f,(select distinct f.sname,s.score from udata as f, botornotscore as s, ourclassify as i where f.sname=s.sname and f.sname=i.sname) as s,(select distinct f.sname from udata as f, botornotscore as s, ourclassify as i where f.sname=s.sname and f.sname=i.sname) as s2 where f.followee_twid=s.sname and f.follower_twid=s2.sname;")
    data=cur.fetchall()
    cur.execute("select distinct f.sname,s.score,i.isbot from udata as f, botornotscore as s, ourclassify as i where f.sname=s.sname and f.sname=i.sname;")
    data2=cur.fetchall()
    g=nx.Graph()
    c={}
    #m={}
    stars={}
    ib={}
    for n in data2:
        stars.update({str(n[0]):[str(n[0])]})
        x=n[1]
        if x==None:
            x=0.0
        c.update({str(n[0]):(x,0,1.0-x)})
        ib.update({str(n[0]):n[2]})
        #if n[2]==0:
            #c.update({str(n[0]):(0,0,1)})
        #else:
            #c.update({str(n[0]):(1,0,0)})
        #if n[1]==None:
            #m.update({str(n[0]):"o"})
        #elif n[1]>.75:
            #m.update({str(n[0]):"*"})
        #elif n[1]<.25:
            #m.update({str(n[0]):"s"})
        #else:
            #m.update({str(n[0]):"o"})
    for tup in data:
        try:
            stars[str(tup[0])].append(str(tup[1]))
        except:
            stars.update({str(tup[0]):[str(tup[0]),str(tup[1])]})
    #xx=0
    #nstars=[]
    for i in stars:
        if len(stars[i])>1:
            g.add_star(stars[i])
            #nstars.append((stars[i],len(stars[i])))
            #xx+=1
            #if xx>100:
                #break
    gs=list(nx.connected_component_subgraphs(g))
    xxxx=0
    for lis in gs:
        print(str(xxxx)+":"+str(lis.edges()))
        xxxx=+1
    print(len(gs))
    #mark=[]
    color=[]
    ecolor=[]
    #p={}
    xx=0.0
    for n in gs[0].nodes():
        #print(n)
        #mark.append(m[n])
        color.append(c[n])
        #p.update({n:(xx,0)})
        xx+=0.1
    for e in gs[0].edges():
        if ib[e[0]]==1 and ib[e[1]]==1:
            ecolor.append((0,0,1))
        elif ib[e[0]]==1 or ib[e[1]]==1:
            ecolor.append((.5,0,.5))
        else:
            ecolor.append((1,0,0))
    print(color)
    p=generatep(sqlfile,gs[0].edges())
    #print(mark)
    print len(gs[0].nodes())
    nx.draw(gs[0],pos=p,node_size=50,with_labels=False,node_color=color,edge_color=ecolor)
    plt.savefig(name+".pdf")
def maxi(lists):
    max=0
    ind=1
    for list in lists[1:]:
        if len(list)>len(lists[max]):
            max=ind
        ind+=1
    return max
def sortlist(lists):
    nlists=[]
    for list in lists:
        nlists.append(list)
    lists=[]
    while len(nlists)>0:
        ind=maxi(nlists)
        list=nlists.pop(ind)
        lists.append(list)
    return lists

def generatep(sqlfile,edglist):
    conn=sqlite3.connect(sqlfile)
    cur=conn.cursor()
    cur.execute("select followee_twid,follower_twid from Followers;")
    el=cur.fetchall()
    stars={}
    for tup in el:
        if ((str(tup[0]),str(tup[1])) in edglist) or ((str(tup[1]),str(tup[0])) in edglist):
            try:
                stars[str(tup[0])].append(str(tup[1]))
            except:
                stars.update({str(tup[0]):[str(tup[0]),str(tup[1])]})  
    nstars=[]
    for star in stars:
        nstars.append(stars[star])
    stars=sortlist(nstars)
    for star in stars:
        print(star)
        #print len(star)
    p={}
    clockhand={}
    maxx=0
    maxy=0
    minx=0
    miny=0
    maxxt=0
    maxyt=0
    minxt=0
    minyt=0
    cnt=0
    for star in stars:
        if cnt%4==0:
            if maxxt>maxx:
                maxx=maxxt+10
            if maxyt>maxy:
                maxy=maxyt+10
            if minxt<minx:
                minx=minxt-10
            if minyt<miny:
                miny=minyt-10
            maxxt=0
            maxyt=0
            minxt=0
            minyt=0
        if star[0] in p:
            #p[star[0]]=(2*p[star[0]][0],2*p[star[0]][1])
            pass
        else:
            if cnt%4==0:
                r=0
                if maxx>=maxy:
                    r=maxx
                else:
                    r=maxy
                p.update({star[0]:calcP(0,r)})
            elif cnt%4==1:
                r=0
                if (-minx)>=maxy:
                    r=-minx
                else:
                    r=maxy
                p.update({star[0]:calcP(1,r)})
            elif cnt%4==2:
                r=0
                if minx<=miny:
                    r=-minx
                else:
                    r=-miny
                p.update({star[0]:calcP(2,r)})
            elif cnt%4==3:
                r=0
                if maxx>=(-miny):
                    r=maxx
                else:
                    r=-miny
                p.update({star[0]:calcP(3,r)})
            cnt+=1
            
        l=len(star[1:])        
        c=0
        non=[]
        ratios={}
        for n in star[1:]:
            if n not in p:
                xxx=calculatep(p[star[0]],c,l)
                if xxx[0]>maxx:
                    maxx=xxx[0]
                if xxx[1]>maxy:
                    maxy=xxx[1]
                if xxx[0]<minx:
                    minx=xxx[0]
                if xxx[1]<miny:
                    miny=xxx[1]
                p.update({n:(xxx[0],xxx[1])})
                clockhand.update({n:(xxx[2],xxx[3])})
                ratios.update({n:float(xxx[2])/float(xxx[3])})
                non.append(n)
            c+=1
    print(p)
    return p
def calcP(q,r):
    theta=random.random()*np.pi/2+q*np.pi/2
    x=r*np.sin(theta)
    y=r*np.cos(theta)
    return (x,y)
def calculatep(center,cur,tot):
    PI=np.pi
    sin=np.sin
    cos=np.cos
    ratio=float(cur)/float(tot)
    theta=PI*2*ratio
    x=10*sin(theta)
    y=10*cos(theta)
    return (x+center[0],y+center[1],cur,tot)
#nodegraph("udataf3.sqlite","te")
    #return stars
nodegraph("udataf3.sqlite","te")
#this makes a bar graph of 100 accounts (either the top 100 highest botornotscore, mode=0, or the 100 lowest botornot score, mode=1, or 100 at random. bars are colored red for accounts classified as bots, and blue if not.
def bargraphbotvscore(sqlfile,name,mode=0):
    conn=sqlite3.connect(sqlfile)
    cur=conn.cursor()
    cur.execute("select s.sname,o.isbot,s.score from ourclassify as o, botornotscore as s where o.sname=s.sname;")
    data=cur.fetchall()
    if mode==0:
        data=sorttup(data,2)
    elif mode==1:
        data=sorttupr(data,2)
    else:
        for i in range(0,10):
            random.shuffle(data)
    data=sorttupr(data[0:100],2)
    ourbots=[]
    xb=[]
    ournots=[]
    xn=[]
    for i in range(0,100):
        print(data[i][0]+":"+str(i)+":"+str(data[i][2])+":"+str(data[i][1]))
        if data[i][1]==0:
            ournots.append(data[i][2])
            xn.append(i)
        elif data[i][1]==1:
            ourbots.append(data[i][2])
            xb.append(i)
    bg=plt.subplot(111)
    for i in range(0,len(xn)):
        print(data[xn[i]][0]+":"+str(xn[i])+":"+str(ournots[i]))
    for i in range(0,len(xb)):
        print(data[xb[i]][0]+":"+str(xb[i])+":"+str(ourbots[i]))
    bg.bar(xn,ournots,width=1,color=(0.0,0.0,1.0))
    bg.bar(xb,ourbots,width=1,color=(1.0,0.0,0.0))
    plt.savefig(name+".pdf")
    plt.close()
            
        
def getUlist(sqlfile):
    conn=sqlite3.connect(sqlfile)
    cur=conn.cursor()
    cur.execute("select sname from udata;")
    uli=cur.fetchall()
    Ulist=[]
    for u in uli:
        Ulist.append(u[0])
    return Ulist
    
def useBotOrNot(sqlfile):
    conna=sqlite3.connect(sqlfile)
    cur=conna.cursor()
    try:
        cur.execute("create table botornotscore(sname varchar(50) primary key, score float);")
        conna.commit()
    except:
        conna.rollback()
    cur.execute("select sname from udata;")
    data=cur.fetchall()
    i=1
    for u in data:
        cur.execute("select * from botornotscore where sname=?;",(u[0],))
        check=cur.fetchall()
        if check==[]:
            result=None
            print(u[0]+" ("+str(i)+"/"+str(len(data))+")")
            i+=1
            try:
                result=bon.check_account(u[0])
                cur.execute("insert into botornotscore values(?,?);",(u[0],result['score']))
            except Exception as e:
                print("wait limit? "+str(e))
                cur.execute("insert into botornotscore values(?,?);",(u[0],None))
            conna.commit()
            time.sleep(.5)
    conna.close()
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
api_key2 = urllib.quote_plus("vJAZyChsolI3ZnHrgW1gJjEx6")
api_secret = urllib.quote_plus("XvX96j82NFPnA74Wrdc8vTpHRi9Il4xAYlVIHw0qIZbUqEwp3L")
api_secret2 = urllib.quote_plus("fpHFdjgG8hN72M9mKJigLHAZXYXfWqEVDf0LfIPrI4gEGMAj1w")

# Generate the credentials
auth = tweepy.OAuthHandler(api_key, api_secret)
auth2 = tweepy.OAuthHandler(api_key2, api_secret2)
auth.set_access_token("800791486228877313-z8tgC5j7rPdK18CBRGtBT2ZBL9aW1xN", "DzKW4y3odgDpfMN6Dd6ixgebRdlzstuzNHbLoNj9j0AUg")
auth2.set_access_token("796463566840688640-Zj0sSWU7Hu7JmjvaTC5RZhhqy7oyesG", "S7cYtJwbcGTR4J7sY6z83I1o3Mm3XLKM8LxqZPuVNnBzo")
api = tweepy.API(auth, wait_on_rate_limit=True)
apii = tweepy.API(auth2, wait_on_rate_limit=True)

limitTweets = True
#these next three functions extract data from tweets, not as good as the build in atributes from the twitter api.
def getats(text):
    ind=text.find("@")
    ats=""
    x=0
    while ind!=-1:
        x+=1
        if x>100:
            int("1")
        #print(text[ind:])
        found=re.match("( |^)@[a-zA-Z0-9_]+",text[ind:])
        if(found!=None):
            #print(text[ind:found.end()+ind])
            ats=ats+text[ind:found.end()+ind]
        ind=text.find("@",ind+1)
    return ats
def gethashes(text):
    ind=text.find("#")
    ats=""
    x=0
    while ind!=-1:
        x+=1
        if x>100:
            int("1")
        #print(text[ind:])
        found=re.match("( |^)#[A-Za-z][a-zA-Z0-9_]+",text[ind:])
        if(found!=None):
            #print(text[ind:found.end()+ind])
            ats=ats+text[ind:found.end()+ind]
        ind=text.find("#",ind+1)
    return ats
def geturlsmaybe(text):
    urls=""
    ind=0
    x=0
    found=re.search("( |^|\@)(https?:\/\/)?([\da-z-]+\.)+([a-z]+)(\/(?:[\/\w\.-]*)*\/?)?([\/?#].*)?",text)
    while found!=None:
        x+=1
        if x>10:
            int("1")
        ind2=found.start()+ind
        if text[ind2]=="@" or text[ind2]==" ":
            ind2+=1
        urls=urls+"\n"+text[ind2:found.end()+ind]
        ind=found.end()+ind
        if re.match("[.!]",urls[len(urls)-1])!=None:
            urls=urls[:len(urls)-1]
            
        found=re.search("( |^|\@)(https?:\/\/)?([\da-z-]+\.)+([a-z]+)(\/(?:[\/\w \.-]*)*\/?)?([\/?#].*)?",text[ind:])
    return urls
#uses previous three functions to extract data from a tweet
def extractfromtweets(sqlfile,twtid):
    conn=sqlite3.connect(sqlfile)
    cur=conn.cursor()
    cur.execute("select twtid,tweet from Tweets where twtid>?;",(twtid,))
    x=cur.fetchall()
    for tup in x:
        print(tup[0])
        ats=getats(tup[1])
        hashes=gethashes(tup[1])
        urls=geturlsmaybe(tup[1])
        cur.execute("update Tweets set hashtags=?,ats=?,urls=? where twtid=?;",(hashes,ats,urls,tup[0]))
        conn.commit()
    conn.close()
#extractfromtweets("udataf3.sqlite",66734)
    
    #( |^)(https?:\/\/)?([\da-z-]+\.)+([a-z]+)(\/(?:[\/\w \.-]*)*\/?)?([\/?#].*)?
#used in crawl to grab tweet data
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
                zz=status._json["entities"]['urls']
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
                        twid=0
                        try:
                            #curse.execute("select * from Tweets;")
                            #print(curse.fetchall())
                            curse.execute("select max(twid) from Tweets;")
                            t=curse.fetchall()[0][0]
                            if t!=None:
                                twid=t+1
                        except:
                            pass
                        #print(screenName,status.text,ba,hashes,ats,urls)
                        curse.execute("insert into Tweets values(?,?,?,?,?,?,?);",(twid,screenName,status.text,ba,hashes,ats,urls))
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
                        time.sleep(.5)
                    time.sleep(.2)
                if bb==5:
                    return None
            b=10
        except Exception as e:
            print("waiting ",e)
            time.sleep(b*4+1)
            b+=1
    if b==5:
        return None
    return [retweets, original]
#used to create tables
def recreatet(sqlfile):
    conn=sqlite3.connect(sqlfile)
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
#next three are gonna be used as an sql function if needed
def usermeantioned(ats,at):
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
#used for crawl. this step isn't really needed. can just do it in getdatafrom, but don't want to mess with it
def grabtweetstuff(usr):
    stuff=getData(usr.screen_name)
    return (usr.screen_name,stuff[0],stuff[1], usr.verified, usr.created_at, usr.default_profile, usr.default_profile_image, usr.favourites_count, usr.followers_count, usr.friends_count, usr.listed_count)
#the recusive call
def getdatafrom(depth,ulist,xx):
    data=[]
    xxxxxx=0
    for user in ulist:
        print("d:"+str(depth)+"\nL:"+str(xxxxxx)+"\nU:"+str(xx[0]))
        xx[0]+=1
        xxxxxx+=1
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
                time.sleep(1)
        if data==[]:
            try:
                data=grabtweetstuff(user)
            except Exception as e:
                print("oops "+str(user.screen_name)+"  "+str(e))
                time.sleep(1)
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
                    time.sleep(1)
            if depth>0:
                nl=[]
                sList = tweepy.Cursor(api.followers, screen_name=user.screen_name).items(10)
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
                                    time.sleep(1)
                                time.sleep(.2)
                        b=10
                    except Exception as e:
                        print("waiting ",e)
                        time.sleep(b*4+1)
                        b+=1
                #print(nl)
                getdatafrom(depth-1,nl,xx)
                    
                
#function that uses userstart for initial list in recursive crawl at depth depth.
def gather(userstart,depth):
    f=open(userstart,"r")
    startl=[]
    for l in f:
        l=l[:-1]
        print(l)
        try:
            startl.append(api.get_user(l))
        except:
            print("not found: ",l)
        time.sleep(.15)
    print(startl)
        #break
    #cur=conn.cursor()
    ##udict=useBotOrNot(ourbots)
    ##sc=binBotOrNotScore(udict)
    #print(getData(ourbots[0]))
    getdatafrom(depth,startl,[0])
#gather()