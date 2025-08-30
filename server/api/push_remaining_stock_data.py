import requests
from bs4 import BeautifulSoup
from datetime import datetime
from datetime import timedelta
import time as tee
import pytz
import pickle
import boto3
import botocore
import os

NUM_SECONDS_PER_DAY = 60*60*24

from dotenv import load_dotenv

dotenv_path = ".env"
values = load_dotenv(dotenv_path)

aws_access_key_id = os.environ.get("ACCESS_KEY")
aws_secret_access_key = os.environ.get("SECRET_KEY")

loginUrl = 'https://seedlive.com/login.i'

chicago_payload = {
    'username' : os.environ.get("seedlive_chi_user"),
    'password' : os.environ.get("seedlive_chi_pw")
}


la_payload = {
    'username' : os.environ.get("seedlive_la_user"),
    'password' : os.environ.get("seedlive_la_pw")
}

TIME_COL = 6
CARD_NUM_COL = 9
PRICE_COL = 10
PRODUCT_ID_COL = 12

def generateSalesUrl(numDaysBeforeToday, terminal_ids):

    if not terminal_ids or not len(terminal_ids):
        return None

    timezone = pytz.timezone('US/Central')
    endDate = datetime.now(timezone)
    startDate = endDate - timedelta(days = numDaysBeforeToday)
    
    startDateStr = startDate.strftime("%m-%d-%Y")
    endDateStr = endDate.strftime("%m-%d-%Y")
    
    total_transaction_sales_url = 'https://seedlive.com/activity_detail.i?saveAction=save_report_params_prompt.i' + \
    '&rangeType=DAY' + \
    '&params.beginDate='+startDateStr+\
    '&params.endDate='+endDateStr+ \
    '&params.tranType=101,91,92,89,90,66,21,67,16,97,87,96,73,69,33,52,53,98,74,13,83,85,86,84,78,15,76,20,38,28,27,94,99,17,34,40,42,44,46,95,64,65,63,54,81,82,55,56,103,48,50,104,18,62,79,70,80,71,72,93,75,30,57,77,59,102,31,39,25,24,32,100,68,88,22,26,29' + \
    '&Currency_Id=1' + \
    '&Region_Name=' + \
    '&Terminal_Id='
    
    for location_name, id in terminal_ids.items():
        total_transaction_sales_url += id + ','
        
    total_transaction_sales_url  = total_transaction_sales_url[0: -1] # delete the last ','
    
    total_transaction_sales_url += '&day=' 
    
    currDate = startDate
    currDateStr = startDateStr
    total_transaction_sales_url += currDateStr
    while(currDateStr != endDateStr):
        currDate += timedelta(days = 1)
        currDateStr = currDate.strftime("%m-%d-%Y")
        total_transaction_sales_url += ',' + currDateStr
        
    total_transaction_sales_url += \
    '&Trans_Type_Id=16,53,97,96,98'
    
    return total_transaction_sales_url
    
def normalizeLocationName(location_name):
    normal_location_name = ""
    
    for c in location_name:
        if (ord(c) >= ord('a') and ord(c) <= ord('z')) or (ord(c) >= ord('A') and ord(c) <= ord('Z')) or (ord(c) >= ord('0') and ord(c) <= ord('9')) or (ord(c) == ord('-')):
            normal_location_name += c
        
    return normal_location_name

