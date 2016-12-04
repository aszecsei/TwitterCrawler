import sqlite3
import matplotlib.pyplot as plt
import random
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
#makes a bar graph. opt is for which type of clustering, opt=0 for no cluster, opt=1 for just score, opt=2 for just subscore, opt=3 for both, and opt=4 for neither. with one of two formulas for the y axis. if opt2=0 y=(number_of_time_hastag_used/number_of_accounts_in_scope)/(max_number_of_times_a_hastag_used)
#if opt2!=0 y=(number_of_time_hastag_used/number_of_accounts_in_scope_that_used_the_hashtag)/(max_number_of_times_a_hastag_used)
def makehashbar(sqlfile,name,opt=0,clust=0,opt2=0):
    hashes=binhash(sqlfile,opt,clust)
    conn=sqlite3.connect(sqlfile)
    cur=conn.cursor()
    q="select sname from "
    if opt==1:
        q+q+"ourclusterscore where cluster="+str(clust)
    elif  opt==2:
        q=q+"ourclustersubscore where cluster="+str(clust)
    elif  opt==3:
        q=q+"ourclusterscoresubscore where cluster="+str(clust)
    elif  opt==4:
        q=q+"ourcluster where cluster="+str(clust)
    else:
        q=q+"udata"
    q=q+";"
    cur.execute(q)
    data=cur.fetchall()
        
    x=[]
    y=[]
    ind=0
    for xx in hashes:
        cnt=0
        #print(ind)
        for xxx in hashes[xx]:
            cnt+=hashes[xx][xxx]
        if cnt>2:
            x.append(ind)
            ind+=1
            if opt2==0:
                y.append((xx,float(cnt)/len(data)))
            else:
                y.append((xx,float(cnt)/len(hashes[xx])))
                
    y=sorttupr(y,1)
    lenn=100
    if len(y)<100:
        lenn=len(y)
    yy=y[:lenn]
    y=[]
    l=[]
    for tup in yy:
        l.append(tup[0])
        y.append(tup[1])
    print("ff")
    m=max(y)
    for i in range(0,lenn):
        y[i]=y[i]/m
    fig=plt.figure(figsize=(50,30))
    bg=fig.add_subplot(111)
    #fig=plt.figure(figsize=(5,3))
    #bg = fig.add_subplot(111)
    bg.set_position([.1,.25,.8,.70])
    #bg.yaxis.set_smart_bounds(True))
    #y.sort(reverse=True)
    bg.bar(x[:lenn],y,width=1, tick_label=l)
    plt.xticks(x[:lenn], l, rotation='vertical')
    if opt2==0:
        bg.yaxis.set_label_text("(# of times used/# of accounts in cluster)/max ratio")
    else:
        bg.yaxis.set_label_text("(# of times used/# of accounts that used it)/max ratio.")
    bg.xaxis.set_label_text("top 100 HashTags")
    plt.savefig(name+".pdf")
    plt.savefig(name+".png")
#makes a dictionary with hashtags as keys and another dictionary as the value, the second dictionaries have the accounts that used the hashtag as key and the number of times they used it has the value.
def binhash(sqlfile,opt=0,clust=0):
    conn=sqlite3.connect(sqlfile)
    cur=conn.cursor()
    q="select t.sname,t.hashtags from Tweets as t"
    if opt==1:
        q+q+", ourclusterscore as o where t.sname=o.sname and cluster="+str(clust)
    elif  opt==2:
        q=q+", ourclustersubscore as o where t.sname=o.sname and cluster="+str(clust)
    elif  opt==3:
        q=q+", ourclusterscoresubscore as o where t.sname=o.sname and cluster="+str(clust)
    elif  opt==4:
        q=q+", ourcluster as o where t.sname=o.sname and cluster="+str(clust)
    q=q+";"
    cur.execute(q)
    data=cur.fetchall()
    #print data
    tags={}
    for tup in data:
        tt=tup[1]
        if tt=="":
            continue
        if tt[-1]=="#":
            tt=tt[:-1]
        ind=tt.find("#")
        if ind==-1:
            continue
        ind2=tt.find("#",ind+1)
        if ind2==-1:
            in2=len(tt)
        if ind==ind2:
            continue
        while ind!=-1:
            tag=tt[ind:ind2]
            #print(tag)
            ind=ind2
            ind2=tt.find("#",ind+1)
            if ind==len(tt):
                ind=-1
            try:
                if tup[0] not in tags[tag]:
                    tags[tag].update({tup[0]:1})
                else:
                    tags[tag][tup[0]]+=1
            except:
                tags.update({tag:{tup[0]:1}})
    return tags
