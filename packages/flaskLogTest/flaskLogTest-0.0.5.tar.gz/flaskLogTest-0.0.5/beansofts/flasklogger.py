import json
from lib2to3.pgen2 import token
import string
from textwrap import wrap
from traceback import print_tb
from flask import jsonify,request
from werkzeug.security import check_password_hash,generate_password_hash
import socket
import geocoder
import os
import pika
import time
import jwt

from functools import wraps
def channelInfo(usrInfo):
    #!/usr/bin/env python
    #establishig a connection
    # convertion of the data to string
    usrInfo=json.dumps(usrInfo)
    url = os.environ.get('CLOUDAMQP_URL', 'amqps://tnmldbri:STSB8LTzIx8PRW8sgaiAslc0iCocUvXe@puffin.rmq2.cloudamqp.com/tnmldbri')
    params = pika.URLParameters(url)
    connection = pika.BlockingConnection(params)
    channel = connection.channel() # start a channel
    channel.queue_declare(queue='leon') # Declare a queue
    channel.basic_publish(exchange='',
                        routing_key='hello',
                        body=usrInfo) #collection of data
    # print(" [x] Sent 'Hello World!'")
    connection.close()
    # authentiocation decroraor

secret_key='BeansoftsLimited/6753Hvcd'
def token_required_addKey(f):
    @wraps(f)
    def decorated(*args,**kwargs):
        # token=request.args.get("token")
        header = request.headers.get('Authorization')
        _, token = header.split()
        print(token)
        # print('jvdvbk')
        # decoded = jwt.decode(token, app.config['SECRET_KEY'], algorithms='HS256')
        # print(decoded)
        if not token:
            return jsonify({'message':'denied'}),401#missing token
        try:
            data=jwt.decode(token,secret_key)
            print(data)
            # print(data)
        except Exception as e:
            print("hello me",e)

            return jsonify({'message':'denied'}),401 #invalid token
        return "hello"
    return decorated















def registerUser(f):
    def wrapper(*args,**kwargs):
        if request.method=="POST":
            contents=request.get_json() #user data
            contents["datafield"]="register"
            #appending Keys
            contents["API_KEY"]="false"
            contents["SECRET_KEY"]="false"


            # acquire user ip adress
            ip_addr = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
            # appending ip
            contents["ip"]=ip_addr
            contents['url']=request.host
            #user location
            location=geocoder.ip(ip_addr)
            city=location.city
            coordinates=location.latlng
            location=f"{city}-{coordinates}"
            contents["location"]=location
            channelInfo(contents)



            # print("hello")
            
        return "hello"
    return wrapper

        











# login decorator
# @token_required
def login(f):
    def login_wrapper(*args,**kwargs):
        loginCredentials=["password","username","password","phone number","email"]
        if request.method=="POST":
            contents=request.get_json()
            foundCredentials=[]
            for key,value in contents.items():
                if key in loginCredentials:
                    foundCredentials.append(key)
                if len(foundCredentials)==0:
                    return f" credentials requirend to login {loginCredentials}"
            # contents['url']=request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
            ip_addr = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
            contents["ip"]=ip_addr
            contents['url']=request.host
            # time and confiruation
            from datetime import datetime,timezone,timedelta
            import re
            now = datetime.now(timezone.utc)
            current_time = now.strftime("%H:%M:%S")
            hours=int(current_time[:2])+3
            cur=re.sub(current_time[:2],str(hours),current_time)
            # print(hours)
            # print(type(current_time))
            # kenyan_time_diff=timedelta(hours=3)
            # datetime.time()
            # print(datetime.time())
            # datetime(now)+kenyan_time_diff
            # current_time+=kenyan_time_diff
            contents["log_tim"]=cur
            contents["datafield"]="logins"
            # print(cur)
            # print("hello martin")
            print('hell kenya')

            channelInfo(contents)
            # check very password
            return jsonify(contents)
            
            # return "hello world"

        return "login"
        

    return login_wrapper



# addKeys
def addKeys(f):
    @wraps(f)
    def decorated(*args,**kwargs):
        # token=request.args.get("token")
        header = request.headers.get('Authorization')
        print(header)
        _, token = header.split()
        # decoded = jwt.decode(token, app.config['SECRET_KEY'], algorithms='HS256')
        # print(decoded)
        print(token)
        if not token:
            print("missing")


            return jsonify({'message':'denied'}),401#missing token
        try:
            secrete_key="leonApllication"
            print(token)
            # data=jwt.decode(token,secrete_key)
            # username=data['user']
        except Exception as e:
            print("hellloo",e)
            return jsonify({'message':'denied'}),401 #invalid token
        # return f(username)
        return "hello"
    return decorated  


def add_key_engine():
    print("helo")
    return "hello"

            

