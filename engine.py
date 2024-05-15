import numpy as np
import pandas as pd
import json
import plotly.express as px
import time
from http.client import HTTPSConnection
from datetime import datetime


DOMAIN_NAME = 'www.seele-tracking.com'
CLIENT_ID_SEELE = 'EE9F73B3-474E-4D10-884A-04196D47DABF' 
GROUP_ID_DELIVERY_HEADER = '067D7718-6C48-4517-AB80-5E6128BAC7C2'
GROUP_ID_DELIVERY_POS = '9EDB2170-EBD4-4F54-BB1E-7E5364FD7320'
USER ='bot@seele.com'
PASSWORD ='1234'
KEY ="ObjectList"


def basic_auth(username, password):


    c = HTTPSConnection(DOMAIN_NAME)
    c.request('POST','/RCOMAPI/token',"grant_type=password&username={0}&password={1}".format(username,password).encode('utf-8'))
    data = json.loads(c.getresponse().read().decode('utf-8'))
    c.close()

    return data["access_token"]


def get_rcom_objects(domainName, token, clientID, groupID, binName=None, searchKey=None, searchValue=None, changedFrom=None, changedUntil=None):

    properties={}
    if (searchValue!= None and searchKey!= None):properties={searchKey:searchValue}
    searchRcomObject={"ClientID" : clientID,"ObjectGroupID" : groupID,"Location" : binName,"FromDate" : changedFrom,"UntilDate" : changedUntil,"Properties":properties}
    c = HTTPSConnection(domainName)
    c.request('POST','/RCOMAPI/api/object/searchobjects',body=json.dumps(searchRcomObject).encode('utf-8'),headers={'Authorization':'Bearer {0}'.format(token),'Content-Type':'application/json'})
    objects = json.loads(c.getresponse().read().decode('utf-8'))
    c.close()

    return objects


def get_rcom_bins(domainName,token):

    c = HTTPSConnection(domainName)
    c.request('GET','/RCOMAPI/api/object/getbins',headers={'Authorization':'Bearer {0}'.format(token),'Content-Type':'application/json'})
    bins=json.loads(c.getresponse().read().decode('utf-8'))
    c.close()

    return bins


def format_rcom_data(objects,bins=None):

    #format bins
    if bins!=None:
      bins_={}
      for item in bins:
        bins_[item['BIN_ID']]=item['BIN_NAME']

    #format objects
    #if  key in objects.keys():
    df_=pd.DataFrame()
    for item in objects:#[key]:
      if bins!=None:
        if item['BinID'] in bins_.keys():
          item['BinID']=bins_[item['BinID']]
      cols,vals=zip(*([[x,[item[x]]] for x in item.keys() if x!='Attributes']+[[x['Name'],[x['Value']]] for x in item['Attributes']]))
      if cols!=None:
        df_=pd.concat([df_,pd.DataFrame(vals,cols).T])
    return df_



def gewicht(df):

    rlas = ["RLA 01", "RLA 02", "RLA 03", "RLA 04", "RLA 05", "RLA 06", "RLA 07", "RLA 08", "RLA 09", "RLA 10", "RLA 11", "RLA 12", "RLA 13", "RLA 14", "RLA 15", "RLA 16", "RLA 17", "RLA 18", "RLA 19", "RLA 20", "RLA 21", "RLA 22", "RLA 23"]
    rla_new = []
    status = ['warehouse', 'readytoship', 'onsite', 'shipped', 'installed']
    status_new =[]
    weights = []
    for rla in rlas: 
        for stat in status:
            df_filtered = df[df["warenausgang_hinweise"].str.contains(rla)==True]
            df_filtered = df_filtered[df_filtered["status"]==stat]
            weight = df_filtered['warenausgang_gewicht'].apply(pd.to_numeric).sum()
            weights.append(weight)
            rla_new.append(rla)
            status_new.append(stat)

    diBar = {
       'RLA_Nummer': rla_new,
        'Status': status_new,
        'Material_kg': weights}
    
    df_bar = pd.DataFrame.from_dict(diBar)
    
    return df_bar

