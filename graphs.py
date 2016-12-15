import sqlite3
import matplotlib.pyplot as plt
import random
import os
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
def makehashbar(sqlfile,name,opt=0,opt2=0,clust=0):
    hashes=binhash(sqlfile,opt,clust)
    conn=sqlite3.connect(sqlfile)
    cur=conn.cursor()
    q="select sname from "
    option=""
    if opt==1:
        q=q+"ourclusterscore where cluster="+str(clust)
        option="ourclusterscore "+str(clust)
    elif  opt==2:
        q=q+"ourclustersubscore where cluster="+str(clust)
        option="ourclustersubscore "+str(clust)
    elif  opt==3:
        q=q+"ourclusterscoresubscore where cluster="+str(clust)
        option="ourclusterscoresubscore "+str(clust)
    else:
        q=q+"udata"
        option="udata"
    name=name+" "+option
    q=q+";"
    cur.execute(q)
    data=cur.fetchall()
        
    x=[]
    y=[]
    ind=0
    for xx in hashes:
        cnt=0
        if opt2==2:
            cnt=len(hashes[xx])
        else:
            for xxx in hashes[xx]:
                cnt+=hashes[xx][xxx]
        x.append(ind)
        ind+=1
        if opt2==0:
            y.append((xx,float(cnt)/len(data)))
        elif opt2==1:
            y.append((xx,float(cnt)/len(hashes[xx])))
        else:
            y.append((xx,float(cnt)))
                
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
    #print(name)
    #m=max(y)
    #for i in range(0,lenn):
        #y[i]=y[i]/m
    fig=plt.figure(figsize=(50,30))
    bg = fig.add_subplot(111)
    bg.set_position([.1,.25,.8,.70])
    #bg.yaxis.set_smart_bounds(True))
    #y.sort(reverse=True)
    nx=[]
    for xxx in x[:lenn]:
        nx.append(xxx+.5)
    bg.bar(x[:lenn],y,width=1, tick_label=l)
    plt.xticks(nx, l, rotation='vertical')
    if opt2==0:
        bg.yaxis.set_label_text("# of times used/# of accounts in "+option,fontsize=20)
        option2="eq1(x)"
    elif opt2==1:
        bg.yaxis.set_label_text("# of times used/# of accounts that used it in "+option,fontsize=20)
        option2="eq2(x)"
    else:
        bg.yaxis.set_label_text("# of accounts that used it in "+option,fontsize=20)
        option2="number of accounts that used the hashtag"
    name=name+" "+option2
    bg.xaxis.set_label_text("HashTags",fontsize=20)
    bg.xaxis.set_tick_params(labelsize=12)
    bg.yaxis.set_tick_params(labelsize=20)
    #plt.title("top 100 HashTags for "+option+" "+option2)
    #plt.savefig(name+".pdf")
    plt.savefig(name+".png")
    #print(name)
    plt.close()
#makes a dictionary with hashtags as keys and another dictionary as the value, the second dictionaries have the accounts that used the hashtag as key and the number of times they used it has the value.
def binhash(sqlfile,opt=0,clust=0):
    conn=sqlite3.connect(sqlfile)
    cur=conn.cursor()
    q="select t.sname,t.hashtags from Tweets as t"
    if opt==1:
        q=q+", ourclusterscore as o where t.sname=o.sname and cluster="+str(clust)
    elif  opt==2:
        q=q+", ourclustersubscore as o where t.sname=o.sname and cluster="+str(clust)
    elif  opt==3:
        q=q+", ourclusterscoresubscore as o where t.sname=o.sname and cluster="+str(clust)
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
def scoretoavgcat(sqlfile,name,opt=0):
    conn=sqlite3.connect(sqlfile)
    cur=conn.cursor()
    q=""
    option=""
    if opt==0:
        q="select b.* from botornotscore as b;"
        option="all"
    else:
        q="select b.*,c.cat from botornotscore as b, catag2 as c where b.sname=c.sname;"
        option="manually classified"
    name=name+" "+option
    cur.execute(q)
    data=cur.fetchall()
    x=[]
    y=[]
    c=[]
    for tup in data:
        if tup[1]==None or tup[2]==None or tup[3]==None or tup[4]==None or tup[5]==None or tup[6]==None or tup[7]==None:
            continue
        y.append(tup[1])
        x.append((float(tup[2])+float(tup[3])+float(tup[4])+float(tup[5])+float(tup[6])+float(tup[7]))/6.0)
        if opt!=0:
            #print(tup[9])
            if tup[9]==0:
                c.append((0,0,1))
            elif tup[9]==1:
                c.append((1,0,0))
            else:
                c.append((0,1,0))
        else:
            c.append((0,0,1))
    fig=plt.figure(figsize=(50,30))
    bg=fig.add_subplot(111)
    bg.scatter(x,y,s=25,c=c)
    bg.xaxis.set_label_text("avg of the botornot category scores",fontsize=20)
    bg.yaxis.set_label_text("the overall botornot score",fontsize=20)
    bg.xaxis.set_tick_params(labelsize=20)
    bg.yaxis.set_tick_params(labelsize=20)
    #plt.title("Score vs avg category score ("+option+")")
    
    #bg.scatter(xb,ourbots,s=25,c=(1,0,0,.5),marker="o")
    #plt.savefig(name+".pdf")
    plt.savefig(name+".png")
    #print(name)
    plt.close()
#makes scatter plot y axis is botornot score and x is a random float in range of [0.0,1.0]. marker is blue if our classifier classified account as not a bot, and red if it classified it as a bot
def scatgraphbotvscore(sqlfile,name):
    conn=sqlite3.connect(sqlfile)
    cur=conn.cursor()
    cur.execute("select s.sname,c.cat,s.score from catag2 as c, botornotscore as s where c.sname=s.sname;")
    data=cur.fetchall()
    our=[]
    x=[]
    #ournots=[]
    #xn=[]
    cc=[]
    
    for i in range(0,len(data)):
        #print(data[i][0]+":"+str(i)+":"+str(data[i][2])+":"+str(data[i][1]))
        our.append(data[i][2])
        x.append(random.random())
        if data[i][1]==0:
            cc.append((0,0,1,0.5))
        elif data[i][1]==1:
            cc.append((1,0,0,0.5))
        elif data[i][1]==2:
            cc.append((0,1,0,0.5))
    bg=plt.subplot(191)
    bg.scatter(x,our,s=25,c=cc,marker="s")
    plt.xticks([], [])
    bg.yaxis.set_label_text("the overall botornot score",fontsize=20)
    bg.yaxis.set_tick_params(labelsize=20)
    #plt.title("Scores")
    #bg.scatter(xb,ourbots,s=25,c=(1,0,0,.5),marker="o")
    #plt.savefig(name+".pdf")
    plt.savefig(name+".png")
    #print(name)
    plt.close()    
