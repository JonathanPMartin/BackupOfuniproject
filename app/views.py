from multiprocessing import Value
from .meta import *
import requests
import datetime
import asyncio
import string
import random
import time
import json
from nltk.tokenize import word_tokenize
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from nltk import ne_chunk, pos_tag
from nltk.tree import Tree
import os
import re
import threading
import hashlib
from bs4 import BeautifulSoup
import pycountry
from werkzeug.utils import secure_filename
def GetLeaders():
    Leaders={
        'Conservative':["Michael Howard","David Cameron","Theresa May","Boris Johnson","Liz Truss","Rishi Sunak"],
        'Labour':["Tony Blair","Gordon Brown","Harriet Harman","Ed Miliband","Jeremy Corbyn","Keir Starmer"],
        'LibDem':["Charles Kennedy","Sir Menzies Campbell","Nick Clegg","Tim Farron","Sir Vince Cable","Jo Swinson","Sir Ed Davey"]
    }
    return Leaders
def CheckPolLean(Site):
    SitePage=Site+".txt"
    f = open(SitePage, "r")

    test=f.readlines()
    Urls=[]
    for i in test:
        tem=i.split("\n")
        Urls.append(tem[0])
    
    Leaders=GetLeaders()
    LabourLeaders=Leaders["Labour"]
    
    ConservativeLeaders=Leaders["Conservative"]
    LibDemLeaders=Leaders["LibDem"]
    temUrls=[]
    for i in range(0,10):
        temUrls.append(Urls[i])
    for i in Urls:
        query="SELECT * FROM SiteData WHERE SiteName = '{}'".format(Site)
        rows = query_db(query)
        data=rows[0]
        r = requests.get(i, allow_redirects=False)
        #r = requests.get(i)
        r=r.text
        soup = BeautifulSoup(r, 'html.parser')
        text=soup.get_text()
        Labour=0
        LibDem=0
        Conservative=0
        Party=""
        for j in LabourLeaders:
            if j in text:
                Labour=Labour+1
                
        for j in ConservativeLeaders:
            if j in text:
                Conservative=Conservative+1
                
        for j in LibDemLeaders:
            if j in text:
                LibDem=LibDem+1
                
       
        sia = SentimentIntensityAnalyzer()
        scores=sia.polarity_scores(text)
        addscore=0
        check=False
        if scores['neg']>scores['pos']:
            addscore=-1
        else:
            addscore=1
        if (Labour> LibDem)&(Labour>Conservative):
            Party="Lab"
            addscore=data["LabourScore"]+addscore
            addtotal=data["LabourCount"]+1
            check=True
            theQry = "Update SiteData Set LabourScore ={},LabourCount={} Where SiteName = '{}'".format(addscore,addtotal,Site)
            
            userQry = write_db(theQry)
            

        elif (LibDem>Labour) &(LibDem>Conservative):
            Party="Lib"
            addscore=data["LibDemScore"]+addscore
            addtotal=data["LibDemCount"]+1
            check=True
            theQry = "Update SiteData Set LibDemScore ={},LibDemCount={} Where SiteName = '{}'".format(addscore,addtotal,Site)
            
            userQry = write_db(theQry)
            
        elif (Conservative>Labour) &(Conservative>LibDem):
            Party="Con"
            addscore=data["ConservativeScore"]+addscore
            addtotal=data["ConservativeCount"]+1
            check=True
            theQry = "Update SiteData Set ConservativeScore ={},ConservativeCount={} Where SiteName = '{}'".format(addscore,addtotal,Site)
            userQry = write_db(theQry)
        else:
            useless=0
        print(check)
    print(rows[0])
def GetStockInfo(Stock,Start,End):
    url="https://api.twelvedata.com/time_series?symbol="+Stock+"&interval=30min&start_date="+Start+"&end_date="+End+"&apikey=5eb91eed0cb149eaa54cb7acc41210ee&source=docs"
    res=requests.get(url)
    resJson=res.json()
    values=resJson['values']
    return values
   #url="https://api.twelvedata.com/time_series?symbol=AAPL&interval=30min&start_date=2020-01-01&end_date=2023-01-01&apikey=5eb91eed0cb149eaa54cb7acc41210ee&source=docs"
  
def News2(site):
    url="https://newsapi.org/v2/everything?q=politics&domains="+site+"&apiKey=54de7376d5474ca0a6e7ec9ecd81ca26"
    tem="https://newsapi.org/v2/everything?q=politics&domains=bbc.co.uk&apiKey=54de7376d5474ca0a6e7ec9ecd81ca26"
    print(url)
    res=requests.get(url)
    open_page=res.json()
    article=open_page['articles']
    results=[]
    source={}
    sitename=site.split('.')
    sitename=sitename[0]
    print(sitename)
    File=sitename+'.txt'
    with open(File,'a') as outfile:
        outfile.write('')
    with open(File,'r') as infile:
        filetext=infile.read()
    for ar in article:
        tem=ar['url']
        if ar['url'] in filetext:
            useless=0
        else:
            results.append(tem)
       
    for i in results:
        with open(File,'a') as outfile:
            outfile.write(i+'\n')
   
    return results
def News3(site,Topic):
    url="https://newsapi.org/v2/everything?q="+Topic+"&domains="+site+"&apiKey=54de7376d5474ca0a6e7ec9ecd81ca26"
    #url="https://newsapi.org/v2/everything?q="+Topic+"&domains="+site+"&apiKey=e3fff7fc440542c9923ebfd16005136f"
    res=requests.get(url)
    open_page=res.json()
    article=open_page['articles']
    results=[]
    source={}
    sitename=site.split('.')
    sitename=sitename[0]
    print(sitename)
    File=sitename+'.txt'
    with open(File,'a') as outfile:
        outfile.write('')
    with open(File,'r') as infile:
        filetext=infile.read()
    for ar in article:
        tem=ar['url']
        if ar['url'] in filetext:
            useless=0
        else:
            results.append(tem)
       
    for i in results:
        with open(File,'a') as outfile:
            outfile.write(i+'\n')
   
    return results
