import os
from flask import Flask,send_file
from flask import redirect
from flask import render_template
from flask import request, jsonify
from flask_sqlalchemy import SQLAlchemy
import random
from datetime import date as dt
import json
from flask_cors import CORS
from celery import Celery
from celery.schedules import crontab     
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import plotly.express as px
from collections import defaultdict
import pdfkit
from email.mime.base import MIMEBase
from email import encoders
import csv

SMPTP_SERVER_HOST="localhost"
SMPTP_SERVER_PORT=1025
SENDER_ADDRESS="email@test.com"
SENDER_PASSWORD=""

current_dir = os.path.abspath(os.path.dirname(__file__))

def send_email(to_address,subject,message):
    msg=MIMEMultipart()
    msg["From"]=SENDER_ADDRESS
    msg["To"]=to_address
    msg["Subject"]=subject

    msg.attach(MIMEText(message,"html"))
    s=smtplib.SMTP(host=SMPTP_SERVER_HOST,port=SMPTP_SERVER_PORT)
    s.login(SENDER_ADDRESS,SENDER_PASSWORD)
    s.send_message(msg)

def send_email_attach(to_address,subject,message):
    global current_dir
    msg=MIMEMultipart()
    msg["From"]=SENDER_ADDRESS
    msg["To"]=to_address
    msg["Subject"]=subject
    pdfkit.from_string(message, 'templates/reports/output3.pdf')  

    msg.attach(MIMEText("The details are in the pdf attached below.","html"))
    attach_file_name = str(current_dir)+'/templates/reports/output3.pdf'
    attach_file = open(attach_file_name, 'rb')
    payload = MIMEBase('application', 'octate-stream')
    payload.set_payload((attach_file).read())
    encoders.encode_base64(payload) 

    payload.add_header('Content-Decomposition', 'attachment', filename=attach_file_name)
    msg.attach(payload)

    s=smtplib.SMTP(host=SMPTP_SERVER_HOST,port=SMPTP_SERVER_PORT)
    s.login(SENDER_ADDRESS,SENDER_PASSWORD)
    text=msg.as_string()
    s.sendmail(SENDER_ADDRESS,to_address,text)


send_email_attach("yo@gmail.com","hello","wassup")



app = Flask(__name__)