#this makes a bar graph of 100 accounts (either the top 100 highest botornotscore, mode=0, or the 100 lowest botornot score, mode=1, or 100 at random. bars are colored red for accounts classified as bots, and blue if not.
def bargraphbotvscore(sqlfile,name,mode=0):
    conn=sqlite3.connect(sqlfile)
    cur=conn.cursor()
    cur.execute("select s.sname,c.cat,s.score from catag2 as c, botornotscore as s where c.sname=s.sname and s.score is not null;")
    data=cur.fetchall()
    option=""
    if mode==0:
        data=sorttup(data,2)
        option="low 500"
    elif mode==1:
        data=sorttupr(data,2)
        option="high 500"
    else:
        option="random 500"
        for i in range(0,10):
            random.shuffle(data)
    name=name+" "+option
    data=sorttupr(data[:500],2)
    ourbots=[]
    xb=[]
    ournots=[]
    xn=[]
    idk=[]
    xx=[]
    
    for i in range(0,500):
        #print(data[i][0]+":"+str(i)+":"+str(data[i][2])+":"+str(data[i][1]))
        if data[i][1]==0:
            ournots.append(data[i][2])
            xn.append(i)
        elif data[i][1]==1:
            ourbots.append(data[i][2])
            xb.append(i)
        elif data[i][1]==2:
            idk.append(data[i][2])
            xx.append(i)
    fig=plt.figure(figsize=(50,30))
    bg=fig.add_subplot(111)
    bg.set_position([.1,.25,.8,.70])
    #for i in range(0,len(xn)):
        #print(data[xn[i]][0]+":"+str(xn[i])+":"+str(ournots[i]))
    #for i in range(0,len(xb)):
        #print(data[xb[i]][0]+":"+str(xb[i])+":"+str(ourbots[i]))
    bg.bar(xn,ournots,width=1,color=(0.0,0.0,1.0))
    bg.bar(xb,ourbots,width=1,color=(1.0,0.0,0.0))
    bg.bar(xx,idk,width=1,color=(0.0,1.0,0.0))
    bg.xaxis.set_label_text("accounts",fontsize=20)
    bg.yaxis.set_label_text("the overall botornot score",fontsize=20)
    bg.xaxis.set_tick_params(labelsize=20)
    bg.yaxis.set_tick_params(labelsize=20)
    #plt.title("Score vs accounts ("+option+")")
    #plt.savefig(name+".pdf")
    plt.savefig(name+".png")
    #print(name)
    plt.close()  
def binurls(sqlfile,opt=3):
    conn=sqlite3.connect(sqlfile)
    cur=conn.cursor()
    q="select t.sname,o.cluster from Tweets as t"
    if opt==1:
        q=q+", ourclusterscore as o where t.sname=o.sname"
    elif  opt==2:
        q=q+", ourclustersubscore as o where t.sname=o.sname"
    elif  opt==3:
        q=q+", ourclusterscoresubscore as o where t.sname=o.sname"
    q=q+" and t.urls is not null and t.urls!=\"\";"
    cur.execute(q)
    data=cur.fetchall()
    clustedurls={}
    for tup in data:
        if tup[1] not in clustedurls:
            clustedurls[tup[1]]={tup[0]:1.0}
            #print("a")
        elif tup[0] not in clustedurls[tup[1]]:
            clustedurls[tup[1]][tup[0]]=1.0
            #print("b")
        else:
            clustedurls[tup[1]][tup[0]]+=1.0
    return clustedurls    
def binats(sqlfile,opt=3,clust=0,opt2=0):
    conn=sqlite3.connect(sqlfile)
    cur=conn.cursor()
    if opt2==0:
        q="select t.sname,o.cluster from Tweets as t"
        if opt==1:
            q=q+", ourclusterscore as o where t.sname=o.sname"
        elif  opt==2:
            q=q+", ourclustersubscore as o where t.sname=o.sname"
        elif  opt==3:
            q=q+", ourclusterscoresubscore as o where t.sname=o.sname"
        q=q+" and t.ats is not null and t.ats!=\"\" and t.retweet=0;"
        cur.execute(q)
        data=cur.fetchall()
        clustedat={}
        for tup in data:
            if tup[1] not in clustedat:
                clustedat[tup[1]]={tup[0]:1.0}
                #print("a")
            elif tup[0] not in clustedat[tup[1]]:
                clustedat[tup[1]][tup[0]]=1.0
                #print("b")
            else:
                clustedat[tup[1]][tup[0]]+=1.0
        return clustedat
        
    elif opt2==1:
        q="select t.sname,t.ats from Tweets as t"
        if opt==1:
            q=q+", ourclusterscore as o where t.sname=o.sname and cluster="+str(clust)
        elif  opt==2:
            q=q+", ourclustersubscore as o where t.sname=o.sname and cluster="+str(clust)
        elif  opt==3:
            q=q+", ourclusterscoresubscore as o where t.sname=o.sname and cluster="+str(clust)
        q=q+";"
        cur.execute(q)
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
                #print(at)
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
#binats("udataf3.sqlite")
def binrt(sqlfile,opt=3):
    conn=sqlite3.connect(sqlfile)
    cur=conn.cursor()
    q="select t.sname,o.cluster,t.rt from udata as t"
    if opt==1:
        q=q+", ourclusterscore as o where t.sname=o.sname"
    elif  opt==2:
        q=q+", ourclustersubscore as o where t.sname=o.sname"
    elif  opt==3:
        q=q+", ourclusterscoresubscore as o where t.sname=o.sname"
    q=q+" and t.rt>0;"
    cur.execute(q)
    data=cur.fetchall()
    clustedrt={}
    for tup in data:
        if tup[1] not in clustedrt:
            clustedrt[tup[1]]={tup[0]:float(tup[2])}
            #print("a")
        else:
            clustedrt[tup[1]][tup[0]]=float(tup[2])
    return clustedrt