def NewsFromSite(site):
    queryparams={
        "source":site,
        "sortBy":"top",
        "apiKey":"54de7376d5474ca0a6e7ec9ecd81ca26"
    }
    mainurl="https://newsapi.org/v1/articles"
    res=requests.get(mainurl,params=queryparams)
    open_page=res.json()
    article=open_page['articles']
    results=[]
    for ar in article:
        tem=[ar['title'],ar['url']]
        results.append(tem)
    return results
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
def PageLog(page):
    date=datetime.datetime.now()
    usercheck= request.cookies.get('session2')
    user=0
    if usercheck!="":
        user=usercheck[13]
    theQry = f"INSERT INTO PageLog (id, PageName, VistDate,AuthUser) VALUES (NULL, '{page}', '{date}',{user})"
    #print(theQry)
    userQry = write_db(theQry)
    flask.session["admin"] = 'test'
glob=""
glob2=False
def clean(user):
    data=string.ascii_lowercase
    data3=[]
    for char in data:
        data3.append(char)
    print(data)
    data2=[]
    for char in data:
        data2.append(char.upper())
    data=data3+data2+["1","2","3","4","5","6","7","8","9","0","-","_",".","@"," ","!"]
        
    for char in user:
        if char in data:
            usless=0
        else:
            user=""    

    return user
