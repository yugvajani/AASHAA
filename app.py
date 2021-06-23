from flask import Flask, request, render_template, session
from flask.helpers import url_for
import pymongo
from pymongo import MongoClient
from datetime import timedelta
import notification
import pandas as pd
import json
import plotly
import pymongo
from pymongo import MongoClient
import plotly.express as px
from collections import defaultdict
from bson.objectid import ObjectId
from werkzeug.utils import redirect

cluster= MongoClient("mongodb+srv://cfgteam74:cfgteam74@cluster0.5pow9.mongodb.net/flaskwebsite?retryWrites=true&w=majority")
client=pymongo.MongoClient("mongodb+srv://cfgteam74:cfgteam74@cluster0.5pow9.mongodb.net/flaskwebsite?retryWrites=true&w=majority")
Database = client.get_database('vaccination')
vaccination=Database.vacc_done

db=cluster["flaskwebsite"]
col=db['users']
ashausers=db['ashaWorkers']
forum = db['forum']
lat_lot = db['lat_lot']

# mongodb+srv://cfgteam74:<password>@cluster0.5pow9.mongodb.net/myFirstDatabase?retryWrites=true&w=majority
app = Flask(__name__)
app.secret_key="hello"
app.permanent_session_lifetime = timedelta(days=31)

# @app.route("/")
# def loginpage():
    
#     return render_template('login.html')


@app.route("/")
def home():
    lat = request.args.get('lat')
    lot = request.args.get('lot')
    date = request.args.get('date')
    lat_lot.insert_one({"lat":lat , "lot":lot,"date":date})
    if date is None:
        return render_template('home.html')
    else:
        return render_template('home.html' , invisible = True)

@app.route("/form")
def form():
    return render_template('form.html')

@app.route("/allAsha")
def allAsha():
    lis=[i for i in ashausers.find()]
    print(lis)

    return render_template('ashaUsers.html',ashaworkers=lis)

@app.route("/children")
def children():
    lis=[i for i in col.find()]
    print(lis)

    return render_template('children.html',children=lis)


@app.route("/addAsha")
def addAsha():
    return render_template('addAshaUsers.html')

@app.route("/addAshaWorker", methods=['POST'])
def addAshaWorker():
    name=request.form['name']
    email=request.form['email']
    ph=request.form['ph']
    city=request.form['city']
    pincode=request.form['pincode']
    userid=request.form['userid']
    password=request.form['password']
    ashausers.insert_one({'name':name,'email':email,'ph':ph,'city':city,'pincode':pincode,'userid':userid,'password':password})
    # return render_template('login.html')
    return render_template('adminhome.html')

@app.route("/admin")
def admin():
    return render_template('adminhome1.html')

@app.route("/register")
def register():
    return render_template('register.html')

@app.route("/signup", methods=['POST'])
def signup():
    pname=request.form['pname']
    # cname=request.form['cname']
    # dob=request.form['dob']
    email=request.form['email']
    ph=request.form['ph']
    # loc=request.form['location']
    # userid=request.form['userid']
    password=request.form['password']
    col.insert_one({'name':pname,'email':email,'phone':ph,'password':password})
    return render_template('login.html')

@app.route("/login")
def login():
    return render_template('login.html')

@app.route("/signin",methods=['POST'])
def signin():
    session.permanent=True
    phone=request.form['ph']
    password=request.form['password']
    session['phone']=phone
    session['userid']=phone
    if((phone)==('1234567890') and (password)==("admin")):
            return render_template('adminhome1.html')
    print(session['userid'])
    for i in col.find():
        if((phone)==i['phone'] and (password)==i['password']):
            return redirect("/parent/home")
            # return render_template('parent_home.html')
    return render_template('register.html')

@app.route("/parent/home")
def parent_home():
    userid = session['userid']
    user_info = col.find_one({"phone" : userid})
    return render_template('parent_landing.html' , user = user_info)

@app.route("/addChild/" , methods = ['POST', 'GET'])
def addchildren():
    if request.method == 'POST':
        userId = session['userid']
        dob = request.form['dob']
        name = request.form['name']
        imgURL = request.form['imgUrl']
        col.update_one({"phone" : userId} , {"$push" : {"children" : {"$each" : [{"name" : name , "imgURL": imgURL , "dob" : dob , "status" : False , "vacination_list" : [0,0,0,0,0,0,0,0,0,0,0,0]}]}}})
        return render_template('addChild.html' , message = "Success")
    else:
        return render_template('addChild.html')

@app.route('/Questions/' , methods = ['POST','GET'])
def load_FAQ():
    if request.method == 'POST':
        user = session['userid']
        message = request.form['message']
        return message
    return render_template('FAQ.html')

@app.route('/vacination/')
def getvacination_status():
    return "user"

@app.route('/Forum/')
def getForum():
    forum_message = forum.find({})
    return render_template('forum.html' , forum_message = forum_message)

@app.route('/Forum/add' , methods = ['POST'])
def addtoForum():
    user = session['userid']
    message = request.form['message']
    comments = []
    if len(message) == 0:
        return redirect(url_for('getForum')) 
    forum.insert_one({"publisherId" : user , "comments" : comments , "message" : message})
    return redirect(url_for('getForum'))