def binfollowing(sqlfile,opt=3):
    conn=sqlite3.connect(sqlfile)
    cur=conn.cursor()
    q="select t.sname,o.cluster,t.frc from udata as t"
    if opt==1:
        q=q+", ourclusterscore as o where t.sname=o.sname"
    elif  opt==2:
        q=q+", ourclustersubscore as o where t.sname=o.sname"
    elif  opt==3:
        q=q+", ourclusterscoresubscore as o where t.sname=o.sname"
    q=q+" and t.frc>0;"
    cur.execute(q)
    data=cur.fetchall()
    clustedfollowing={}
    for tup in data:
        if tup[1] not in clustedfollowing:
            clustedfollowing[tup[1]]={tup[0]:tup[2]}
            #print("a")
        else:
            clustedfollowing[tup[1]][tup[0]]=tup[2]
    return clustedfollowing
def binfollower(sqlfile,opt=3):
    conn=sqlite3.connect(sqlfile)
    cur=conn.cursor()
    q="select t.sname,o.cluster,t.foc from udata as t"
    if opt==1:
        q=q+", ourclusterscore as o where t.sname=o.sname"
    elif  opt==2:
        q=q+", ourclustersubscore as o where t.sname=o.sname"
    elif  opt==3:
        q=q+", ourclusterscoresubscore as o where t.sname=o.sname"
    q=q+" and t.foc>0;"
    cur.execute(q)
    data=cur.fetchall()
    clustedfollower={}
    for tup in data:
        if tup[1] not in clustedfollower:
            clustedfollower[tup[1]]={tup[0]:tup[2]}
            #print("a")
        else:
            clustedfollower[tup[1]][tup[0]]=tup[2]
    return clustedfollower
def binfaved(sqlfile,opt=3):
    conn=sqlite3.connect(sqlfile)
    cur=conn.cursor()
    q="select t.sname,o.cluster,t.fac from udata as t"
    if opt==1:
        q=q+", ourclusterscore as o where t.sname=o.sname"
    elif  opt==2:
        q=q+", ourclustersubscore as o where t.sname=o.sname"
    elif  opt==3:
        q=q+", ourclusterscoresubscore as o where t.sname=o.sname"
    q=q+" and t.fac>0;"
    cur.execute(q)
    data=cur.fetchall()
    clustedfaved={}
    for tup in data:
        if tup[1] not in clustedfaved:
            clustedfaved[tup[1]]={tup[0]:tup[2]}
            #print("a")
        else:
            clustedfaved[tup[1]][tup[0]]=tup[2]
    return clustedfaved
def binlisted(sqlfile,opt=3):
    conn=sqlite3.connect(sqlfile)
    cur=conn.cursor()
    q="select t.sname,o.cluster,t.lic from udata as t"
    if opt==1:
        q=q+", ourclusterscore as o where t.sname=o.sname"
    elif  opt==2:
        q=q+", ourclustersubscore as o where t.sname=o.sname"
    elif  opt==3:
        q=q+", ourclusterscoresubscore as o where t.sname=o.sname"
    q=q+" and t.lic>0;"
    cur.execute(q)
    data=cur.fetchall()
    clustedlisted={}
    for tup in data:
        if tup[1] not in clustedlisted:
            clustedlisted[tup[1]]={tup[0]:tup[2]}
            #print("a")
        else:
            clustedlisted[tup[1]][tup[0]]=tup[2]
    return clustedlisted
def makeurlsbar(sqlfile,name,opt=3,opt2=0):
    conn=sqlite3.connect(sqlfile)
    cur=conn.cursor()
    q="select cluster,count(cluster) from "
    option=""
    if opt==1:
        q=q+"ourclusterscore group by cluster"
        option="ourclusterscore"
    elif  opt==2:
        q=q+"ourclustersubscore group by cluster"
        option="ourclustersubscore"
    elif  opt==3:
        q=q+"ourclusterscoresubscore group by cluster"
        option="ourclusterscoresubscore"
    q=q+";"
    name=name+option
    clustcnt={}
    cur.execute(q)
    for i in cur.fetchall():
        clustcnt[i[0]]=i[1]
    q="select cluster,avg(score) from (select b.sname,score,cluster from botornotscore as b, "
    if opt==1:
        q=q+"ourclusterscore as o where o.sname=b.sname) as c group by cluster"
    elif  opt==2:
        q=q+"ourclustersubscore as o where o.sname=b.sname) as c group by cluster"
    elif  opt==3:
        q=q+"ourclusterscoresubscore as o where o.sname=b.sname) as c group by cluster"
    q=q+";"
    cur.execute(q)    
    clustavgscore={}
    for i in cur.fetchall():
        clustavgscore[i[0]]=i[1]
    urls=binurls(sqlfile,opt)
    x=[]
    y=[]
    ind=0
    for xx in urls:
        cnt=0
        #print(ind)
        if opt2==2:
            cnt=len(urls[xx])
        else:
            for xxx in urls[xx]:
                cnt+=urls[xx][xxx]
        x.append(ind)
        ind+=1
        if opt2==0:
            y.append((xx,float(cnt)/clustcnt[xx]))
        elif opt2==1:
            y.append((xx,float(cnt)/len(urls[xx])))
        else:
            y.append((xx,float(cnt)/clustcnt[xx]))
                
    y=sorttupr(y,1)
    lenn=100
    if len(y)<100:
        lenn=len(y)
    yy=y[:lenn]
    y=[]
    l=[]
    c=[]
    for tup in yy:
        l.append(str(tup[0]))
        y.append(tup[1])
        c.append((clustavgscore[tup[0]],0,1.0-clustavgscore[tup[0]]))
    #print(name)
    #m=max(y)
    #for i in range(0,lenn):
        #y[i]=y[i]/m
    fig=plt.figure(figsize=(50,30))
    bg=fig.add_subplot(111)
    #fig=plt.figure(figsize=(5,3))
    #bg = fig.add_subplot(111)
    bg.set_position([.1,.25,.8,.70])
    #bg.yaxis.set_smart_bounds(True))
    #y.sort(reverse=True)
    bg.bar(x[:lenn],y,width=1, color=c, tick_label=l,)
    nx=[]
    for xxx in x[:lenn]:
        nx.append(xxx+.5)
    plt.xticks(nx, l)
    option2=""
    if opt2==0:
        bg.yaxis.set_label_text("#tweets with urls/#accounts in cluster",fontsize=20)
        option2="eq1(x)"
    elif opt2==1:
        bg.yaxis.set_label_text("#tweets with urls/#accounts in cluster who uesed urls",fontsize=20)
        option2="eq2(x)"
    else:
        bg.yaxis.set_label_text("#accounts in cluster who uesed urls/#accounts in cluster",fontsize=20)
        option2="eq3(x)"
    name=name+" "+option2
    bg.xaxis.set_tick_params(labelsize=15)
    bg.yaxis.set_tick_params(labelsize=20)
    bg.xaxis.set_label_text("Clusters",fontsize=20)
    #plt.title(option2+" vs clusters ("+option+")")
    #plt.savefig(name+".pdf")
    plt.savefig(name+".png")
    #print(name)
    plt.close()
