from flask import Flask
import json
import boto3
import pickle

from dotenv import load_dotenv
from os.path import join, dirname
import os



aws_access_key_id = os.environ.get("ACCESS_KEY")
aws_secret_access_key = os.environ.get("SECRET_KEY")


def upload_file(filename, data):
    #open up access to s3

    s3 = boto3.client('s3',  region_name='us-east-2', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
    pickle.dump( data, open( filename, "wb" ) )
    s3.upload_file(filename, 'mycha-inventory', filename)



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
        return None






app = Flask(__name__); 

@app.route('/') 
def home(): 
    return "Running!"




@app.route('/fetch_stock_location/<location>') 
def fetch_stock_location(location): 
            
    filename = location+'_current_inventory_fobboyandy'
    print(filename)
    data = download_file(filename)


    return(json.dumps(data, indent=2))



