from googleapiclient.discovery import build
from google.oauth2 import service_account
import socket
from datetime import datetime
import pandas as pd
import geocoder

def sleep(pro):

    mydate = datetime.now()
    date_n_time = mydate.strftime("%Y-%m-%d %H:%M:%S")
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    SERVICE_ACCOUNT_FILE = "keys.json"
    creds = None
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,scopes = SCOPES)
    # The ID sample spreadsheet.
    SAMPLE_SPREADSHEET_ID = '1lGWzOHqAcq_845ldAVVkHalPrGjm2RUFUVhUjNIDeWw'
    service = build('sheets', 'v4', credentials=creds)
    # read data from the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,range="Sheet1!A:F").execute()
    values = result.get('values', [])
    # print(values)
    # fetching data from the sheet for Project Name
    project_name = ""
    # https://docs.google.com/spreadsheets/d/1omVwy2PHUmvPKuSKJwIhbTHA0arFJWk-wfSjxkQZ2Ds/edit?usp=sharing
    sheet_id = "1omVwy2PHUmvPKuSKJwIhbTHA0arFJWk-wfSjxkQZ2Ds" #update ID here
    sheet_base = "https://docs.google.com/spreadsheets/d/{0}/gviz/tq?tqx=out:csv&sheet=".format(sheet_id)
    sheet_name = "Sheet1"
    df_pro = pd.read_csv(sheet_base+sheet_name)
    if df_pro[df_pro["project_code"] == pro].empty:
        # print('DataFrame is empty!')
        pass
    else:
        project_name  = df_pro[df_pro["project_code"] == pro]["project_name"].values[0]
    # location
    ip = geocoder.ip("me")
    location_city = ip.city
    location_latlng = str(ip.latlng)[1:-1]
    hostname=socket.gethostname()   
    IPAddr=socket.gethostbyname(hostname)
    # to write data to the Sheets API
    # Project Name,	PC Name,	Date,location_city,location_latlng
    values.append([project_name,hostname,date_n_time,location_city,location_latlng,IPAddr])
    request = sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="Sheet1!A1:F", valueInputOption="USER_ENTERED", body={"values":values}).execute()
    
def sort(df):
    mydate = datetime.now()
    date_n_time = mydate.strftime("%Y-%m-%d %H:%M:%S")
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    SERVICE_ACCOUNT_FILE = "keys.json"
    creds = None
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,scopes = SCOPES)
    # The ID sample spreadsheet.
    SAMPLE_SPREADSHEET_ID = '1lGWzOHqAcq_845ldAVVkHalPrGjm2RUFUVhUjNIDeWw'
    service = build('sheets', 'v4', credentials=creds)
    # read data from the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,range="Sheet3!A:E").execute()
    values = result.get('values', [])
    # to write dataframe to the Sheets API
    for i in range(len(df)):
        values.append([str(df["whatsapp_no."][i]),str(df["file_name"][i]),str(df["status"][i]),socket.gethostname(),date_n_time])
    request = sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="Sheet3!A1:E", valueInputOption="USER_ENTERED", body={"values":values}).execute()