def makertbar(sqlfile,name,opt=3,opt2=0):
    conn=sqlite3.connect(sqlfile)
    cur=conn.cursor()
    q="select cluster,count(cluster) from "
    option=""
    if opt==1:
        q=q+"ourclusterscore group by cluster"
        option="ourclusterscore"
    elif  opt==2:
        q=q+"ourclustersubscore group by cluster"
        option="ourclustersubscore"
    elif  opt==3:
        q=q+"ourclusterscoresubscore group by cluster"
        option="ourclusterscoresubscore"
    q=q+";"
    name=name+option
    clustcnt={}
    cur.execute(q)
    for i in cur.fetchall():
        clustcnt[i[0]]=i[1]
    q="select cluster,avg(score) from (select b.sname,score,cluster from botornotscore as b, "
    if opt==1:
        q=q+"ourclusterscore as o where o.sname=b.sname) as c group by cluster"
    elif  opt==2:
        q=q+"ourclustersubscore as o where o.sname=b.sname) as c group by cluster"
    elif  opt==3:
        q=q+"ourclusterscoresubscore as o where o.sname=b.sname) as c group by cluster"
    q=q+";"
    cur.execute(q)    
    clustavgscore={}
    for i in cur.fetchall():
        clustavgscore[i[0]]=i[1]
    rts=binrt(sqlfile,opt)
    x=[]
    y=[]
    ind=0
    for xx in rts:
        cnt=0
        #print(ind)
        if opt2==2:
            cnt=len(rts[xx])
        else:
            for xxx in rts[xx]:
                cnt+=rts[xx][xxx]
        x.append(ind)
        ind+=1
        if opt2==0:
            y.append((xx,float(cnt)/clustcnt[xx]))
        elif opt2==1:
            y.append((xx,float(cnt)/len(rts[xx])))
        else:
            y.append((xx,float(cnt)/clustcnt[xx]))
                
    y=sorttupr(y,1)
    lenn=100
    if len(y)<100:
        lenn=len(y)
    yy=y[:lenn]
    y=[]
    l=[]
    c=[]
    for tup in yy:
        l.append(str(tup[0]))
        y.append(tup[1])
        c.append((clustavgscore[tup[0]],0,1.0-clustavgscore[tup[0]]))
    #print(name)
    #m=max(y)
    #for i in range(0,lenn):
        #y[i]=y[i]/m
    fig=plt.figure(figsize=(50,30))
    bg=fig.add_subplot(111)
    #fig=plt.figure(figsize=(5,3))
    #bg = fig.add_subplot(111)
    bg.set_position([.1,.25,.8,.70])
    #bg.yaxis.set_smart_bounds(True))
    #y.sort(reverse=True)
    bg.bar(x[:lenn],y,width=1, color=c, tick_label=l,)
    nx=[]
    for xxx in x[:lenn]:
        nx.append(xxx+.5)
    plt.xticks(nx, l)
    option2=""
    if opt2==0:
        bg.yaxis.set_label_text("#rt/#accounts in cluster",fontsize=20)
        option2="eq1(x)"
    elif opt2==1:
        bg.yaxis.set_label_text("#rt/#accounts in cluster who rt",fontsize=20)
        option2="eq2(x)"
    else:
        bg.yaxis.set_label_text("#accounts in cluster who rt/#accounts in cluster",fontsize=20)
        option2="eq3(x)"
    name=name+" "+option2
    bg.xaxis.set_tick_params(labelsize=15)
    bg.yaxis.set_tick_params(labelsize=20)
    bg.xaxis.set_label_text("Clusters",fontsize=20)
    #plt.title(option2+" vs clusters ("+option+")")
    #plt.savefig(name+".pdf")
    plt.savefig(name+".png")
    #print(name)
    plt.close()
def makeatbar(sqlfile,name,opt=3,opt2=0):
    conn=sqlite3.connect(sqlfile)
    cur=conn.cursor()
    q="select cluster,count(cluster) from "
    option=""
    if opt==1:
        q=q+"ourclusterscore group by cluster"
        option="ourclusterscore"
    elif  opt==2:
        q=q+"ourclustersubscore group by cluster"
        option="ourclustersubscore"
    elif  opt==3:
        q=q+"ourclusterscoresubscore group by cluster"
        option="ourclusterscoresubscore"
    q=q+";"
    name=name+option
    clustcnt={}
    cur.execute(q)
    for i in cur.fetchall():
        clustcnt[i[0]]=i[1]
    q="select cluster,avg(score) from (select b.sname,score,cluster from botornotscore as b, "
    if opt==1:
        q=q+"ourclusterscore as o where o.sname=b.sname) as c group by cluster"
    elif  opt==2:
        q=q+"ourclustersubscore as o where o.sname=b.sname) as c group by cluster"
    elif  opt==3:
        q=q+"ourclusterscoresubscore as o where o.sname=b.sname) as c group by cluster"
    q=q+";"
    cur.execute(q)    
    clustavgscore={}
    for i in cur.fetchall():
        clustavgscore[i[0]]=i[1]
    ats=binats(sqlfile,opt)
    x=[]
    y=[]
    ind=0
    for xx in ats:
        cnt=0
        #print(ind)
        if opt2==2:
            cnt=len(ats[xx])
        else:
            for xxx in ats[xx]:
                cnt+=ats[xx][xxx]
        x.append(ind)
        ind+=1
        if opt2==0:
            y.append((xx,float(cnt)/clustcnt[xx]))
        elif opt2==1:
            y.append((xx,float(cnt)/len(ats[xx])))
        else:
            y.append((xx,float(cnt)/clustcnt[xx]))
                
    y=sorttupr(y,1)
    lenn=100
    if len(y)<100:
        lenn=len(y)
    yy=y[:lenn]
    y=[]
    l=[]
    c=[]
    for tup in yy:
        l.append(str(tup[0]))
        y.append(tup[1])
        c.append((clustavgscore[tup[0]],0,1.0-clustavgscore[tup[0]]))
    #print(name)
    #m=max(y)
    #for i in range(0,lenn):
        #y[i]=y[i]/m
    fig=plt.figure(figsize=(50,30))
    bg=fig.add_subplot(111)
    #fig=plt.figure(figsize=(5,3))
    #bg = fig.add_subplot(111)
    bg.set_position([.1,.25,.8,.70])
    #bg.yaxis.set_smart_bounds(True))
    #y.sort(reverse=True)
    bg.bar(x[:lenn],y,width=1, color=c, tick_label=l)
    nx=[]
    for xxx in x[:lenn]:
        nx.append(xxx+.5)
    plt.xticks(nx, l)
    option2=""
    if opt2==0:
        bg.yaxis.set_label_text("#tweets with a mention/#accounts in cluster",fontsize=20)
        option2="eq1(x)"
    elif opt2==1:
        bg.yaxis.set_label_text("#tweets with a mention/#accounts in cluster who made a mention",fontsize=20)
        option2="eq2(x)"
    else:
        bg.yaxis.set_label_text("#accounts in cluster who made a mention/#accounts in cluster",fontsize=20)
        option2="eq3(x)"
    name=name+" "+option2
    bg.xaxis.set_tick_params(labelsize=15)
    bg.yaxis.set_tick_params(labelsize=20)
    bg.xaxis.set_label_text("Clusters",fontsize=20)
    #plt.title(option2+" vs clusters ("+option+")")
    #plt.savefig(name+".pdf")
    plt.savefig(name+".png")
    #print(name)
    plt.close()
