from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import pymongo
from twilio.rest import Client
from pymongo import MongoClient
import keys

cluster= MongoClient("mongodb+srv://cfgteam74:cfgteam74@cluster0.5pow9.mongodb.net/flaskwebsite?retryWrites=true&w=majority")
db=cluster["Messages"]
col=db['message']

def sendMail(message):
    try:
        sg = SendGridAPIClient(keys.SENDGRID_API_KEY)
        response = sg.send(message)
    except Exception as e:
        print(e.message)


def gen_email_body(id , type , language):
    message = col.find_one({"language" : language , "type" : type} , {"_id":0 , "message":1})
    email_body = Mail(
    from_email='zedmitchell3825@gmail.com',
    to_emails = id,
    subject= "It's time to fill the survey!!",
    html_content= ('<h3>' + message['message'] + '</h3>'))
    sendMail(email_body)


def gen_SMS_body(phone , type , language):
    account_sid = keys.account_sid
    auth_token = keys.auth_token
    message = col.find_one({"language" : language , "type" : type} , {"_id":0 , "message":1})
    client = Client(account_sid, auth_token)
    message = client.messages.create(body=message,from_='+13055703436',to=phone)

def gen_mail_to_team(message):
    email_body = Mail(
    from_email='zedmitchell3825@gmail.com',
    to_emails = 'adityakathal672@gmail.com',
    subject= "FAQ Question",
    html_content= ('<h3>' + message + '</h3>'))
    print("mail going")
    sendMail(email_body)