def tcnIndexToRowCol(index):
    return ((index - 1)//10, (index - 1) % 10)
    
    

def getOtherSalesPagesUrls(content):



    # print("content", content)
    search_string = b"&nbsp;of&nbsp;"
    
    
    pages = 1
    #get pages
    find_idx = content.find(search_string)
    if(find_idx != -1 ):
        end_idx =  content.find(b"</td>", find_idx)
        pages = int(content[find_idx + len(search_string) : end_idx - 1])
        print("pages", pages)
        
    urls = []
    
    if(pages < 2):
        print("no other pages found")
        return []
    else:

        # print("content", content)
        request_id_search_string = b"<input type=\"hidden\" name=\"requestId\" value="
        profile_id_search_string = b"<input type=\"hidden\" name=\"profileId\" value="

        #find profile and request id and generate the rest of the urls
        url_prefix = "https://seedlive.com/retrieve_report_page_by_user.i?pollInterval=1000&pollIntervalIndex=1"

        print("multiple pages? command_idx", find_idx)

        if(find_idx != -1):
                
            value_search_start_idx = content.find(request_id_search_string)
            value_search_end_idx = content.find(b"\" />", value_search_start_idx + len(request_id_search_string))
            request_id = content[value_search_start_idx + len(request_id_search_string) + 1: value_search_end_idx].decode()


            value_search_start_idx = content.find(profile_id_search_string)
            value_search_end_idx = content.find(b"\" />", value_search_start_idx + len(profile_id_search_string))
            profile_id = content[value_search_start_idx + len(profile_id_search_string) + 1: value_search_end_idx].decode()

            print("request_id", request_id)
            print("profile_id", profile_id)
            # page_command = str(page_command, 'utf-8')
            
            for page_num in range(pages - 1):
                page_url = url_prefix + "&profileId="+profile_id+"&requestId="+request_id+"&pageId="+str(page_num+1)
                urls.append(page_url)
                
            print(urls)
        
                
    return urls
    


    
def generateSalesByLocation(login_data, url):    
    current_report_location = ""

    if "seedlive.com" not in url:
        return {}
    
    with requests.session() as s:
        s.post(loginUrl, data = login_data)
    
    def getContentFromUrl(urlIn):
        r = s.get(urlIn)
        attempts = 0
        while(r.text.find("Your report is being generated") != -1 and attempts < 5):
            tee.sleep(2) # wait a sec
            r = s.get(urlIn)
            attempts += 1
            
        if(r.text.find("Your report is being generated") != -1):
            raise "Failed to get report in a timely manner"
            
        return r.content;
          
    sales_by_location = {}
          
    def readSalesFromSoup(soupIn):
        global current_report_location
        
        new_location = False
        transactions_table_start = False
        col = 0
        current_date = ""
        
        all_tr = soup.find_all("tr")
        for tr in all_tr:
            tr_items = str.split(tr.get_text(), '\n')
        
            valid_transaction = True
            
            # find some important headers to determine the format
            # of this tr block
            for index, tr_item in enumerate(tr_items):
                
                if tr_item == "Location:":
                    new_location = True
                    transactions_table_start = False
                    valid_transaction = False
                elif tr_item == "Apply To Card Id":
                    new_location = False
                    transactions_table_start = True
                    valid_transaction = False
                elif new_location:
                        current_report_location = tr_item
                        new_location = False
                        transactions_table_start = False
                        valid_transaction = False
                        
            expected_transaction_tr_len = 35
            if valid_transaction and transactions_table_start and len(tr_items) == expected_transaction_tr_len:
            
                all_td = tr.find_all('td')
                
                # adding an hour to the timestamp from seedlive. for some reason the reported transactions are real time
                # but all the timestamps are indicating that it's an hour ago
                timestamp = int(all_td[1].get('data-sort-value')) // 1000 + 3600
                
                datetime_index = 5
                amount_index = 17
                item_id_index = 23
                
                datetime = tr_items[datetime_index]
                amount = tr_items[amount_index]
                id = tr_items[item_id_index]
                
                # make sure it's not a refund. refunds don't have product id
                if(len(id)):
                    id = int(id[0:4], 16)
                    
                    if current_report_location not in sales_by_location:
                        sales_by_location[current_report_location] = []
                        
                    sales_by_location[current_report_location].append({"ID":id, "Amount": amount, "Timestamp":timestamp, "Datetime":datetime})
                    
    content = getContentFromUrl(url)
    soup = BeautifulSoup(content, 'html.parser')
    readSalesFromSoup(soup)
    
    restOfPagesUrls = getOtherSalesPagesUrls(content)
    for pageUrl in restOfPagesUrls:
        content = getContentFromUrl(pageUrl)
        soup = BeautifulSoup(content, 'html.parser')
        readSalesFromSoup(soup)
    
    return sales_by_location


def upload_file(filename, data):
    #open up access to s3

    s3 = boto3.client('s3',  region_name='us-east-2', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
    pickle.dump( data, open( filename, "wb" ) )
    s3.upload_file(filename, 'mycha-inventory', filename)



def download_file(filename):

    #open up access to s3
    s3 = boto3.client('s3',  region_name='us-east-2', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
    try:
        s3.download_file('mycha-inventory', filename, filename, Config=boto3.s3.transfer.TransferConfig(use_threads=False))
        data = pickle.load( open(filename, "rb" ) )
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            data = None
        else:
            raise
            
    return data

# creates a report, looks at the stocking information and then looks at layout
# to generate the exact state of the machine at this time
def calculate_inventory_remaining(locations, login_data, REPORT_DAYS_LIMIT = 3):
    
    terminal_ids = download_file("terminal_ids")
    
    selected_terminal_ids = {}
    
    # go through each location and find the maximum number of days
    # we need to dig through in the sales report based on the last time
    # these selected locations were stocked. for example, location A could have
    # been last stocked 5 days ago, we need sales report going back 5 days ago to 
    # start checking how many were sold since it was last stocked
    
    for location in locations:
        selected_terminal_ids[location] = terminal_ids[location]
        
    inventory_stocking_data_by_location = {}
    
    centraltimezone = pytz.timezone('US/Central')
    thetimenow = int(datetime.now(centraltimezone).timestamp())
    datenow = str(datetime.fromtimestamp(thetimenow, centraltimezone))[0:10]
            
    # find the machine with the oldest restock time. this should be the machine with 
    # the smallest timestamp
    oldest_restocked_timestamp = thetimenow
    
    valid_terminal_ids_for_report = {}
    
    inventory_stock_data_by_location = {}
    for location in locations:
        inventory_stock_data = download_file(normalizeLocationName(location)+"_stock-data")
        # if the data exists but the stocking time is beyond an upper limit, eg. the machine was 
        # last stocked before the beginning of a long holiday break, just treat the machine as empty
        # we need to do this in order to have an upper bound on the how far we should go back in the 
        # sales reports. Also if we cant find a restock data (not yet initialized, then treat it as empty also)
        inventory_stock_data_by_location[location] = inventory_stock_data
        if inventory_stock_data:
            last_restock_time_timestamp = int(inventory_stock_data["time"])
            
            laststockingdate = str(datetime.fromtimestamp(last_restock_time_timestamp, centraltimezone))[0:10]
            d1 = datetime.strptime(datenow, "%Y-%m-%d")
            d2 = datetime.strptime(laststockingdate, "%Y-%m-%d")
            deltadates = d1 - d2
            deltadays = deltadates.days
            
            if deltadays <= REPORT_DAYS_LIMIT:
                valid_terminal_ids_for_report[location] = selected_terminal_ids[location]
                if last_restock_time_timestamp < oldest_restocked_timestamp:
                    oldest_restocked_timestamp = last_restock_time_timestamp
                    
    oldestlaststockingdate = str(datetime.fromtimestamp(oldest_restocked_timestamp, centraltimezone))[0:10]
    d1 = datetime.strptime(datenow, "%Y-%m-%d")
    d2 = datetime.strptime(oldestlaststockingdate, "%Y-%m-%d")
    maxdeltadates = d1 - d2
    maxdeltadays = maxdeltadates.days

    remaining_inventory_by_location = {}
    
    # locations that are not valid for generating a report means it exceeded the restocking days
    # assume they are empty
    for loc in locations:
        if loc not in valid_terminal_ids_for_report:
            remaining_inventory_by_location[loc] = [[0] * 7] * 6
        else:
            remaining_inventory_by_location[loc] = inventory_stock_data_by_location[loc]["stock"]

    salesByLocation = {}
    
    if len(valid_terminal_ids_for_report):
        salesReportUrl = generateSalesUrl(int(maxdeltadays), valid_terminal_ids_for_report)
    
        salesByLocation = generateSalesByLocation(login_data, salesReportUrl)

    # subtract every sale past the restocking timestamp
    for loc, sales in salesByLocation.items():
        timestamp_since_restock = int(inventory_stock_data_by_location[loc]["time"])

        for sale in sales:
            # for each sale, if the timestamp is after restock, then subtract from
            # the inventory stock data
            if sale["Timestamp"] >= timestamp_since_restock:

                row,col = tcnIndexToRowCol(sale["ID"])
                
                remaining_inventory_by_location[loc][row][col] -= 1
                if(remaining_inventory_by_location[loc][row][col] < 0):
                    remaining_inventory_by_location[loc][row][col] = 0
                
    print("remaining_inventory_by_location", remaining_inventory_by_location)
            
    return remaining_inventory_by_location
    
    
groups = download_file("groups")
layout = download_file("layout")

chicago_locations = []
la_locations = []

for location, group in groups.items():
    if(group.lower() == "chicago"):
        chicago_locations.append(location)
    elif(group.lower() == "la"):
        la_locations.append(location)


# print("chicago_locations", chicago_locations, "la_locations", la_locations)

chi_remaining_inventory_by_location = calculate_inventory_remaining(chicago_locations, chicago_payload, 7)
la_rem_inventory_by_location = calculate_inventory_remaining(la_locations, la_payload, 7)

remaining_inventory_by_location = chi_remaining_inventory_by_location | la_rem_inventory_by_location

#organized as group:location:item name, count
for location,inventory in remaining_inventory_by_location.items():
    inventory_with_name = []
    for row in range(6):
        row_items = []
        for col in range(7):
            name = layout[location][row][col]
            count = inventory[row][col] 
            row_items.append((name, count))
                
        inventory_with_name.append(row_items)
        
    upload_file(location+"_current_inventory_fobboyandy", inventory_with_name)