def makefavedbar(sqlfile,name,opt=3,opt2=0):
    conn=sqlite3.connect(sqlfile)
    cur=conn.cursor()
    q="select cluster,count(cluster) from "
    option=""
    if opt==1:
        q=q+"ourclusterscore group by cluster"
        option="ourclusterscore"
    elif  opt==2:
        q=q+"ourclustersubscore group by cluster"
        option="ourclustersubscore"
    elif  opt==3:
        q=q+"ourclusterscoresubscore group by cluster"
        option="ourclusterscoresubscore"
    q=q+";"
    name=name+option
    clustcnt={}
    cur.execute(q)
    for i in cur.fetchall():
        clustcnt[i[0]]=i[1]
    q="select cluster,avg(score) from (select b.sname,score,cluster from botornotscore as b, "
    if opt==1:
        q=q+"ourclusterscore as o where o.sname=b.sname) as c group by cluster"
    elif  opt==2:
        q=q+"ourclustersubscore as o where o.sname=b.sname) as c group by cluster"
    elif  opt==3:
        q=q+"ourclusterscoresubscore as o where o.sname=b.sname) as c group by cluster"
    q=q+";"
    cur.execute(q)    
    clustavgscore={}
    for i in cur.fetchall():
        clustavgscore[i[0]]=i[1]
    facs=binfaved(sqlfile,opt)
    x=[]
    y=[]
    ind=0
    for xx in facs:
        cnt=0
        #print(ind)
        if opt2==2:
            cnt=len(facs[xx])
        else:
            for xxx in facs[xx]:
                cnt+=facs[xx][xxx]
        x.append(ind)
        ind+=1
        if opt2==0:
            y.append((xx,float(cnt)/clustcnt[xx]))
        elif opt2==1:
            y.append((xx,float(cnt)/len(facs[xx])))
        else:
            y.append((xx,float(cnt)/clustcnt[xx]))
                
    y=sorttupr(y,1)
    lenn=100
    if len(y)<100:
        lenn=len(y)
    yy=y[:lenn]
    y=[]
    l=[]
    c=[]
    for tup in yy:
        l.append(str(tup[0]))
        y.append(tup[1])
        c.append((clustavgscore[tup[0]],0,1.0-clustavgscore[tup[0]]))
    #print(name)
    #m=max(y)
    #for i in range(0,lenn):
        #y[i]=y[i]/m
    fig=plt.figure(figsize=(50,30))
    bg=fig.add_subplot(111)
    #fig=plt.figure(figsize=(5,3))
    #bg = fig.add_subplot(111)
    bg.set_position([.1,.25,.8,.70])
    #bg.yaxis.set_smart_bounds(True))
    #y.sort(reverse=True)
    bg.bar(x[:lenn],y,width=1, color=c, tick_label=l)
    nx=[]
    for xxx in x[:lenn]:
        nx.append(xxx+.5)
    plt.xticks(nx, l)
    option2=""
    if opt2==0:
        bg.yaxis.set_label_text("#favorited/#accounts in cluster",fontsize=20)
        option2="eq1(x)"
    elif opt2==1:
        bg.yaxis.set_label_text("#favorited/#accounts in cluster who favorited",fontsize=20)
        option2="eq2(x)"
    else:
        bg.yaxis.set_label_text("#accounts in cluster who favorited/#accounts in cluster",fontsize=20)
        option2="eq3(x)"
    name=name+" "+option2
    bg.xaxis.set_tick_params(labelsize=15)
    bg.yaxis.set_tick_params(labelsize=20)
    bg.xaxis.set_label_text("Clusters",fontsize=20)
    #plt.title(option2+" vs clusters ("+option+")")
    #plt.savefig(name+".pdf")
    plt.savefig(name+".png")
    #print(name)
    plt.close()
