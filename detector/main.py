import re
import time
import subprocess
import select
from pymongo import MongoClient
import creds
import boto3


# Database connection
db_username = creds.db_connection["db_username"]
db_password = creds.db_connection["db_password"]
cluster = MongoClient(f"mongodb+srv://{db_username}:{db_password}@cluster0.dwcri.mongodb.net/tasd?retryWrites=true&w=majority")
db = cluster.tasd

# AWS connection
init_instance_capacity=1
client = boto3.client('autoscaling', 'us-east-1')

collection_tasd = db["clients"]
collection_scaling = db["scaling"]
collection_clients_scaling = db["clients_scaling"]
collection_suspection = db["suspections"]

if collection_scaling.find_one({"info":"scaling"}):
    if collection_scaling.find_one({"info":"scaling"})['status']!=0 :
        pass
else:
    collection_scaling.insert_one({"info":"scaling", "init_instance_capacity":init_instance_capacity, "status":0})
    print("init")


# Initialize trusted value T for users
Init_value = 10
request_number = 0
# Tail access log
filename = '/var/log/nginx/access.log'
# tail only last line
f = subprocess.Popen(['tail','-n','1','-F',filename],\
    stdout=subprocess.PIPE,stderr=subprocess.PIPE)

p = select.poll()
p.register(f.stdout)
trsuted_value = Init_value
while True:
    asgs = client.describe_auto_scaling_groups()['AutoScalingGroups']
    instance_desired_capacity = asgs[0]['DesiredCapacity']

    init_instance_capacity = collection_scaling.find_one({"info":"scaling"})['init_instance_capacity']
    print(init_instance_capacity)
    # detect scale up
    if instance_desired_capacity > init_instance_capacity:
        print("scale up")
        collection_scaling.find_one_and_update({"info":"scaling"},  { "$set" : {'status':1}})
        collection_scaling.find_one_and_update({"info":"scaling"},  { "$set" : {'init_instance_capacity':instance_desired_capacity}})
    
    # detect scale down
    if instance_desired_capacity < init_instance_capacity:
        print("scale down")
        collection_scaling.find_one_and_update({"info":"scaling"},  { "$set" : {'status':-1}})
        collection_scaling.find_one_and_update({"info":"scaling"},  { "$set" : {'init_instance_capacity':instance_desired_capacity}})
    # read UP address    
    raw_ip = re.findall(r"\"\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}\"",str(f.stdout.readline().decode("utf-8")))
    if raw_ip :
        client_ip = raw_ip[0].replace("\"","")
        print(client_ip)
        if collection_scaling.find_one({"info":"scaling"})['status']==0:
            if not collection_tasd.find_one({"client_ip":client_ip}):
                collection_tasd.insert_one({"client_ip":client_ip, "Trusted_value": trsuted_value, "request_number":request_number})
        elif collection_scaling.find_one({"info":"scaling"})['status']==1:
            if not collection_tasd.find_one({"client_ip":client_ip}):
                collection_tasd.insert_one({"client_ip":client_ip, "Trusted_value": trsuted_value, "request_number":request_number})
            else:
                request_number_value = collection_tasd.find_one({"client_ip":client_ip})['request_number'] + 1
                collection_tasd.find_one_and_update({"client_ip" : client_ip} , { "$set" : { "request_number" : request_number_value  }} )

            for item in collection_tasd.find({"request_number":{ "$gt" : 100}}):
                high_client_ip = item["client_ip"]
                high_request_number = item ["request_number"]
                if not collection_clients_scaling.find_one({"high_client_ip":high_client_ip}):
                    collection_clients_scaling.insert_one({"high_client_ip":high_client_ip,"high_request_number":high_request_number})
                else:
                    collection_clients_scaling.find_one_and_update({"high_client_ip" : high_client_ip} , { "$set" : { "high_request_number" : high_request_number  }} )


        elif collection_scaling.find_one({"info":"scaling"})['status']== -1 :
            if not collection_tasd.find_one({"client_ip":client_ip}):
                collection_tasd.insert_one({"client_ip":client_ip, "Trusted_value": trsuted_value, "request_number": 0})
            else:
                request_number_value = collection_tasd.find_one({"client_ip":client_ip})['request_number'] + 1
                collection_tasd.find_one_and_update({"client_ip" : client_ip} , { "$set" : { "request_number" : request_number_value  }} )

            for item in collection_clients_scaling.find({}):
                x= collection_tasd.find_one({"client_ip": item['high_client_ip']})['request_number'] - (item['high_request_number'])
                if x > 50:
                    print("suspect")
                    new_trsuted_value = collection_tasd.find_one({"client_ip":item['high_client_ip']})['Trusted_value'] - 1
                    collection_tasd.find_one_and_update({"client_ip" : item['high_client_ip']} , { "$set" : { "Trusted_value" : new_trsuted_value }} )
                    collection_tasd.find_one_and_update({"client_ip" : item['high_client_ip']} , { "$set" : { "request_number" : 0  }} )
                    collection_suspection.insert_one({"client_ip":item['high_client_ip'], "Trusted_value": new_trsuted_value})
                    collection_clients_scaling.delete_one({"high_client_ip":item['high_client_ip']})

