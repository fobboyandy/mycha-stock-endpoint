import json
import sys
import boto3
import pickle
import pytz
from datetime import datetime

from dotenv import load_dotenv
from os.path import join, dirname
import os

dotenv_path = ".env"
values = load_dotenv(dotenv_path)


def upload_file(filename, data):
    #open up access to s3
    s3 = boto3.client('s3', 
                      region_name='us-east-2',
                      aws_access_key_id=os.environ.get("ACCESS_KEY"),
                      aws_secret_access_key=os.environ.get("SECRET_KEY"))
    
    pickle.dump( data, open( filename, "wb" ) )
    s3.upload_file(filename, 'mycha-inventory', filename)

timezone = pytz.timezone('US/Central')
submission_time = datetime.now(timezone).timestamp()

stock = json.loads(sys.argv[1])
    
location_stock = {"stock": stock, "time": submission_time}

location_name = json.loads(sys.argv[2])


upload_file(location_name+"_stock-data", location_stock)
# print(json.dumps(submission_time))
print(json.dumps({"status": str('success'), "time": str(submission_time)}))