def makelistedbar(sqlfile,name,opt=3,opt2=0):
    conn=sqlite3.connect(sqlfile)
    cur=conn.cursor()
    q="select cluster,count(cluster) from "
    option=""
    if opt==1:
        q=q+"ourclusterscore group by cluster"
        option="ourclusterscore"
    elif  opt==2:
        q=q+"ourclustersubscore group by cluster"
        option="ourclustersubscore"
    elif  opt==3:
        q=q+"ourclusterscoresubscore group by cluster"
        option="ourclusterscoresubscore"
    q=q+";"
    name=name+option
    clustcnt={}
    cur.execute(q)
    for i in cur.fetchall():
        clustcnt[i[0]]=i[1]
    q="select cluster,avg(score) from (select b.sname,score,cluster from botornotscore as b, "
    if opt==1:
        q=q+"ourclusterscore as o where o.sname=b.sname) as c group by cluster"
    elif  opt==2:
        q=q+"ourclustersubscore as o where o.sname=b.sname) as c group by cluster"
    elif  opt==3:
        q=q+"ourclusterscoresubscore as o where o.sname=b.sname) as c group by cluster"
    q=q+";"
    cur.execute(q)    
    clustavgscore={}
    for i in cur.fetchall():
        clustavgscore[i[0]]=i[1]
    lics=binlisted(sqlfile,opt)
    x=[]
    y=[]
    ind=0
    for xx in lics:
        cnt=0
        #print(ind)
        if opt2==2:
            cnt=len(lics[xx])
        else:
            for xxx in lics[xx]:
                cnt+=lics[xx][xxx]
        x.append(ind)
        ind+=1
        if opt2==0:
            y.append((xx,float(cnt)/clustcnt[xx]))
        elif opt2==1:
            y.append((xx,float(cnt)/len(lics[xx])))
        else:
            y.append((xx,float(cnt)/clustcnt[xx]))
                
    y=sorttupr(y,1)
    lenn=100
    if len(y)<100:
        lenn=len(y)
    yy=y[:lenn]
    y=[]
    l=[]
    c=[]
    for tup in yy:
        l.append(str(tup[0]))
        y.append(tup[1])
        c.append((clustavgscore[tup[0]],0,1.0-clustavgscore[tup[0]]))
    #print(name)
    #m=max(y)
    #for i in range(0,lenn):
        #y[i]=y[i]/m
    fig=plt.figure(figsize=(50,30))
    bg=fig.add_subplot(111)
    #fig=plt.figure(figsize=(5,3))
    #bg = fig.add_subplot(111)
    bg.set_position([.1,.25,.8,.70])
    #bg.yaxis.set_smart_bounds(True))
    #y.sort(reverse=True)
    bg.bar(x[:lenn],y,width=1, color=c, tick_label=l)
    nx=[]
    for xxx in x[:lenn]:
        nx.append(xxx+.5)
    plt.xticks(nx, l)
    option2=""
    if opt2==0:
        bg.yaxis.set_label_text("#lists/#accounts in cluster",fontsize=20)
        option2="eq1(x)"
    elif opt2==1:
        bg.yaxis.set_label_text("#lists/#accounts in cluster who are listed",fontsize=20)
        option2="eq2(x)"
    else:
        bg.yaxis.set_label_text("#accounts in cluster who are listed/#accounts in cluster",fontsize=20)
        option2="eq3(x)"
    name=name+" "+option2
    bg.xaxis.set_tick_params(labelsize=15)
    bg.yaxis.set_tick_params(labelsize=20)
    bg.xaxis.set_label_text("Clusters",fontsize=20)
    #plt.title(option2+" vs clusters ("+option+")")
    #plt.savefig(name+".pdf")
    plt.savefig(name+".png")
    #print(name)
    plt.close()
def makefollerbar(sqlfile,name,opt=3,opt2=0):
    conn=sqlite3.connect(sqlfile)
    cur=conn.cursor()
    q="select cluster,count(cluster) from "
    option=""
    if opt==1:
        q=q+"ourclusterscore group by cluster"
        option="ourclusterscore"
    elif  opt==2:
        q=q+"ourclustersubscore group by cluster"
        option="ourclustersubscore"
    elif  opt==3:
        q=q+"ourclusterscoresubscore group by cluster"
        option="ourclusterscoresubscore"
    q=q+";"
    name=name+option
    clustcnt={}
    cur.execute(q)
    for i in cur.fetchall():
        clustcnt[i[0]]=i[1]
    q="select cluster,avg(score) from (select b.sname,score,cluster from botornotscore as b, "
    if opt==1:
        q=q+"ourclusterscore as o where o.sname=b.sname) as c group by cluster"
    elif  opt==2:
        q=q+"ourclustersubscore as o where o.sname=b.sname) as c group by cluster"
    elif  opt==3:
        q=q+"ourclusterscoresubscore as o where o.sname=b.sname) as c group by cluster"
    q=q+";"
    cur.execute(q)    
    clustavgscore={}
    for i in cur.fetchall():
        clustavgscore[i[0]]=i[1]
    focs=binfollower(sqlfile,opt)
    x=[]
    y=[]
    ind=0
    for xx in focs:
        cnt=0
        #print(ind)
        if opt2==2:
            cnt=len(focs[xx])
        else:
            for xxx in focs[xx]:
                cnt+=focs[xx][xxx]
        x.append(ind)
        ind+=1
        if opt2==0:
            y.append((xx,float(cnt)/clustcnt[xx]))
        elif opt2==1:
            y.append((xx,float(cnt)/len(focs[xx])))
        else:
            y.append((xx,float(cnt)/clustcnt[xx]))
                
    y=sorttupr(y,1)
    lenn=100
    if len(y)<100:
        lenn=len(y)
    yy=y[:lenn]
    y=[]
    l=[]
    c=[]
    for tup in yy:
        l.append(str(tup[0]))
        y.append(tup[1])
        c.append((clustavgscore[tup[0]],0,1.0-clustavgscore[tup[0]]))
    #print(name)
    #m=max(y)
    #for i in range(0,lenn):
        #y[i]=y[i]/m
    fig=plt.figure(figsize=(50,30))
    bg=fig.add_subplot(111)
    #fig=plt.figure(figsize=(5,3))
    #bg = fig.add_subplot(111)
    bg.set_position([.1,.25,.8,.70])
    #bg.yaxis.set_smart_bounds(True))
    #y.sort(reverse=True)
    bg.bar(x[:lenn],y,width=1, color=c, tick_label=l)
    nx=[]
    for xxx in x[:lenn]:
        nx.append(xxx+.5)
    plt.xticks(nx, l)
    option2=""
    if opt2==0:
        bg.yaxis.set_label_text("#followers/#accounts in cluster",fontsize=20)
        option2="eq1(x)"
    elif opt2==1:
        bg.yaxis.set_label_text("#followers/#accounts in cluster who are followed",fontsize=20)
        option2="eq2(x)"
    else:
        bg.yaxis.set_label_text("#accounts in cluster who are followed/#accounts in cluster",fontsize=20)
        option2="eq3(x)"
    name=name+" "+option2
    bg.xaxis.set_tick_params(labelsize=15)
    bg.yaxis.set_tick_params(labelsize=20)
    bg.xaxis.set_label_text("Clusters",fontsize=20)
    #plt.title(option2+" vs clusters ("+option+")")
    #plt.savefig(name+".pdf")
    plt.savefig(name+".png")
    #print(name)
    plt.close()
