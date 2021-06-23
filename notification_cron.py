from pymongo import MongoClient
import keys
import datetime
import notification
import schedule
import time

cluster= MongoClient("mongodb+srv://cfgteam74:cfgteam74@cluster0.5pow9.mongodb.net/flaskwebsite?retryWrites=true&w=majority")
db=cluster["flaskwebsite"]
col=db['users']
def send_notification():
    all_users = list(col.find({}))
    for users in all_users:
        for child in users['children']:
            dob = datetime.date.fromisoformat(child['dob'])
            today = datetime.date.today() 
            if dob.strftime("%d") == today.strftime("%d") and dob.month == today.month:
                age = today - dob
                message = "Your child is " + str(age) + "days old today. Please take the test"
                print("[S]Sending message")
                notification.gen_SMS_body(users['phone'] , 'reminder' , users['language'])
                try:
                    notification.gen_email_body(users['email'] , 'reminder' , users['language'])
                except:
                    print("[W]Email address not found")
                    print("[W]User Phone number:")
                    print(user['phone'])
            
schedule.every().day.at("00:00").do(send_notification)
while True:
    schedule.run_pending()
    time.sleep(10)