def salt(Pass):
    #Pass=hashlib.sha256(Pass.encode()).hexdigest()
    List=[' ','a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '!', '£', '$', '%', '^', '&', '*', '(', ')','α','β','γ','δ','ε','ζ','η','θ','ι','κ','λ','μ','ν','ξ','ο''π','ρ','ϲ','τ','υ','φ','χ''ψ','ω','Α','Β','Γ','s', 't', 'u', 'v', 'w', 'x']
    Rand=[633, 101, 286, 510, 885, 183, 331, 446, 747, 688, 487, 963, 760, 505, 485, 622, 983, 736, 737, 639, 852, 369, 232, 151, 464, 444, 236, 528, 538, 304, 238, 789, 977, 741, 451, 601, 572, 548, 661, 745, 583, 293, 748, 904, 325, 145, 186, 122, 542, 167, 906, 541, 497, 468, 981, 997, 790, 258, 583, 612, 111, 805, 411, 952, 964, 688, 960, 152, 378, 634, 442, 851, 298, 769, 723, 110, 461, 928, 638, 434, 972, 569, 715, 963, 410, 456, 176, 693, 711, 635, 408, 317, 672, 961, 300, 269, 598, 809, 567, 762, 527, 138, 142, 372, 359]
    
    Return=''
    BIG=1
    for i in range(0,len(Pass)):
        for j in range(0,len(List)):
            if Pass[i]==List[j]:
                BIG=BIG*Rand[j]
    BIG=BIG**2           
    BIG=str(BIG)
    #print(BIG)
    for i in range(0,len(BIG)-1):
        tem=str(BIG[i])+str(BIG[i+1])
        tem=int(tem)
        Return=Return+List[tem]
        tem2=str(BIG[i+1])+str(BIG[i])
        tem2=int(tem2)
        #print(tem2)
        #print(tem)
        Return=Return+List[tem2]
    print(Return)
    Hash=hashlib.md5(Return.encode()).hexdigest()
    #return Hash
    return Hash
def PartyDataClean(Party,TextNum):
    data=3
@app.route("/imageuplaod", methods=['GET', 'POST'])
def upload_file():
    cookie = request.cookies.get('session2')
    print("COOKIE BELOW ON REVIEW")
    print(cookie)
    if len(cookie)>14:
        Qry="Select * FROM roles WHERE userID= {0}".format(cookie[13])
        role = query_db(Qry, one=True)
        role=role['userRole']
        if role=='admin':
            print("this guy is an admin")
        else:
            return redirect("https://habitatcrater-geniusgenesis-5000.codio-box.uk/logout", code=302)
    else:
        return redirect("https://habitatcrater-geniusgenesis-5000.codio-box.uk/logout", code=302)
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flask.flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            useless=0
            filename = secure_filename(file.filename)
            basedir = os.path.abspath(os.path.dirname(__file__))
            file.save(os.path.join(basedir,app.config['UPLOAD_FOLDER'], filename))
            #return redirect(url_for('download_file', name=filename))
    resp = make_response(render_template("image.html"))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    <a href="https://habitatcrater-geniusgenesis-5000.codio-box.uk/">Home</a>
    '''
@app.route("/")
def index():
  
    """
    Main Page.
    """

    #Get data from the DB using meta function
    
    rows = query_db("SELECT * FROM product")
    app.logger.info(rows)
    resp = make_response(render_template("index.html", bookList = rows))
    global glob
    global glob2
    if glob2:
        resp.set_cookie('session2', '', expires=0)
    else:
        
        if glob!="":
            resp.set_cookie('session2', glob, httponly = True)
            resp.set_cookie('attemps', '', expires=0)
    resp.set_cookie('session2', glob, httponly = True)       
    return resp

@app.route("/newsData")

def news():
    directory=os.getcwd()
    print(directory)
    #Sources=NewsFromSite('bbc-news')

    NewsPapers=['dailymail.co.uk','independent.co.uk','express.co.uk','theguardian.com','telegraph.co.uk',"bbc.co.uk"]
    PoliticalLeaders=["David Cameron","Theresa May","Boris Johnson","Liz Truss","Rishi Sunak","Tony Blair","Gordon Brown","Ed Miliband","Jeremy Corbyn","Keir Starmer","Charles Kennedy","Sir Menzies Campbell","Nick Clegg","Tim Farron","Sir Vince Cable","Jo Swinson","Sir Ed Davey"]
    for i in NewsPapers:
        for j in PoliticalLeaders:
            News3(i,j)

    """
    News2('bbc.co.uk')
    News2('dailymail.co.uk')
    News2('thetimes.co.uk')
    News2('express.co.uk')
    News2('independent.co.uk')
    News2('mirror.co.uk')
    News2('thetimes.co.uk')
    News2('telegraph.co.uk')
   """ 
    Sources=['1','2']
    async def Clean(URL,Site,Count):
        r = requests.get(URL)
        r=r.text
        soup = BeautifulSoup(r, 'html.parser')
        bigtest=soup.p.get_text()
        #print(soup.get_text())
        wash=r.split('<')
        tem=[]
        for i in wash:
            if 'script' in i[0:7]:
                useless=0
            elif 'style' in i[0:7]:
                useless=0
            elif '{' in i[0:7]:
                useless=0
            elif '&'in i[0:7]:
                useless=0
            else:
            
                if '>' in i:
                    tem2=0
                    for j in range(0,len(i)):
                        if i[j]=='>':
                            tem2=j
                    tem3=i[tem2+1:len(i)]
                    if tem3!='':
                        if tem3!=' ':
                            #print(tem3[0])
                            #print(tem3)
                            tem.append(tem3)
                            
                                               
                        
                            #tem.append(tem3)
       
        alpha=['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
        Return=[]
        for i in tem:
            if "\n" in i:
                usless=0
            else:
                if len(i)>2:
                    if i[1]=='x':
                        useless=0
                    else:
                        Return.append(i)
            #print('test')
        Count=str(Count)
        Src="/home/codio/workspace/6005-CW-Teplate/"
        File=Site+Count
        # Directory
        directory = Site
        
        # Parent Directory path
        parent_dir = Src
        
        # Path
        path = os.path.join(parent_dir, directory)
        
        # Create the directory
        # 'GeeksForGeeks' in
        # '/home / User / Documents'
        completeName = os.path.join(path, File+".txt")
        #/home/codio/workspace/6005-CW-Teplate
        f = open(completeName, "w")
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', r)   
        #f.write(cleantext)
        #f.write(r)
        for i in Return:
            if 'script' in i[0:7]:
                useless=0
            elif 'style' in i[0:7]:
                useless=0
            elif '{' in i[0:7]:
                useless=0
            elif '&'in i[0:7]:
                useless=0
            elif '('in i[0:7]:
                usless=0
            elif ')'in i[0:7]:
                usless=0
            elif '()' in i:
                usless=0
            elif '?' in i[0:7]:
                usless=0
            elif '!' in i[0:7]:
                usless=0
            elif '=' in i[0:7]:
                usless=0

            else:
                tem=i.split(" ")
                List=[]
                if len(tem)>5:
                    for k in tem:
                        if "&#x27;" in k:
                            tem2=k.split("&#x27;")
                            if len(tem2)>1:
                                tem3=tem2[0]+"'"+tem2[1]
                                List.append(tem3)
                            else:
                                tem3=tem2[0]+"'"
                                List.append(tem3)
                        elif 'â' in k:
                            tem2=k.split("â")
                            if len(tem2)>1:
                                tem3=tem2[0]+"'"+tem2[1]
                                List.append(tem3)
                            else:
                                tem3=tem2[0]+"'"
                                List.append(tem3)
                        elif "&quot;" in k:
                            temWhatever=k.split("&quot;")
                            for newloop in temWhatever:
                                 List.append(newloop)



                                
                                    
                        else:
                            List.append(k)

                    #f.write(i+'\n')
                    for k in range(0,len(List)-1):
                        f.write(List[k]+" ")
                    tem4=len(List)-1
                    f.write(List[tem4]+'\n')

        f.close()
        f = open(completeName, "w")
        f.write(bigtest)
        f.close()
        return Return
    def Attempt(URL):
        Return="LOG IN Failed"
        r = requests.get(URL)
        r=r.text
        return r
    data='<ttt<ttt>words'
    #data2=Attempt('https://www.conservatives.com/our-plan')
    #data3=Attempt('https://www.conservatives.com/our-plan')
    
    async def BigOlLoop(Site):
        x=0
        SitePage=Site+".txt"
        f = open(SitePage, "r")
        test=f.readlines()
        tem=test[0].split("\n")
        await Clean(tem[0],Site,x)
        for i in test:
            tem=i.split("\n")
            await Clean(tem[0],Site,x)
            
            x=x+1
          
            
            
            #print(tem[0])
        f.close()
        flask.render_template("news.html",sources = ['Loading Shit'])
        
         
    #BigOlLoop("telegraph")
    async def mul(x, y):
        return x * y
    asyncio.set_event_loop(asyncio.SelectorEventLoop())
    loop = asyncio.get_event_loop()

    #res = loop.run_until_complete(BigOlLoop("dailymail"))
    #res = loop.run_until_complete(BigOlLoop("express"))
    #res = loop.run_until_complete(BigOlLoop("independent"))
    #res = loop.run_until_complete(BigOlLoop("Labour"))
    #res = loop.run_until_complete(BigOlLoop("theguardian"))
    #print(res)

    loop.close()
    #Clean('https://www.conservatives.com/our-plan',"Con","1")


    
    
    return flask.render_template("news.html",sources = Sources)
    
@app.route("/newsData2")
def test():
    #CheckPolLean("bbc")
    #CheckPolLean("dailymail")
    #CheckPolLean("independent")
    #CheckPolLean("telegraph")
    CheckPolLean("theguardian")
    Src="/home/codio/workspace/6005-CW-Teplate/"
    File="LibDem"+"1"
        
    directory = "LibDem"
        
    parent_dir = Src
        
    path = os.path.join(parent_dir, directory)
    completeName = os.path.join(path, File+".txt")
    text=open(completeName,encoding="utf-8").read()
    
    bee=open("bee.txt",encoding="utf-8").read()
    beelowercase=bee.lower()
    beecleantext=beelowercase.translate(str.maketrans('','',string.punctuation))
    beeList=word_tokenize(beecleantext,"english")
    """
    FinalbeeList=[]
    for i in beeList:
        if i in keys:
            useless=0
        elif i in stopwords.words('english'):
            useless=0
        else:
            FinalbeeList.append(i)
    f=open("bee.txt","w")
    for i in FinalbeeList:
        f.write(i)
        f.write(" ")
    f.close()"""
    """
    nltk_results = word_tokenize(text,"english")
    firstclean=[]
    for nltk_result in nltk_results:
        if type(nltk_result) == Tree:
            useless=0
        else:
            firstclean.append(nltk_result)
    text2=""
    for i in firstclean:
        text2=text2+i+" "

    lowercase=text2.lower()
    cleantext=lowercase.translate(str.maketrans('','',string.punctuation))
    tokenwords=word_tokenize(cleantext,"english")
    finalwords=[]
    for i in tokenwords:
        if i in stopwords.words('english'):
            useless=0
        elif i in beeList:
            useless=0
        else:
            finalwords.append(i)"""
    rows = query_db("SELECT * FROM SiteData")
    #print(rows)
    return flask.render_template("news.html",sources = rows)

@app.route("/newsData3")
def test2():
    rows = query_db("SELECT * FROM SiteData")
    #print(rows)
    return flask.render_template("news.html",sources = rows)
   
@app.route("/newsData4")
def test3():
    theQry = "Update SiteData Set LabourScore =0,LabourCount=0,LibDemCount=0,LibDemScore=0,ConservativeCount=0,ConservativeScore=0 Where SiteName != 'Smith'"
    userQry = write_db(theQry)
    rows = query_db("SELECT * FROM SiteData")
    #print(rows)
    return flask.render_template("news.html",sources = rows)
@app.route("/GetStock/<CurStock>")
def stock(CurStock):
    #url="https://api.twelvedata.com/time_series?symbol=AAPL&interval=30min&start_date=2020-01-01&end_date=2023-01-01&apikey=5eb91eed0cb149eaa54cb7acc41210ee&source=docs"
    stock=CurStock
    data=GetStockInfo(stock,'2020-01-01','2023-01-01')
    #Qry="INSERT INTO StockInfo (Stock, Value, time, day, month, year) VALUES ('APPl',20.4,'10:30','01','02','2022')"
    #Qry="INSERT INTO StockInfo (Stock, Value, time, day, month, year) VALUES ('AAPL',128.9,'15:30:','30','12','2022')"
    #userQry = write_db(Qry)
    """
    time=data[0]["datetime"]
    year=time[0:4]
    month=time[5:7]
    day=time[8:10]
    hour=time[11:16]
    value=float(data[0]["open"])
    """
    #Qry="INSERT INTO StockInfo (Stock, Value, time, day, month, year) VALUES ('{}',{},'{}','{}','{}','{}')".format(stock,value,hour,day,month,year)
    
    #print(Qry)
    #userQry =  write_db(Qry)
    x=True
    while x:
        
        for i in range(0,len(data)):
            time=data[i]["datetime"]
            year=time[0:4]
            month=time[5:7]
            day=time[8:10]
            hour=time[11:16]
            value=float(data[i]["open"])
            Qry="INSERT INTO StockInfo (Stock, Value, time, day, month, year) VALUES ('{}',{},'{}','{}','{}','{}')".format(stock,value,hour,day,month,year)
            userQry =  write_db(Qry)
            #print('true')
            print(time[0:10])
        tem=data[len(data)-1]["datetime"]
        year=tem[0:4]
        if year=='2020':
            x=False
        else:
            
            data=GetStockInfo(stock,'2020-01-01',tem[0:10])
    #Qry="INSERT INTO StockInfo (Stock, Value, time, day
        
    return flask.render_template("news.html",sources =data)
@app.route("/CalStockTimeDif/<CurStock>")
def Stock2(CurStock):
    Qry="select  day, month, year from StockInfo where Stock='{}' and time='15:00'".format(CurStock)
    userQry=query_db(Qry)
    data=[]
    data2=[]
    for i in userQry:
        tem=[]
        tem.append(i["day"])
        tem.append(i["month"])
        tem.append(i["year"])
        data.append(tem)
    #data=[data[2]]
    for i in data:
        Values=[]
        Times=[]
        Qry="select Value,time from StockInfo where Stock='{}' and day='{}' and month='{}' and year='{}'".format(CurStock,i[0],i[1],i[2])
        Qry2=query_db(Qry)
        
        for j in Qry2:
            Values.append(j["Value"])
            Times.append(j["time"])
        for j in range(0,len(Qry2)-1):
           val1=Qry2[j]["Value"]
           time1=Qry2[j]["time"]
           val2=0
           time2=0
           for k in range(j+1,len(Qry2)):
               val2=Qry2[k]["Value"]
               time2=Qry2[k]["time"]
               rate=0
               change="NA"
               if val1<val2:
                     rate=(((val2-val1)/val2)*100)
                     change="DOWN"
               elif val2<val1:
                    rate=(((val1-val2)/val2)*100)
                    change="UP"
               Qry="INSERT INTO StockCompare (Stock, Time1, Time2,Change,Rate, day, month, year) VALUES ('{}','{}','{}','{}',{},'{}','{}','{}')".format(CurStock,time2,time1,change,rate,i[0],i[1],i[2])
               userQry =  write_db(Qry)
           
               print(change)
           
          
           print(time2)
        """for j in range(len(Values)-2,len(Values)-1):
            print(Times[j])
            print(Values[j])
            print(Times[j+1])
            print(Values[j+1])
            for k in range(j+1,len(Values)):
                print(i)
                print(j<k)
                rate=0
                change="NA"
                if(j<k):
                    rate=(((Values[k]-Values[j])/Values[k])*100)
                    change="UP"
                elif(k<j):
                    rate=(((Values[j]-Values[k])/Values[k])*100)
                    change="DOWN"
                else:
                   usless=0
                Qry="INSERT INTO StockCompare (Stock, Time1, Time2,Change,Rate, day, month, year) VALUES ('{}','{}','{}','{}',{},'{}','{}','{}')".format(CurStock,Times[k],Times[j],change,rate,i[0],i[1],i[2])
                userQry =  write_db(Qry)
                
        data2=Times
        """
            
    return flask.render_template("news.html",sources =data)
    
@app.route("/products", methods=["GET","POST"])

def products():
  
    PageLog('Products')
    """
    Single Page (ish) Application for Products
    """
    theItem = flask.request.args.get("item")
    if theItem:
        
        #We Do A Query for It
        #vunrable to sql injection  uses quote marks when starting server use this to select data not intended fix for cw1 is to filter any data that is not of type int
        itemQry = query_db(f"SELECT * FROM product WHERE id = ?",[theItem], one=True)

        #And Associated Reviews
        #reviewQry = query_db("SELECT * FROM review WHERE productID = ?", [theItem])
        theSQL = f"""
        SELECT * 
        FROM review
        INNER JOIN user ON review.userID = user.id
        WHERE review.productID = {itemQry['id']};
        """
        reviewQry = query_db(theSQL)
        
        #If there is form interaction and they put somehing in the basket
        if flask.request.method == "POST":

            quantity = flask.request.form.get("quantity")
            quantity=clean(quantity)
            try:
                #int convertion might be good enough to prevent sql injection here test anyway
                quantity = int(quantity)
            except ValueError:
                flask.flash("Error Buying Item")
                return flask.render_template("product.html",
                                             item = itemQry,
                                             reviews=reviewQry)
            
            app.logger.warning("Buy Clicked %s items", quantity)
            
            #And we add something to the Session for the user to keep track
            basket = flask.session.get("basket", {})

            basket[theItem] = quantity
            flask.session["basket"] = basket
            flask.flash("Item Added to Cart")

            
        return flask.render_template("product.html",
                                     item = itemQry,
                                     reviews=reviewQry)
    else:
        
        books = query_db("SELECT * FROM product")        
        return flask.render_template("products.html",
                                     books = books)


# ------------------
# USER Level Stuff
# ---------------------
    
@app.route("/user/login", methods=["GET", "POST"])
def login():
    """
    Login Page
    """
    PageLog('Login')
    cookie=""
    resp = make_response(render_template('login.html'))
    resp.set_cookie('session2', cookie)
    
    
    if flask.request.method == "POST":
		
        #Get data
        user = flask.request.form.get("email")
        user=clean(user)
        #username and password might be vunrable to injection needs test
        #https://www.w3schools.com/python/ref_string_format.asp
        #site above alowed to demonstate possilbe vunrablity if fed '' at end of string 
        password = salt(flask.request.form.get("password"))
        app.logger.info("Attempt to login as %s:%s", user, password)

        theQry = "Select * FROM User WHERE email = '{0}'".format(user)
        
   
        userQry =  query_db(theQry, one=True)
        data=string.ascii_lowercase
        data3=[]
        for char in data:
            data3.append(char)
        print(data)
        data2=[]
        for char in data:
            data2.append(char.upper())
        data=data3+data2+["1","2","3","4","5","6","7","8","9","0","-","_",".","@"," ","!"]
        for i in range(0,13):
           # print(i)
            cookie = cookie+ data[random.randint(0,len(data)-1)]
        cookie = cookie+str(userQry["id"])
        #print(cookie[13])    
        for i in range(0,21):
            cookie= cookie+ data[random.randint(0,len(data)-1)]
        print('COOKIE')
        print(cookie)
        global glob
        glob=cookie
        def MakeCookie(cookie):
            resp = make_response(render_template('login.html'))
            resp.set_cookie('session2', cookie)
            return resp
        MakeCookie('test')
        if userQry is None:
            flask.flash("No Such User")
        else:
            app.logger.info("User is Ok")
            print("PASSWORD")
            print(userQry["password"])
            #print(salt(userQry["password"]))
            if userQry["password"] == password:
                app.logger.info("Login as %s Success", userQry["email"])
                flask.session["user"] = userQry["id"]
                flask.flash("Login Successful")
                return (flask.redirect(flask.url_for("index")))
            else:
                flask.flash("Password is Incorrect")
    
    print("GLOB IS BELLOW")
    print(glob)
    attemps= request.cookies.get('attemps')
    print('LENGTH')
    print(attemps==None)
    if attemps==None:
        attemps=""
    attemps+="1"
    print("attemps")
    resp.set_cookie('attemps',attemps, httponly = True)  
    if len(attemps)<7:
        return resp
    else:
        flask.flash("You've had one to many failed attempts")
        return (flask.redirect(flask.url_for("index")))

@app.route("/user/create", methods=["GET","POST"])
def create():
    PageLog('Create')
    """ Create a new account,
    we will redirect to a homepage here
    """

    if flask.request.method == "GET":
        return flask.render_template("create_account.html")
    
    #Get the form data
    email = flask.request.form.get("email")
    email=clean(email)
    password = flask.request.form.get("password")
    password=clean(password)
    password=salt(password)
    #Sanity check do we have a name, email and password
    if not email or not password: 
        flask.flash("Not all info supplied")
        return flask.render_template("create_account.html",
                                     email = email)


    #Otherwise we can add the user
    #query bellow is vunrable to sql injection fix is to remove quote marks from string in all their forms 
    theQry = "Select * FROM User WHERE email = '{0}'".format(email)                                                   
    userQry =  query_db(theQry, one=True)
   
    if userQry:
        flask.flash("A User with that Email Exists")
        return flask.render_template("create_account.html",
                                     name = name,
                                     email = email)

    else:
        #Crate the user
        #might be vunrable im not sure
        app.logger.info("Create New User")
       
       
        

        theQry = f"INSERT INTO user (id, email, password) VALUES (NULL, '{email}', '{password}')"
        userQry = write_db(theQry)
        theQry = "Select * FROM User;"                                                 
        userQry =  query_db(theQry)
        lastid=userQry[-1]['id']
        theQry = f"INSERT INTO roles (id, UserID, userRole) VALUES (NULL, '{lastid}', 'user')"
        

        userQry = write_db(theQry)
        
        
        flask.flash("Account Created, you can now Login")
        return flask.redirect(flask.url_for("login"))

@app.route("/user/<userId>/settings")
def settings(userId):
    PageLog('Settings')
    """
    Update a users settings, 
    Allow them to make reviews
    """
    #two vunrablities 1st is sql seccond is that you could iterate over the userid in form after sql 
    theQry = "Select * FROM User WHERE id = '{0}'".format(userId)                                                   
    thisUser =  query_db(theQry, one=True)

    
    if not thisUser:
        flask.flash("No Such User")
        return flask.redirect(flask.url_for("index"))

    #Purchases
    #vunrable
    theSQL = f"Select * FROM purchase WHERE userID = {userId}"
    purchaces = query_db(theSQL)

    theSQL = """
    SELECT productId, date, product.name
    FROM purchase
    INNER JOIN product ON purchase.productID = product.id
    WHERE userID = {0};
    """.format(userId)

    purchaces = query_db(theSQL)
    cookie = request.cookies.get('session2')
    print("COOKIE BELOW ON REVIEW")
    print(cookie)
    if len(cookie)>14:
        Qry2 = "Select * FROM roles WHERE userID= {0}".format(cookie[13])
        role = query_db(Qry2, one=True)
        role=role['userRole']
    
        
        if role == "admin":
            return flask.render_template("adminsettings.html",user = thisUser,purchaces = purchaces)
        elif cookie[13]==userId:
            print("welp the problem is here")
            return flask.render_template("usersettings.html",user = thisUser,purchaces = purchaces)
        
        else:
            return redirect("https://habitatcrater-geniusgenesis-5000.codio-box.uk/logout", code=302)
    else:
        return redirect("https://habitatcrater-geniusgenesis-5000.codio-box.uk/logout", code=302)
    

@app.route("/terms")
def terms():
	return flask.render_template("terms.html")
@app.route("/logout")
def logout():
    """
    Login Page
    """
    PageLog('Logout')
    flask.session.clear()
    resp = flask.redirect(flask.url_for("index"))
    resp.set_cookie('attemps', '', expires=0)
    global glob2
    glob2=True
    return resp
    

#fucking update this shit dumbass currently not safe 
@app.route("/user/<userId>/update", methods=["GET","POST"])
def updateUser(userId):
    PageLog('Update')
    """
    Process any chances from the user settings page
    """
    cookie = request.cookies.get('session2')
    print("COOKIE BELOW ON REVIEW")
    print(cookie)
    Qry2 = "Select * FROM roles WHERE userID= {0}".format(cookie[13])
    role = query_db(Qry2, one=True)
    role=role['userRole']
    if len(cookie)>14:
        if cookie[13]==userId:
            print("welp the problem is here")
            usless=0
        
        elif role == "admin":
            usless=0
        else:
            return redirect("https://habitatcrater-geniusgenesis-5000.codio-box.uk/logout", code=302)
    else:
        return redirect("https://habitatcrater-geniusgenesis-5000.codio-box.uk/logout", code=302)
    #sql vunrable
    theQry = "Select * FROM User WHERE id = '{0}'".format(userId)   
    thisUser = query_db(theQry, one=True)
    if not thisUser:
        flask.flash("No Such User")
        return flask.redirect(flask_url_for("index"))

    #otherwise we want to do the checks
    if flask.request.method == "POST":
        current = flask.request.form.get("current")
        current = clean(current)
        password = flask.request.form.get("password")
        password=clean(password)
        #major vunrablity logging the userID current and password if any front end vunrablity is found this will be seized 
        app.logger.info("Attempt password update for %s from %s to %s", userId, current, password)
        app.logger.info("%s == %s", current, thisUser["password"])
        if current:
            
            if current == thisUser["password"]:
                app.logger.info("Password OK, update")
                #Update the Password
                #sql vunrable
                theSQL = f"UPDATE user SET password = '{password}' WHERE id = {userId}"
                app.logger.info("SQL %s", theSQL)
                write_db(theSQL)
                flask.flash("Password Updated")
                
            else:
                app.logger.info("Mismatch")
                flask.flash("Current Password is incorrect")
            return flask.redirect(flask.url_for("settings",
                                                userId = thisUser['id']))

            
    
        flask.flash("Update Error")
    return flask.redirect(flask.url_for("settings", userId=userId))

# -------------------------------------
#
# Functionality to allow user to review items
#
# ------------------------------------------

@app.route("/review/<userId>/<itemId>", methods=["GET", "POST"])
def reviewItem(userId, itemId):
    PageLog('review')
    """Add a Review"""
    
    #Handle input
    if flask.request.method == "POST":
        reviewStars = flask.request.form.get("rating")
        reviewStars=clean(reviewStars)
        reviewComment = flask.request.form.get("review")

        #Clean up review whitespace
        #https://www.w3schools.com/python/trypython.asp?filename=demo_ref_string_strip test shows still execpts '' so sql vunrable
        reviewComment = reviewComment.strip()
        data=string.ascii_lowercase
        data3=[]
        for char in data:
            data3.append(char)
        print(data)
        data2=[]
        for char in data:
            data2.append(char.upper())
        data=data3+data2+["@",".","_"," ","1","2","3","4","5","6","7","8","0","9"]
        for char in reviewComment:
            if char in data:
                usless=0
            else:
                reviewComment=""
        reviewId = flask.request.form.get("reviewId")
        #info could be used for injection 
        app.logger.info("Review Made %s", reviewId)
        app.logger.info("Rating %s  Text %s", reviewStars, reviewComment)

        if reviewId:
            #if vunrablity from above is used could be changed on a whim
            #Update an existing oe
            #bellow form is sql vunrable
            app.logger.info("Update Existing")

            theSQL = f"""
            UPDATE review
            SET stars = {reviewStars},
                review = '{reviewComment}'
            WHERE
                id = {reviewId}"""

            app.logger.debug("%s", theSQL)
            write_db(theSQL)

            flask.flash("Review Updated")
            
        else:
            app.logger.info("New Review")

            theSQL = f"""
            INSERT INTO review (userId, productId, stars, review)
            VALUES ({userId}, {itemId}, {reviewStars}, '{reviewComment}');
            """

            app.logger.info("%s", theSQL)
            write_db(theSQL)

            flask.flash("Review Made")

    #Otherwise get the review
    #vunrable
    theQry = f"SELECT * FROM product WHERE id = {itemId};"
    item = query_db(theQry, one=True)
    
    theQry = f"SELECT * FROM review WHERE userID = {userId} AND productID = {itemId};"
    review = query_db(theQry, one=True)
    app.logger.debug("Review Exists %s", review)
    cookie = request.cookies.get('session2')
    print("COOKIE BELOW ON REVIEW")
    print(cookie)
    Qry2 = "Select * FROM roles WHERE userID= {0}".format(cookie[13])
    role = query_db(Qry2, one=True)
    role=role['userRole']
    if len(cookie)>14:
        if cookie[13]==userId:
            print("welp the problem is here")
            return flask.render_template("reviewItem.html",item = item,review = review,)
        
        elif role=="admin":
            return flask.render_template("reviewItem.html",item = item,review = review,)
        else:
            return redirect("https://habitatcrater-geniusgenesis-5000.codio-box.uk/logout", code=302)
    else:
        return redirect("https://habitatcrater-geniusgenesis-5000.codio-box.uk/logout", code=302)
                        
    #return redirect("https://habitatcrater-geniusgenesis-5000.codio-box.uk/user/login", code=302)
    """return flask.render_template("reviewItem.html",
                                 item = item,
                                 review = review,
                                 )"""

# ---------------------------------------
#
# BASKET AND PAYMEN
#
# ------------------------------------------



@app.route("/basket", methods=["GET","POST"])
def basket():
    PageLog('Basket')
    #Check for user
    if not flask.session["user"]:
        flask.flash("You need to be logged in")
        return flask.redirect(flask.url_for("index"))


    theBasket = []
    #Otherwise we need to work out the Basket
    #Get it from the session
    sessionBasket = flask.session.get("basket", None)
    if not sessionBasket:
        flask.flash("No items in basket")
        return flask.redirect(flask.url_for("index"))

    totalPrice = 0
    for key in sessionBasket:
        #vunrable
        theQry = f"SELECT * FROM product WHERE id = {key}"
        theItem =  query_db(theQry, one=True)
        quantity = int(sessionBasket[key])
        thePrice = theItem["price"] * quantity
        totalPrice += thePrice
        theBasket.append([theItem, quantity, thePrice])
    
        
    return flask.render_template("basket.html",
                                 basket = theBasket,
                                 total=totalPrice)

@app.route("/basket/payment", methods=["GET", "POST"])
def pay():
    PageLog('Payment')
    """
    Fake paymeent.

    YOU DO NOT NEED TO IMPLEMENT PAYMENT
    """
    
    if not flask.session["user"]:
        flask.flash("You need to be logged in")
        return flask.redirect(flask.url_for("index"))

    #Get the total cost
    cost = flask.request.form.get("total")
    


    
    #Fetch USer ID from Sssion
    #sql vunrable
    theQry = "Select * FROM User WHERE id = {0}".format(flask.session["user"])
    theUser = query_db(theQry, one=True)

    #Add products to the user
    sessionBasket = flask.session.get("basket", None)

    theDate = datetime.datetime.utcnow()
    for key in sessionBasket:

#vunrable to sql
        #As we should have a trustworthy key in the basket.
        theQry = "INSERT INTO PURCHASE (userID, productID, date) VALUES ({0},{1},'{2}')".format(theUser['id'],
                                                                                              key,
                                                                                              theDate)
                                                                                              
        app.logger.debug(theQry)
        write_db(theQry)

    #Clear the Session
    flask.session.pop("basket", None)
    
    return flask.render_template("pay.html",
                                 total=cost)



# ---------------------------
# HELPER FUNCTIONS
# ---------------------------


@app.route('/uploads/<name>')
def serve_image(name):
   
    """
    Helper function to serve an uploaded image
    """
    return flask.send_from_directory(app.config["UPLOAD_FOLDER"], name)


@app.route("/initdb")
def database_helper():
    """
    Helper / Debug Function to create the initial database

    You are free to ignore scurity implications of this
    """
    
    init_db()
    return "Done"

@app.route("/admin", methods=["GET","POST"])
def admin():
    PageLog('Admin')
    #Check for user
    if not flask.session["user"]:
        flask.flash("You need to be logged in")
        return flask.redirect(flask.url_for("index"))


    
    theQry = "Select * FROM User;"
    Users = query_db(theQry)
    users=[]
    for user in Users:
        tem=[]
        tem.append(user['id'])
        tem.append(user['email'])
        Qry2 = "Select * FROM roles WHERE userID= {0}".format(user['id'])
        role = query_db(Qry2, one=True)
        role=role['userRole']
        tem.append(role)
        users.append(tem)
    print(Users)
    cookie = request.cookies.get('session2')
    print("COOKIE BELOW ON REVIEW")
    print(cookie)
    if len(cookie)>14:
        Qry="Select * FROM roles WHERE userID= {0}".format(cookie[13])
        role = query_db(Qry, one=True)
        role=role['userRole']
        if role=='admin':
            print("welp the problem is here")
            return flask.render_template("admin.html",users=users)
        else:
            return redirect("https://habitatcrater-geniusgenesis-5000.codio-box.uk/logout", code=302)
    else:
        return redirect("https://habitatcrater-geniusgenesis-5000.codio-box.uk/logout", code=302)
             
  

@app.route("/admin/create", methods=["GET","POST"])
def Admincreate():
    PageLog('Admin Create')
    """ Create a new account,
    we will redirect to a homepage here
    """
    cookie = request.cookies.get('session2')
    print("COOKIE BELOW ON REVIEW")
    print(cookie)
    if len(cookie)>14:
        Qry="Select * FROM roles WHERE userID= {0}".format(cookie[13])
        role = query_db(Qry, one=True)
        role=role['userRole']
        if role=='admin':
            print("this guy is an admin")
        else:
            return redirect("https://habitatcrater-geniusgenesis-5000.codio-box.uk/logout", code=302)
    else:
        return redirect("https://habitatcrater-geniusgenesis-5000.codio-box.uk/logout", code=302)
    if flask.request.method == "GET":
        return flask.render_template("create_item.html")
    
    #Get the form data
    name = flask.request.form.get("name")
    description = flask.request.form.get("description")
    price = flask.request.form.get("price")
    image = flask.request.form.get("image")
    #Sanity check do we have a name, email and password

    #Otherwise we can add the user
    #query bellow is vunrable to sql injection fix is to remove quote marks from string in all their forms 
    
   
    if False:
        flask.flash("A User with that Email Exists")
        return flask.render_template("create_account.html",
                                     name = name,
                                     email = email)

    else:
        #Crate the user
        #might be vunrable im not sure
        
    
        UPLOAD_FOLDER = '/uploads'
        theQry = f"INSERT INTO product (id, name, description,price,image) VALUES (NULL, '{name}', '{description}',{price},'{image}')"
       
        #filename = request.files['file']
        #filename = secure_filename(file.filename)
        #file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        userQry = write_db(theQry)
        
        flask.flash("Account Created, you can now Login")
        return flask.redirect(flask.url_for("login"))
    
@app.route("/admin/update", methods=["GET","POST"])
def Adminupdate():
    PageLog('Admin Update')
    
    cookie = request.cookies.get('session2')
    print("COOKIE BELOW ON REVIEW")
    print(cookie)
    if len(cookie)>14:
        Qry="Select * FROM roles WHERE userID= {0}".format(cookie[13])
        role = query_db(Qry, one=True)
        role=role['userRole']
        if role=='admin':
            print("this guy is an admin")
        else:
            return redirect("https://habitatcrater-geniusgenesis-5000.codio-box.uk/logout", code=302)
    else:
        return redirect("https://habitatcrater-geniusgenesis-5000.codio-box.uk/logout", code=302)
    if flask.request.method == "GET":
        return flask.render_template("update_user.html")
    
    #Get the form data
    Userid = flask.request.form.get("id")
    role = flask.request.form.get("role")
    #Sanity check do we have a name, email and password

    #Otherwise we can add the user
    #query bellow is vunrable to sql injection fix is to remove quote marks from string in all their forms 
    
   
    if False:
        flask.flash("A User with that Email Exists")
        return flask.render_template("create_account.html",
                                     name = name,
                                     email = email)

    else:
        #Crate the user
        #might be vunrable im not sure
        

        theQry = f"UPDATE roles SET userRole = '{role}' WHERE userID = {Userid}"

        userQry = write_db(theQry)
        
        flask.flash("Account Created, you can now Login")
        return flask.redirect(flask.url_for("login"))
    