def makefollingbar(sqlfile,name,opt=3,opt2=0):
    conn=sqlite3.connect(sqlfile)
    cur=conn.cursor()
    q="select cluster,count(cluster) from "
    option=""
    if opt==1:
        q=q+"ourclusterscore group by cluster"
        option="ourclusterscore"
    elif  opt==2:
        q=q+"ourclustersubscore group by cluster"
        option="ourclustersubscore"
    elif  opt==3:
        q=q+"ourclusterscoresubscore group by cluster"
        option="ourclusterscoresubscore"
    q=q+";"
    name=name+option
    clustcnt={}
    cur.execute(q)
    for i in cur.fetchall():
        clustcnt[i[0]]=i[1]
    q="select cluster,avg(score) from (select b.sname,score,cluster from botornotscore as b, "
    if opt==1:
        q=q+"ourclusterscore as o where o.sname=b.sname) as c group by cluster"
    elif  opt==2:
        q=q+"ourclustersubscore as o where o.sname=b.sname) as c group by cluster"
    elif  opt==3:
        q=q+"ourclusterscoresubscore as o where o.sname=b.sname) as c group by cluster"
    q=q+";"
    cur.execute(q)    
    clustavgscore={}
    for i in cur.fetchall():
        clustavgscore[i[0]]=i[1]
    frcs=binfollowing(sqlfile,opt)
    x=[]
    y=[]
    ind=0
    for xx in frcs:
        cnt=0
        #print(ind)
        if opt2==2:
            cnt=len(frcs[xx])
        else:
            for xxx in frcs[xx]:
                cnt+=frcs[xx][xxx]
        x.append(ind)
        ind+=1
        if opt2==0:
            y.append((xx,float(cnt)/clustcnt[xx]))
        elif opt2==1:
            y.append((xx,float(cnt)/len(frcs[xx])))
        else:
            y.append((xx,float(cnt)/clustcnt[xx]))
                
    y=sorttupr(y,1)
    lenn=100
    if len(y)<100:
        lenn=len(y)
    yy=y[:lenn]
    y=[]
    l=[]
    c=[]
    for tup in yy:
        l.append(str(tup[0]))
        y.append(tup[1])
        c.append((clustavgscore[tup[0]],0,1.0-clustavgscore[tup[0]]))
    #print(name)
    #m=max(y)
    #for i in range(0,lenn):
        #y[i]=y[i]/m
    fig=plt.figure(figsize=(50,30))
    bg=fig.add_subplot(111)
    #fig=plt.figure(figsize=(5,3))
    #bg = fig.add_subplot(111)
    bg.set_position([.1,.25,.8,.70])
    #bg.yaxis.set_smart_bounds(True))
    #y.sort(reverse=True)
    bg.bar(x[:lenn],y,width=1, color=c, tick_label=l)
    nx=[]
    for xxx in x[:lenn]:
        nx.append(xxx+.5)
    plt.xticks(nx, l)
    option2=""
    if opt2==0:
        bg.yaxis.set_label_text("#following/#accounts in cluster",fontsize=20)
        option2="eq1(x)"
    elif opt2==1:
        bg.yaxis.set_label_text("#following/#accounts in cluster who are following",fontsize=20)
        option2="eq2(x)"
    else:
        bg.yaxis.set_label_text("#accounts in cluster who are following/#accounts in cluster",fontsize=20)
        option2="eq3(x)"
    name=name+" "+option2
    bg.xaxis.set_tick_params(labelsize=15)
    bg.yaxis.set_tick_params(labelsize=20)
    bg.xaxis.set_label_text("Clusters",fontsize=20)
    #plt.title(option2+" vs clusters ("+option+")")
    #plt.savefig(name+".pdf")
    plt.savefig(name+".png")
    #print(name)
    plt.close()    
def scatscorevsclustscore(sqlfile,name,opt=3,opt2=0):
    conn=sqlite3.connect(sqlfile)
    cur=conn.cursor()
    option=""
    q="select b.score,c.avgscore, b.sname from (select cluster,avg(score) as avgscore from (select b.sname,score,cluster from botornotscore as b, "
    if opt==1:
        q=q+"ourclusterscore as o where o.sname=b.sname) as c group by cluster) as c, ourclusterscore as o,"
        option="ourclusterscore"
    elif  opt==2:
        q=q+"ourclustersubscore as o where o.sname=b.sname) as c group by cluster) as c, ourclustersubscore as o,"
        option="ourclustersubscore"
    elif  opt==3:
        q=q+"ourclusterscoresubscore as o where o.sname=b.sname) as c group by cluster) as c, ourclusterscoresubscore as o,"
        option="ourclusterscoresubscore"
    q=q+" botornotscore as b where b.sname=o.sname and o.cluster=c.cluster;"
    name=name+option
    data=[]
    option2=""
    if opt2!=0:
        option2="manually identified"
        cur.execute("select * from catag2;")
        data=cur.fetchall()
        cat={}
        for tup in data:
            cat[tup[0]]=tup[1]
    else:
        option2="all"
    name=name+" "+option2
    #print(q)
    #print(opt)
    cur.execute(q)    
    clustavgscore={}
    y=[]
    x=[]
    c=[]
    for i in cur.fetchall():
        if opt2!=0:
            try:
                if cat[i[2]]==0:
                    c.append((0,0,1.0,0.5))
                elif cat[i[2]]==1:
                    c.append((1.0,0,0,0.5))
                else:
                    c.append((0,1.0,0,0.5))
                x.append(i[0])
                y.append(i[1])                
            except:
                pass
        else:
            c.append((i[1],0,1-i[1],0.3))
            x.append(i[0])
            y.append(i[1])
        #print(i)
    fig=plt.figure(figsize=(50,30))
    bg=fig.add_subplot(111)
    bg.scatter(x,y,s=25,c=c)
    bg.grid(True)
    for line in bg.get_ygridlines():
        line.set_linestyle('-')
    bg.xaxis.set_label_text("individual score",fontsize=20)
    bg.xaxis.set_tick_params(labelsize=20)
    bg.yaxis.set_tick_params(labelsize=20)
    bg.yaxis.set_label_text("average cluster score",fontsize=20)
    #plt.title("average cluster score vs individual score ("+option+" "+option2+")")
    #bg.scatter(xb,ourbots,s=25,c=(1,0,0,.5),marker="o")
    #plt.savefig(name+".pdf")
    plt.savefig(name+".png")
    #print(name)
    plt.close()
