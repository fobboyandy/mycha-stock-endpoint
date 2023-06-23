import json
import sys
import boto3
import pickle

from dotenv import load_dotenv
from os.path import join, dirname
import os

from datetime import datetime, time

dotenv_path = ".env"
values = load_dotenv(dotenv_path)


def download_file(filename):
    #open up access to s3
    s3 = boto3.client('s3', 
                      region_name='us-east-2',
                      aws_access_key_id=os.environ.get("ACCESS_KEY"),
                      aws_secret_access_key=os.environ.get("SECRET_KEY"))
                      
    try:
        s3.download_file('mycha-inventory', filename, filename, Config=boto3.s3.transfer.TransferConfig(use_threads=False))
        data = pickle.load( open(filename, "rb" ) )
        return data 
    except:
        return 'not found'
        
        
location_name = json.loads(sys.argv[1])
        
data = download_file(location_name+'_stock-second')


print(json.dumps({"stock":data["stock"], "time":str(data["time"])}, indent=2))