def lieferschein(df):

    rlas = ["RLA 01", "RLA 02", "RLA 03", "RLA 04", "RLA 05", "RLA 06", "RLA 07", "RLA 08", "RLA 09", "RLA 10", "RLA 11", "RLA 12", "RLA 13", "RLA 14", "RLA 15", "RLA 16", "RLA 17", "RLA 18", "RLA 19", "RLA 20", "RLA 21", "RLA 22", "RLA 23"]
    rla_new = []
    status = ['readytoship','shipped','warehouse', 'onsite', 'installed']
    status_new =[]
    count_ls = []

    for rla in rlas: 
        for stat in status:
            df_filtered = df[df["warenausgang_hinweise"].str.contains(rla)==True]
            df_filtered = df_filtered[df_filtered["status"]==stat]
            count = df_filtered['warenausgang_gewicht'].shape[0]
            count_ls.append(count)
            rla_new.append(rla)
            status_new.append(stat)
    
    diBar = {
    'rla_nummer': rla_new,
    'status': status_new,
    'anzahl_lieferscheine': count_ls
    }   

    df_bar = pd.DataFrame.from_dict(diBar)

    return df_bar

def bar_1796(df):

    target = ["RLA", "Nicht RLA"]
    count =[]

    df_1796 = df[df["warenausgang_projekt"]=="1796"]
    count1 = df[df["warenausgang_hinweise"].str.contains("RLA")==True].shape[0]
    count.append(count1)
    count2 = df_1796[df_1796["warenausgang_hinweise"].str.contains("RLA")==False].shape[0]
    count2 += df[df["warenausgang_hinweise"].isnull()].shape[0]
    count.append(count2)

    
    diBar = {
    'ziel': target,
    'lieferscheine': count
    }   

    df_bar = pd.DataFrame.from_dict(diBar)

    return df_bar

def plz(df):
    
    plz=['71665', '70173', 'other']
    counts=[]

    counts.append(df[df['empfaenger_plz']=='71665'].shape[0])
    counts.append(df[df['empfaenger_plz']=='70173'].shape[0])
    counts.append(df.shape[0]-counts[0]-counts[1])

    dic_plz = {
        'plz': plz,
        'counts': counts
    }

    df_plz = pd.DataFrame.from_dict(dic_plz)
    
    return df_plz

def installed(df):

    df_installed = df[df['status']=='installed']
    df_installed['date_installed']=pd.to_datetime(df_installed['date_installed'])
    df_installed.reset_index(drop=True, inplace=True)
    df_installed.set_index('date_installed', inplace=True)
    df_hist = df_installed['lieferschein'].resample('W').count().to_frame()
    df_hist.reset_index(inplace=True)
    df_hist.rename(columns={'date_installed': 'week_installed', 'lieferschein': 'anzahl_lieferscheine'}, inplace=True)

    return df_hist

def warehouse(df):

    df_warehouse = df[df['status']=='warehouse']
    df_warehouse['date_warehouse']=pd.to_datetime(df_warehouse['date_warehouse'], format='%d.%m.%Y')
    df_warehouse.reset_index(drop=True, inplace=True)
    df_warehouse.set_index('date_warehouse', inplace=True)
    df_ware = df_warehouse['lieferschein'].resample('W').count().to_frame()
    df_ware.reset_index(inplace=True)
    df_ware.rename(columns={'date_warehouse': 'week_warehouse', 'lieferschein': 'anzahl_lieferscheine'}, inplace=True)

    return df_ware

def onsite(df):

    df_onsite = df[df['status']=='onsite']
    df_onsite['date_onsite']=pd.to_datetime(df_onsite['date_onsite'], format='%d.%m.%Y')
    df_onsite.reset_index(drop=True, inplace=True)
    df_onsite.set_index('date_onsite', inplace=True)
    df_onsite = df_onsite['lieferschein'].resample('W').count().to_frame()
    df_onsite.reset_index(inplace=True)
    df_onsite.rename(columns={'date_onsite': 'week_onsite', 'lieferschein': 'anzahl_lieferscheine'}, inplace=True)

    return df_onsite

def gate():

    _type = ['Handheld', 'Gate']
    _count = []

    _count.append(df[df['warehouse_lager'].isnull()].shape[0])
    _count.append(df[df['warehouse_lager'].str.contains('Gate')==True].shape[0])

    dic_gate = {
        'Type': _type,
        'Count': _count
        }

    df_gate = pd.DataFrame.from_dict(dic_gate)

    return df_gate

token = basic_auth(USER, PASSWORD)

