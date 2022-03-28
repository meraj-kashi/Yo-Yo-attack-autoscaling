import re
import time
import subprocess
import select
import pymongo
from pymongo import MongoClient
import creds


# Database connection
db_username = creds.db_connection["db_username"]
db_password = creds.db_connection["db_password"]
cluster = MongoClient(f"mongodb+srv://{db_username}:{db_password}@cluster0.dwcri.mongodb.net/tasd?retryWrites=true&w=majority")
db = cluster.test

db = cluster["tasd"]
collection = db["clients"]

# Initialize trusted value T for users
Init_value = 10
request_number = 0
# Tail access log
filename = './access.log'
f = subprocess.Popen(['tail','-F',filename],\
    stdout=subprocess.PIPE,stderr=subprocess.PIPE)

p = select.poll()
p.register(f.stdout)
db.list_collection_names()
trsuted_value = Init_value
while True:
    if p.poll(1):
        client_ip = re.findall(r"^\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}",str(f.stdout.readline().decode("utf-8")))
        print(client_ip[0])
        if not collection.find_one({"client_ip":client_ip[0]}):
            collection.insert_one({"client_ip":client_ip[0], "Trusted_value": trsuted_value, "request_number":request_number})
        else:
            request_number_value = collection.find_one({"client_ip":client_ip[0]})['request_number'] + 1
            collection.find_one_and_update({"client_ip" : client_ip[0]} , { "$set" : { "request_number" : request_number_value  }} )
            print(request_number_value)
    time.sleep(1)