app.config["CELERY_BROKER_URL"] = "redis://localhost:6379"
celery = Celery(app.name, broker=app.config["CELERY_BROKER_URL"])
celery.conf.update(app.config)
celery.conf.enable_utc = False
celery.conf.timezone = "Asia/Calcutta"
celery.conf.beat_schedule={
    'add-every-monday-morning': {
        'task': 'tasks.add',
        'schedule': crontab(minute='00', hour='17', day_of_week='*', day_of_month='*', month_of_year='*'),
    },
    'add-every-month-morning': {
        'task': 'tasks.month',
        'schedule': crontab(minute='00', hour='00', day_of_month='01', month_of_year='*'),
    },
    'removing-unwanted-files-morning': {
        'task': 'tasks.remove',
        'schedule': crontab(minute='*', hour='*', day_of_month='*', month_of_year='*'),
    }
}
CORS(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(current_dir, "testdb.sqlite3")
db = SQLAlchemy()
db.init_app(app)
app.app_context().push()

usersid = random.randint(2, 10000)
listsid = random.randint(2, 10000)
cardsid = random.randint(2, 10000)


class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    username = db.Column(db.String, unique=True, nullable=False)
    rep_type=db.Column(db.Integer, default=1)


class Auth(db.Model):
    __tablename__ = 'auth'
    email = db.Column(db.String, primary_key=True)
    auth = db.Column(db.Integer)


class Lists(db.Model):
    __tablename__ = 'lists'
    userid = db.Column(db.Integer, nullable=False)
    listname = db.Column(db.String, nullable=False)
    # cardid = db.Column(db.Integer,nullable=False)
    listid = db.Column(db.Integer, primary_key=True, nullable=False)
    list_view = db.Column(db.Integer, default=1)


class Cards(db.Model):
    __tablename__ = 'cards'
    card_id = db.Column(db.Integer, nullable=False, primary_key=True)
    card_name = db.Column(db.String, nullable=False)
    card_txt = db.Column(db.String, nullable=False)
    card_date = db.Column(db.String, nullable=False)
    card_status = db.Column(db.Integer, nullable=False)
    listid = db.Column(db.Integer, nullable=False)
    userid = db.Column(db.Integer, nullable=False)
    card_fin = db.Column(db.String)
    card_upd = db.Column(db.String)
    card_exp = db.Column(db.String)
    card_view = db.Column(db.Integer, default=1)

def prep_report(userid):
    fin_msg=""
    msg1="Total Tasks created Last month: "
    msg2="Total no tasks completed Last Month: "
    msg3="Total no of tasks that crossed deadline last month: "
    msg4="Upcoming Tasks: "
    card=Cards.query.filter_by(userid=userid)
    today=dt.today()
    month=today.month
    year=today.year
    if month==0:
        month=12
        year=year-1
    ttc=ttco=ttd=0
    l=[]
    task_fin_dat = defaultdict(lambda : 0)
    months = { "1" : 31 , "2" : 28 , "3" : 31 , "4" : 30 , "5" : 31 , "6" : 30 , "7" : 31 , "8" : 31 , "9" : 30 , "10" : 31 , "11" : 30 , "12" : 31}
    for i in card:
        
        temp=i.card_date
        temp2=i.card_exp
        cdate=dt(int(temp[0:4]),int(temp[5:7]),int(temp[8:10]))
        cexp=dt(int(temp2[0:4]),int(temp2[5:7]),int(temp2[8:10]))
        if cdate>dt(year,month,1):
            ttc+=1
            if i.card_status==1:
                ttco+=1
                task_fin_dat[i.card_fin]+=1
            if today>cexp:
                ttd+=1
            if today<=cexp:
                if i.card_view==1 and i.card_status==0:
                    l.append([i.card_name,i.card_exp])
    fin_msg+="<div>"
    fin_msg+=msg1+str(ttc)+"<br>"
    fin_msg+=msg2+str(ttco)+"<br>"
    fin_msg+=msg3+str(ttd)+"<br>"
    fin_msg+=msg4+"<br>"
    if len(l)==0:
        fin_msg+="None"
    else:
        fin_msg+="<table><tr><th>Task Name</th><th>Deadline</th></tr>"
        for i in l:
            fin_msg+="<tr><td style=\"border: solid 2px lightgrey;\">"+i[0]+"</td><td style=\"border: solid 2px lightgrey;\">"+i[1]+"</td></tr>"
    dtlist=[]
    fin_msg+="</table></div>"
    tsklist=[]
    for i in range(1,months[str(month)]+1):
        if month!=11 and month!=12 and month!=10:
            dat=str(year)+"-0"+str(month)+"-"+str(i)
            dtlist.append(dat)
            if task_fin_dat[dat]!=0:
                tsklist.append(task_fin_dat[dat])
            else:
                tsklist.append(0)
        else:
            dat=str(year)+"-"+str(month)+"-"+str(i)
            dtlist.append(dat)
            if task_fin_dat[dat]!=0:
                tsklist.append(task_fin_dat[dat])
            else:
                tsklist.append(0)


    df = {"Date":dtlist,"No. of tasks completed":tsklist}
    fig = px.line(df, x='Date', y="No. of tasks completed")
    htm="templates/reports/"+str(userid)+".html"
    fig.write_html(htm)
    f = open(htm, "r")
    txt=f.readlines()
    fin_lis=txt[3:-2]
    os.remove(os.path.join(current_dir,htm))
    for i in fin_lis:
        fin_msg+=i
    return fin_msg

def prep_report_sum(userid):
    fin_msg=""
    msg0="Total Lists created Last month:"
    msg1="Total Tasks created Last month: "
    msg2="Total no tasks completed Last Month: "
    msg3="Total no of tasks that crossed deadline last month: "
    msg4="Upcoming Tasks: "
    card=Cards.query.filter_by(userid=userid)
    today=dt.today()
    month=today.month
    year=today.year
    if month==0:
        month=12
        year=year-1
    ttc=ttco=ttd=0
    l=[]
    listd=[]
    task_fin_dat = defaultdict(lambda : 0)
    months = { "1" : 31 , "2" : 28 , "3" : 31 , "4" : 30 , "5" : 31 , "6" : 30 , "7" : 31 , "8" : 31 , "9" : 30 , "10" : 31 , "11" : 30 , "12" : 31}
    for i in card:
        
        temp=i.card_date
        temp2=i.card_exp
        cdate=dt(int(temp[0:4]),int(temp[5:7]),int(temp[8:10]))
        cexp=dt(int(temp2[0:4]),int(temp2[5:7]),int(temp2[8:10]))
        if cdate>dt(year,month,1):
            if i.listid not in listd:
                listd.append(i.listid)
            ttc+=1
            if i.card_status==1:
                ttco+=1
                task_fin_dat[i.card_fin]+=1
            if today>cexp:
                ttd+=1
            if today<=cexp:
                if i.card_view==1 and i.card_status==0:
                    l.append([i.card_name,i.card_exp])
    fin_msg+="<div>"
    fin_msg+=msg0+str(len(listd))+"<br>"
    fin_msg+=msg1+str(ttc)+"<br>"
    fin_msg+=msg2+str(ttco)+"<br>"
    fin_msg+=msg3+str(ttd)+"<br>"
    fin_msg+=msg4+"<br>"
    if len(l)==0:
        fin_msg+="None"
    else:
        fin_msg+="<table><tr><th>Task Name</th><th>Deadline</th></tr>"
        for i in l:
            fin_msg+="<tr><td style=\"border: solid 2px lightgrey;\">"+i[0]+"</td><td style=\"border: solid 2px lightgrey;\">"+i[1]+"</td></tr>"
    dtlist=[]
    fin_msg+="</table></div>"
    tsklist=[]
    for i in range(1,months[str(month)]+1):
        if month!=11 and month!=12 and month!=10:
            dat=str(year)+"-0"+str(month)+"-"+str(i)
            dtlist.append(dat)
            if task_fin_dat[dat]!=0:
                tsklist.append(task_fin_dat[dat])
            else:
                tsklist.append(0)
        else:
            dat=str(year)+"-"+str(month)+"-"+str(i)
            dtlist.append(dat)
            if task_fin_dat[dat]!=0:
                tsklist.append(task_fin_dat[dat])
            else:
                tsklist.append(0)
    return [fin_msg,dtlist,tsklist]

def prep_report_list(userid,listid):
    fin_msg=""
    
    msg1="Total Tasks created Last month: "
    msg2="Total no tasks completed Last Month: "
    msg3="Total no of tasks that crossed deadline last month: "
    msg4="Upcoming Tasks: "
    card=Cards.query.filter_by(userid=userid,listid=listid)
    today=dt.today()
    month=today.month
    year=today.year
    if month==0:
        month=12
        year=year-1
    ttc=ttco=ttd=0
    l=[]
    task_fin_dat = defaultdict(lambda : 0)
    months = { "1" : 31 , "2" : 28 , "3" : 31 , "4" : 30 , "5" : 31 , "6" : 30 , "7" : 31 , "8" : 31 , "9" : 30 , "10" : 31 , "11" : 30 , "12" : 31}
    for i in card:
        
        temp=i.card_date
        temp2=i.card_exp
        cdate=dt(int(temp[0:4]),int(temp[5:7]),int(temp[8:10]))
        cexp=dt(int(temp2[0:4]),int(temp2[5:7]),int(temp2[8:10]))
        if cdate>dt(year,month,1):
            ttc+=1
            if i.card_status==1:
                ttco+=1
                task_fin_dat[i.card_fin]+=1
            if today>cexp:
                ttd+=1
            if today<=cexp:
                if i.card_view==1 and i.card_status==0:
                    l.append([i.card_name,i.card_exp])
    fin_msg+="<div>"
    fin_msg+=msg1+str(ttc)+"<br>"
    fin_msg+=msg2+str(ttco)+"<br>"
    fin_msg+=msg3+str(ttd)+"<br>"
    fin_msg+=msg4+"<br>"
    if len(l)==0:
        fin_msg+="None"
    else:
        fin_msg+="<table><tr><th>Task Name</th><th>Deadline</th></tr>"
        for i in l:
            fin_msg+="<tr><td style=\"border: solid 2px lightgrey;\">"+i[0]+"</td><td style=\"border: solid 2px lightgrey;\">"+i[1]+"</td></tr>"
    dtlist=[]
    fin_msg+="</table></div>"
    tsklist=[]
    for i in range(1,months[str(month)]+1):
        if month!=11 and month!=12 and month!=10:
            dat=str(year)+"-0"+str(month)+"-"+str(i)
            dtlist.append(dat)
            if task_fin_dat[dat]!=0:
                tsklist.append(task_fin_dat[dat])
            else:
                tsklist.append(0)
        else:
            dat=str(year)+"-"+str(month)+"-"+str(i)
            dtlist.append(dat)
            if task_fin_dat[dat]!=0:
                tsklist.append(task_fin_dat[dat])
            else:
                tsklist.append(0)
    return [fin_msg,dtlist,tsklist]
@celery.task(name='tasks.add')
def add():
    use=Users.query.all()
    for i in use:
        car=Cards.query.filter_by(userid=i.id)
        
        msg="CARDS PENDING: "
        msg2="CARDS EXPIRING TODAY: "
        msg3="CARDS PENDING: "
        msg4="CARDS EXPIRING TODAY: "
        for j in car:
            if j.card_status==0:
                msg+="["+j.card_name+":"+j.card_txt+"] "
                if j.card_exp==dt.today():
                    msg2+="["+j.card_name+":"+j.card_txt+"] "
        if msg!=msg3:
            if msg2!=msg4:
                fin_msg=msg+"<br>"+msg2
                
            else:
                fin_msg=msg+"<br>"+"You dont have any tasks expiring today."
            fin_msg+="<br><br><br>"+"To mark as completed, go to <a href=\"http://localhost:5173/\">this</a>."
            send_email(i.email,"Your Pending Taks",fin_msg)

    return True

@celery.task(name='tasks.month')
def month():
    use=Users.query.all()
    for i in use:
        if i.rep_type==1:
            send_email(i.email,"Your Monthly Report",prep_report(i.id))
        else:
            send_email_attach(i.email,"Your Monthly Report",prep_report(i.id))


    return True

@celery.task(name='tasks.remove')
def remove():
    use=Users.query.all()
    for i in use:
        htm="templates/reports/"+str(i.username)+".csv"
        htm2="templates/reports/"+str(i.username)+"_list.csv"
        filename=os.path.join(current_dir,htm)
        filename2=os.path.join(current_dir,htm2)
        f=open(filename,"w+",newline='')
        f.close()
        os.remove(filename)
        f=open(filename2,"w+",newline='')
        f.close()
        os.remove(filename2)
    return True

@app.route('/')
def add_task():
    for i in range(10000):
        add.delay(i, i)
    return jsonify({'status': 'ok'})

@app.route('/report/<userid>')
def gen_report(userid):
    htm=str(userid)+".html"
    return render_template("reports/"+htm)

@app.route("/login/<uname>/<passw>", methods=["Get"])
def userlogin(uname, passw):
    if request.method == "GET":
        user1 = Users.query.filter_by(username=uname).first()
        if user1 == None:
            return jsonify(auth="False", user="False")
        elif user1.password == passw:
            user2 = Auth.query.filter_by(email=user1.username).first()
            user2.auth = 1
            db.session.commit()
            return jsonify(auth="True", user="True")
        else:
            return jsonify(auth="False", user="True")


@app.route("/getauth/<id0>", methods=["Get"])
def getauth(id0):
    if request.method == "GET":
        user2 = Auth.query.filter_by(email=id0).first()
        if user2.auth == 1:
            return jsonify(auth="True")
        else:
            return jsonify(auth="False")

@app.route("/getuserdata/<id0>", methods=["Get"])
def getusedata(id0):
    if request.method == "GET":
        user1 = Users.query.filter_by(username=id0).first()
        d={}
        d['name']=user1.name
        d['email']=user1.email
        d["passwd"]=user1.password
        d["rep_type"]=user1.rep_type
        print(d)
        return jsonify(d)

@app.route("/getsumdata/<id0>", methods=["Get"])
def getsumdata(id0):
    if request.method == "GET":
        user1 = Users.query.filter_by(username=id0).first()
        list=Lists.query.filter_by(userid=user1.id)
        d={}
        e={}
        start=2
        for i in (list):
            d[i.listname]=prep_report_list(user1.id,i.listid)
            d[i.listname].append(start)
            start+=1
        e["Complete Summary"]=prep_report_sum(user1.id)
        e["Complete Summary"].append(1)
        f=[e,d,start-1,e["Complete Summary"][1],e["Complete Summary"][2]]
        return jsonify(f)


@app.route("/changedata/<id0>/<name>/<email>/<password>/<rep_type>", methods=["Get"])
def changeusedata(id0,name,email,password,rep_type):
    if request.method == "GET":
        user1 = Users.query.filter_by(username=id0).first()
        user= Users.query.all()
        for i in user:
            print(i.username,name,id0)
            if i.username==name and name!=id0:
                return jsonify(commit="False")
        user1.name=name
        user1.email=email
        user1.password=password
        user1.rep_type=int(rep_type)
        db.session.add(user1)
        db.session.commit()
        return jsonify(commit="True")


@app.route("/getlist/<id0>", methods=["Get"])
def getlist(id0):
    if request.method == "GET":
        user1 = Users.query.filter_by(username=id0).first()
        list = Lists.query.filter_by(userid=user1.id,list_view=1).all()
        d = {}
        c = []
        for i in list:
            d[i.listname] = []
            c.append(i.listname)
        for i in list:
            cards = Cards.query.filter_by(listid=i.listid,card_view=1).all()
            for j in cards:
                if j.card_exp<str(dt.today()):
                    strat=3
                else:
                    strat=j.card_status
                d[i.listname].append([j.card_name, j.card_txt, j.card_exp, strat])
                g = [j.card_name, j.card_txt, j.card_date, j.card_status, j.listid]
                print(g)
        # d['userlist']=c
        return jsonify(d)


@app.route("/createlist/<id0>/<lisname>", methods=["Get"])
def createlist(id0, lisname):
    if request.method == "GET":
        global listsid
        user1 = Users.query.filter_by(username=id0).first()
        list1 = Lists(userid=user1.id, listname=lisname, listid=listsid)
        listsid += 1
        db.session.add(list1)
        db.session.commit()
        return jsonify(commit='True')


@app.route("/addcard/<id0>/<lisname>/<summary>/<date>/<lname>", methods=["Get"])
def addcard(id0, lisname, summary, date, lname):
    if request.method == "GET":
        global cardsid
        user1 = Users.query.filter_by(username=id0).first()
        today = dt.today()
        list = Lists.query.filter_by(listname=lname, userid=user1.id).first()
        list1 = Cards(card_id=cardsid, card_name=lisname, card_txt=summary, card_date=today, card_status=0,
                      listid=list.listid, userid=user1.id,card_exp=date)
        cardsid += 1
        db.session.add(list1)
        db.session.commit()
        return jsonify(commit='True')


@app.route("/editlist/<id0>/<lisname>/<flname>", methods=["Get"])
def editlist(id0, lisname, flname):
    if request.method == "GET":
        global listsid
        user1 = Users.query.filter_by(username=id0).first()
        list = Lists.query.filter_by(userid=user1.id, listname=lisname).first()
        list.listname = flname
        listsid += 1
        db.session.add(list)
        db.session.commit()
        return jsonify(commit='True')


@app.route("/deletelist/<id0>/<lisname>", methods=["Get"])
def deletelist(id0, lisname):
    if request.method == "GET":
        global listsid
        user1 = Users.query.filter_by(username=id0).first()
        list = Lists.query.filter_by(userid=user1.id, listname=lisname).first()
        list.list_view=0
        db.session.add(list)
        card = Cards.query.filter_by(listid=list.listid).all()
        for i in card:
            i.card_view=0
            db.session.add(i)
        db.session.commit()
        return jsonify(commit='True')


@app.route("/editcard/<id0>/<lisname>/<summary>/<date>/<lname>/<cname>", methods=["Get"])
def editcard(id0, lisname, summary, date, lname, cname):
    if request.method == "GET":
        global cardsid
        global usersid
        user1 = Users.query.filter_by(username=id0).first()
        list = Lists.query.filter_by(listname=lisname, userid=user1.id).first()
        card = Cards.query.filter_by(listid=list.listid, card_name=cname, userid=user1.id).first()
        card.card_name = lname
        card.card_txt = summary
        card.card_exp = date
        card.card_upd=dt.today()
        db.session.add(card)
        db.session.commit()
        return jsonify(commit='True')


@app.route("/deletecard/<id0>/<lisname>/<cname>", methods=["Get"])
def deletecard(id0, lisname, cname):
    if request.method == "GET":
        global cardsid
        user1 = Users.query.filter_by(username=id0).first()
        list = Lists.query.filter_by(listname=lisname, userid=user1.id).first()
        card = Cards.query.filter_by(listid=list.listid, card_name=cname, userid=user1.id).first()
        card.card_view=0
        db.session.add(card)
        db.session.commit()
        return jsonify(commit='True')


@app.route("/stat1card/<id0>/<lisname>/<cname>", methods=["Get"])
def stat1card(id0, lisname, cname):
    if request.method == "GET":
        user1 = Users.query.filter_by(username=id0).first()
        global cardsid
        list = Lists.query.filter_by(listname=lisname, userid=user1.id).first()
        card = Cards.query.filter_by(listid=list.listid, card_name=cname, userid=user1.id).first()
        card.card_status = 1
        card.card_fin=dt.today()
        db.session.add(card)
        db.session.commit()
        return jsonify(commit='True')


@app.route("/stat0card/<id0>/<lisname>/<cname>", methods=["Get"])
def stat0card(id0, lisname, cname):
    if request.method == "GET":
        user1 = Users.query.filter_by(username=id0).first()
        global cardsid
        list = Lists.query.filter_by(listname=lisname, userid=user1.id).first()
        card = Cards.query.filter_by(listid=list.listid, card_name=cname, userid=user1.id).first()
        card.card_status = 0
        card.card_fin=None
        db.session.add(card)
        db.session.commit()
        return jsonify(commit='True')


@app.route("/movecard/<id0>/<lisname>/<lis2name>/<cname>", methods=["Get"])
def movecard(id0, lisname, lis2name, cname):
    if request.method == "GET":
        global cardsid
        user1 = Users.query.filter_by(username=id0).first()
        list = Lists.query.filter_by(listname=lisname, userid=user1.id).first()
        list2 = Lists.query.filter_by(listname=lis2name, userid=user1.id).first()
        card = Cards.query.filter_by(listid=list.listid, card_name=cname, userid=user1.id).first()
        print(card)
        card.listid = list2.listid
        db.session.add(card)
        db.session.commit()
        return jsonify(commit='True')


@app.route("/logout/<id0>", methods=["Get"])
def logout(id0):
    if request.method == "GET":
        global cardsid
        user1 = Users.query.filter_by(username=id0).first()
        auth = Auth.query.filter_by(email=user1.username).first()
        auth.auth = 0
        db.session.add(auth)
        db.session.commit()
        return jsonify(commit='True')


@app.route("/newuser/<email>/<pwd>/<uname>", methods=["Get"])
def newuser(email, pwd, uname):
    if request.method == "GET":
        global cardsid
        global usersid
        user= Users.query.all()
        for i in user:
            if i.username==uname:
                return jsonify(commit="False")
        user1 = Users(id=usersid, name=uname, email=email, password=pwd, username=uname)
        auth = Auth(email=uname, auth=1)
        usersid += 1
        db.session.add(user1)
        db.session.add(auth)
        db.session.commit()
        return jsonify(commit='True')


@app.route("/getlists/<id0>", methods=["Get"])
def getlists(id0):
    if request.method == "GET":
        user1 = Users.query.filter_by(username=id0).first()
        list=Lists.query.filter_by(userid=user1.id).all()
        d={}
        for i in list:
            if i.list_view==1:
                d[i.listid]=i.listname
        card=Cards.query.filter_by(userid=user1.id,card_view=1).all()
        lidt=[]
        for i in card:
            e={}
            e["Listname"]=d[i.listid]
            e["Card_Name"]=i.card_name
            e["Card_Description"]=i.card_txt
            e["Card_Created"]=i.card_date
            e["Card_Expiry"]=i.card_exp
            e["Card_Updated"]=i.card_upd if i.card_upd!=None else "None"
            e["Card_Status"]="Completed" if i.card_status==1 else "Pending"
            e["Card_Completed_Date"]=i.card_fin if i.card_fin!=None else "None"
            lidt.append(e)
        fields = ['Listname', 'Card_Name', 'Card_Description','Card_Created', 'Card_Expiry', 'Card_Updated','Card_Status', 'Card_Completed_Date'] 
        filename="templates/reports/"
        filename+=user1.username+".csv"
        with open(filename, 'w+', newline='') as file: 
            writer = csv.DictWriter(file, fieldnames = fields)

            writer.writeheader() 

            writer.writerows(lidt)


        return send_file(filename,as_attachment=True)

@app.route("/getlis/<id0>/<lisname>", methods=["Get"])
def getlis(id0,lisname):
    if request.method == "GET":
        user1 = Users.query.filter_by(username=id0).first()
        list=Lists.query.filter_by(userid=user1.id,listname=lisname).first()
        d={}
        card=Cards.query.filter_by(userid=user1.id,card_view=1,listid=list.listid).all()
        lidt=[]
        for i in card:
            e={}
            e["Listname"]=list.listname
            e["Card_Name"]=i.card_name
            e["Card_Description"]=i.card_txt
            e["Card_Created"]=i.card_date
            e["Card_Expiry"]=i.card_exp
            e["Card_Updated"]=i.card_upd if i.card_upd!=None else "None"
            e["Card_Status"]="Completed" if i.card_status==1 else "Pending"
            e["Card_Completed_Date"]=i.card_fin if i.card_fin!=None else "None"
            lidt.append(e)
        fields = ['Listname', 'Card_Name', 'Card_Description','Card_Created', 'Card_Expiry', 'Card_Updated','Card_Status', 'Card_Completed_Date'] 
        filename="templates/reports/"
        filename+=user1.username+"_list"+".csv"
        with open(filename, 'w+', newline='') as file: 
            writer = csv.DictWriter(file, fieldnames = fields)

            writer.writeheader() 

            writer.writerows(lidt)


        return send_file(filename,as_attachment=True)

if __name__ == "__main__":
    app.run(
        host='0.0.0.0',
        debug=True,
        port=8080)
    celery.start()