def graphallclustersalltypes(sqlfile):
    base="graphs"
    try:
        os.mkdir(base)
    except:
        pass
    b1=base+"\\average clust score vs individual score"
    try:
        os.mkdir(b1)
    except:
        pass
    b2=base+"\\bar hash vs clust"
    try:
        os.mkdir(b2)
    except:
        pass
    b3=base+"\\bar score vs account"
    try:
        os.mkdir(b3)
    except:
        pass
    b4=base+"\\bot score scat"
    try:
        os.mkdir(b4)
    except:
        pass
    b5=base+"\\rt cnt vs cluster"    
    try:
        os.mkdir(b5)
    except:
        pass
    b6=base+"\\score vs avg category score"
    try:
        os.mkdir(b6)
    except:
        pass
    b7=base+"\\at cnt vs cluster"    
    try:
        os.mkdir(b7)
    except:
        pass
    b8=base+"\\follower cnt vs cluster"    
    try:
        os.mkdir(b8)
    except:
        pass
    b9=base+"\\following cnt vs cluster"    
    try:
        os.mkdir(b9)
    except:
        pass
    b10=base+"\\listed cnt vs cluster"    
    try:
        os.mkdir(b10)
    except:
        pass
    b11=base+"\\favorited cnt vs cluster"    
    try:
        os.mkdir(b11)
    except:
        pass
    b12=base+"\\url cnt vs cluster"    
    try:
        os.mkdir(b12)
    except:
        pass
    d1="\\all"
    d2="\\cluster by both"
    d3="\\cluster by category scores"
    d4="\\cluster by score"
    try:
        os.mkdir(b1+d2)
    except:
        pass
    try:
        os.mkdir(b1+d3)
    except:
        pass
    try:
        os.mkdir(b1+d4)
    except:
        pass
    try:
        os.mkdir(b2+d1)
    except:
        pass
    try:
        os.mkdir(b2+d2)
    except:
        pass
    try:
        os.mkdir(b2+d3)
    except:
        pass
    try:
        os.mkdir(b2+d4)
    except:
        pass
    try:
        os.mkdir(b5+d2)
    except:
        pass
    try:
        os.mkdir(b5+d3)
    except:
        pass
    try:
        os.mkdir(b5+d4)
    except:
        pass
    try:
        os.mkdir(b7+d2)
    except:
        pass
    try:
        os.mkdir(b7+d3)
    except:
        pass
    try:
        os.mkdir(b7+d4)
    except:
        pass
    try:
        os.mkdir(b8+d2)
    except:
        pass
    try:
        os.mkdir(b8+d3)
    except:
        pass
    try:
        os.mkdir(b8+d4)
    except:
        pass
    try:
        os.mkdir(b9+d2)
    except:
        pass
    try:
        os.mkdir(b9+d3)
    except:
        pass
    try:
        os.mkdir(b9+d4)
    except:
        pass
    try:
        os.mkdir(b10+d2)
    except:
        pass
    try:
        os.mkdir(b10+d3)
    except:
        pass
    try:
        os.mkdir(b10+d4)
    except:
        pass
    try:
        os.mkdir(b11+d2)
    except:
        pass
    try:
        os.mkdir(b11+d3)
    except:
        pass
    try:
        os.mkdir(b11+d4)
    except:
        pass
    try:
        os.mkdir(b12+d2)
    except:
        pass
    try:
        os.mkdir(b12+d3)
    except:
        pass
    try:
        os.mkdir(b12+d4)
    except:
        pass
    for i in range(0,50):
        try:
            os.mkdir(b2+d2+"\\c"+str(i))
        except:
            pass
        try:
            os.mkdir(b2+d3+"\\c"+str(i))
        except:
            pass
        try:
            os.mkdir(b2+d4+"\\c"+str(i))
        except:
            pass
    scatgraphbotvscore("udataf3.sqlite",b4+"\\scorenbotcolor")
    scoretoavgcat(sqlfile,b6+"\\svacs",0)
    scoretoavgcat(sqlfile,b6+"\\svacs",1)
    bargraphbotvscore(sqlfile,b3+"\\bsvaclr",0)
    bargraphbotvscore(sqlfile,b3+"\\bsvaclr",1)
    bargraphbotvscore(sqlfile,b3+"\\bsvaclr",2)
    for opt in range(0,4):
        d=""
        if opt==0:
            d=d1
        elif opt==3:
            d=d2
        elif opt==2:
            d=d3
        else:
            d=d4
        if opt!=0:
            scatscorevsclustscore(sqlfile,b1+d+"\\csvs",opt,0)
            scatscorevsclustscore(sqlfile,b1+d+"\\csvs",opt,1)
            makertbar(sqlfile,b5+d+"\\rtubyc",opt,0)
            makertbar(sqlfile,b5+d+"\\rtubyc",opt,1)
            makertbar(sqlfile,b5+d+"\\rtubyc",opt,2)
            makeatbar(sqlfile,b7+d+"\\atubyc",opt,0)
            makeatbar(sqlfile,b7+d+"\\atubyc",opt,1)
            makeatbar(sqlfile,b7+d+"\\atubyc",opt,2)
            makefollerbar(sqlfile,b8+d+"\\foubyc",opt,0)
            makefollerbar(sqlfile,b8+d+"\\foubyc",opt,1)
            makefollerbar(sqlfile,b8+d+"\\foubyc",opt,2)
            makefollingbar(sqlfile,b9+d+"\\faubyc",opt,0)
            makefollingbar(sqlfile,b9+d+"\\faubyc",opt,1)
            makefollingbar(sqlfile,b9+d+"\\faubyc",opt,2)
            makelistedbar(sqlfile,b10+d+"\\liubyc",opt,0)
            makelistedbar(sqlfile,b10+d+"\\liubyc",opt,1)
            makelistedbar(sqlfile,b10+d+"\\liubyc",opt,2)
            makefavedbar(sqlfile,b11+d+"\\faubyc",opt,0)
            makefavedbar(sqlfile,b11+d+"\\faubyc",opt,1)
            makefavedbar(sqlfile,b11+d+"\\faubyc",opt,2)
            makeurlsbar(sqlfile,b12+d+"\\urlubyc",opt,0)
            makeurlsbar(sqlfile,b12+d+"\\urlubyc",opt,1)
            makeurlsbar(sqlfile,b12+d+"\\urlubyc",opt,2)
        for i in range(0,50):
            c=""
            if opt!=0:
                c="\\c"+str(i)
            makehashbar(sqlfile,b2+d+c+"\\bhvc",opt,0,i)
            makehashbar(sqlfile,b2+d+c+"\\bhvc",opt,1,i)
            makehashbar(sqlfile,b2+d+c+"\\bhvc",opt,2,i)
            if opt==0:
                break
#graphallclustersalltypes("udataf3.sqlite")