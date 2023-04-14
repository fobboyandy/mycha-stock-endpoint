import json
import boto3
import pickle

import os
from os.path import join, dirname

from dotenv import load_dotenv

path = ".env"
values = load_dotenv(path)

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
        print("couldn't load file from S3.")
        return None
        
layout = download_file('layout')

locations = json.dumps(list(layout.keys()))

print(locations)