#plots the overall score to average catagory score
def scoretoavgcat(sqlfile,name):
    conn=sqlite3.connect(sqlfile)
    cur=conn.cursor()
    cur.execute("select * from botornotscore;")
    data=cur.fetchall()
    x=[]
    y=[]
    for tup in data:
        if tup[1]==None or tup[2]==None or tup[3]==None or tup[4]==None or tup[5]==None or tup[6]==None or tup[7]==None:
            continue
        y.append(tup[1])
        x.append((float(tup[2])+float(tup[3])+float(tup[4])+float(tup[5])+float(tup[6])+float(tup[7]))/6.0)
    fig=plt.figure(figsize=(50,30))
    bg=fig.add_subplot(111)
    bg.scatter(x,y,s=25)
    bg.xaxis.set_label_text("avg of the botornot catagory scores")
    bg.yaxis.set_label_text("the overall botornot score")
    plt.title("Score vs avg catagory score")
    
    #bg.scatter(xb,ourbots,s=25,c=(1,0,0,.5),marker="o")
    plt.savefig(name+".pdf")
    plt.savefig(name+".png")
#makes scatter plot y axis is botornot score and x is a random float in range of [0.0,1.0]. marker is blue if our classifier classified account as not a bot, and red if it classified it as a bot
def scatgraphbotvscore(sqlfile,name,mode=0):
    conn=sqlite3.connect(sqlfile)
    cur=conn.cursor()
    cur.execute("select s.sname,o.isbot,s.score from ourclassify as o, botornotscore as s where o.sname=s.sname;")
    data=cur.fetchall()
    our=[]
    x=[]
    #ournots=[]
    #xn=[]
    cc=[]
    
    for i in range(0,len(data)):
        print(data[i][0]+":"+str(i)+":"+str(data[i][2])+":"+str(data[i][1]))
        our.append(data[i][2])
        x.append(random.random())
        if data[i][1]==0:
            cc.append((0,0,1,0.5))
        elif data[i][1]==1:
            cc.append((1,0,0,0.5))
    bg=plt.subplot(191)
    bg.scatter(x,our,s=25,c=cc,marker="s")
    bg.yaxis.set_label_text("the overall botornot score")
    plt.title("Scores")
    #bg.scatter(xb,ourbots,s=25,c=(1,0,0,.5),marker="o")
    plt.savefig(name+".pdf")
    plt.savefig(name+".png")
    #plt.close()    
#this makes a bar graph of 100 accounts (either the top 100 highest botornotscore, mode=0, or the 100 lowest botornot score, mode=1, or 100 at random. bars are colored red for accounts classified as bots, and blue if not.
def bargraphbotvscore(sqlfile,name,mode=0):
    conn=sqlite3.connect(sqlfile)
    cur=conn.cursor()
    cur.execute("select s.sname,o.isbot,s.score from ourclassify as o, botornotscore as s where o.sname=s.sname and s.score is not null;")
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
    bg.xaxis.set_label_text("accounts")
    bg.yaxis.set_label_text("the overall botornot score")
    plt.title("Score vs accounts")
    plt.savefig(name+".pdf")
    plt.savefig(name+".png")
    #plt.close()    
def binats(sqlfile):
    conn=sqlite3.connect(sqlfile)
    cur=conn.cursor()
    cur.execute("select sname,ats from Tweets;")
    data=cur.fetchall()
    #print data
    ats={}
    for tup in data:
        tt=tup[1]
        if tt=="":
            continue
        if tt[-1]=="@":
            tt=tt[:-1]
        ind=tt.find("@")
        if ind==-1:
            continue
        ind2=tt.find("@",ind+1)
        if ind2==-1:
            in2=len(tt)
        if ind==ind2:
            continue
        while ind!=-1:
            at=tt[ind:ind2]
            ind=ind2
            ind2=tt.find("@",ind+1)
            if ind==len(tt):
                ind=-1
            try:
                if tup[0] not in ats[at]:
                    ats[at].update({tup[0]:1})
                else:
                    ats[at][tup[0]]+=1
            except:
                ats.update({at:{tup[0]:1}})
    return ats    