@app.route('/Forum/comment' , methods = ['POST'])
def addComment():
    user = session['userid']
    comment = request.form['comment']
    if len(comment) == 0:
        return redirect(url_for('getForum'))    
    forum.update_one({"publisherId" : user} , { "$push" : {"comments" : comment}})
    return redirect(url_for('getForum'))

@app.route('/user/Forum/')
def getUserForum():
    userid = session['userid']
    get_posts = forum.find({"publisherId" : userid})
    return "okaty"

@app.route('/contact/' , methods = ['POST' , 'GET'])
def getContact():
    if request.method == 'POST':
        message = request.form['message']
        notification.gen_mail_to_team(message)

    userid = session['userid']
    pincode = col.find_one({"phone" : userid} , {"pincode" : 1 , "_id" : 0})
    asha_worker = list(ashausers.find({"pincode" : str(pincode['pincode'])}))
    return render_template('contactpage.html' , workerdata = asha_worker)

@app.route("/child/")
def loadtest():
    return "TEST"

@app.route("/update_asha/<id>")
def update_worker(id):
    if request.method == "POST":
        name=request.form['name']
        email=request.form['email']
        ph=request.form['ph']
        city=request.form['city']
        pincode=request.form['pincode']
        userid=request.form['userid']
        password=request.form['password']
        ashausers.remove({'email':email})
        ashausers.update_one({'email':email,'ph':ph} , {"$set" : {'name':name,'city':city,'pincode':pincode,'userid':userid,'password':password}})
    getpresentdata = ashausers.find_one({"userid" : ObjectId(id)})
    print(getpresentdata)
    return  render_template('updateAshaUser.html' , data = getpresentdata)



value={'1':'Polio Vaccine','2':'Hepatitis B Vaccine','3':'Rotavirus Vaccine','4':'Influenza Vaccine',
'5':'Pneumococcal Vaccine','6':'Meningococcal Vaccine','7':'DTaP Vaccine','8':'Hib Vaccine','9':'MMR Vaccine',
'10':'Chickenpox Vaccine','11':'Hepatitis A Vaccine','12':'HPV Vaccine'}

value1={'Polio Vaccine':'1','Hepatitis B Vaccine':'2','Rotavirus Vaccine':'3','Influenza Vaccine':'4',
'Pneumococcal Vaccine':'5','Meningococcal Vaccine':'6','DTaP Vaccine':'7','Hib Vaccine':'8','MMR Vaccine':'9',
'Chickenpox Vaccine':'10','Hepatitis A Vaccine':'11','HPV Vaccine':'12'}

@app.route('/vaccination/', methods=['GET', 'POST'])
def get_vaccination_status():
    if request.method=='POST':
        vacc_done=request.form.getlist('mycheckbox')
        print(vacc_done)
        # vaccination.insert_one({"user_id":"4","vaccination":["Bello","BKK","BMM"]})
        v = vaccination.find_one({"phone": "7038987950"})
        print(v) ##change this value later
        vac=v["vaccination"]
        print(vac)
        temp=[]
        for x in vacc_done:
            temp.append(value[x])
        vac=vac+temp
        # print(vac)
        vac=set(vac)
        vac=list(vac)
        myquery = {"phone":"7038987950"}
        newvalues={"$set":{"vaccination":vac}}
        vaccination.update_one(myquery,newvalues)
        return 'Done'


    else: 
        v = vaccination.find_one({"phone": "7038987950"})
        vac=v["vaccination"]
        keys=[]
        vacc=[]
        v=[]
        k=[]
        for key,val in value.items():
            if val not in vac:
                vacc.append(val)
                keys.append(key)
            else:
                v.append(val)
                k.append(key)
        # print(vac)
        return render_template('vaccination.html',keys=keys,vac=vacc,k=k,v=v)


@app.route('/children/associated/<id>', methods=['GET', 'POST'])
def children_associated_with_asha(id):
	x=list(col.find({"ashaworkerid":id}))
	return render_template("dv.html",user=x)

@app.route("/add/asha/parent/<id>" , methods = ['POST'])
def add_parent_to_asja(id):
    if request.method == 'POST':
        phone = request.form['phone']
        col.update_one({"phone":phone} , {"$set":{"ashaworkerid" : id}})
    return render_template("addParentAsha.html")

@app.route('/asha/<id>')
def asha_home(id):
    return render_template('addParentAsha.html' , id = id)

@app.route("/notify")
def send_notification_vaccine():
    all_users = list(col.find({}))
    for users in all_users:
        for child in users['children']:
            dob = datetime.date.fromisoformat(child['dob'])
    today=datetime.date.today()
    print(today)
    print(dob)
    diff=(today-dob).days
    print(diff)
    if diff==60:
        notification.gen_SMS_body("7111111111","reminder","English")
    return "Hello"

@app.route('/visual/')
def visuallization():
    data = list(col.find({} , {"state" : 1 , "_id" : 0}))
    state_list = []
    for datapoints in data:
        state_list.append(datapoints['state'])
    fq= defaultdict( int )
    for state in state_list:
        fq[state] += 1
    fq = dict(fq)
    dict_required = {"States" : list(set(state_list)) , "Number" : list((fq.values())) , "Country" : ["India"]*len(set(state_list))}
    print(dict_required)
    df = pd.DataFrame(dict_required)
    fig = px.bar(df, x="States", y="Number", color="Country", barmode="group")
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('notdash2.html', graphJSON=graphJSON)

if __name__ == "__main__":
    app.run(debug=True)