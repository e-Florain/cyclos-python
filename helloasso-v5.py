#!/usr/bin/python3
# -*- coding: utf-8 -*-
import requests
import json
import re
import os
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta
import config as cfg
import cyclos
from cyclos import Cyclos

requests.packages.urllib3.disable_warnings()

def displayJson(json_text):
    json_object = json.loads(json_text)
    json_formatted_str = json.dumps(json_object, indent=2)
    print(json_formatted_str)

cyclos = Cyclos()
with open(cfg.ha['transactions']) as data_file:
	listtransactions = json.load(data_file)

now = datetime.now()
last_hour_date_time = datetime.now() - timedelta(days = 2)
#url = cfg.ha['url']+'?from='+last_hour_date_time.strftime("%Y-%m-%dT%H:%M:%S")
url = 'https://api.helloasso.com/oauth2/token'
headers = {'Content-type': 'application/x-www-form-urlencoded', 'Accept': 'text/plain'}
data = {
    'grant_type': 'client_credentials',
    'client_id': cfg.ha['user'],
    'client_secret': cfg.ha['password']
}
resp = requests.post(url, verify=False, data=data, headers=headers)
result = json.loads(resp.text)
token = result['access_token']

url = 'https://api.helloasso.com/v5/organizations/le-florain'
params = {}
headers = {'Content-type': 'application/json', 'Authorization': 'Bearer '+token}
resp = requests.get(url, params=params, headers=headers)

now = datetime.now()
last_hour_date_time = datetime.now() - timedelta(days = 30)
#url = cfg.ha['url']+'?from='+last_hour_date_time.strftime("%Y-%m-%dT%H:%M:%S")
url = 'https://api.helloasso.com/v5/organizations/le-florain/payments'+'?from='+last_hour_date_time.strftime("%Y-%m-%dT%H:%M:%S")
params = {}
headers = {'Content-type': 'application/json', 'Authorization': 'Bearer '+token}
resp = requests.get(url, params=params, headers=headers)
displayJson(resp.text)
result = json.loads(resp.text)
for data in result['data']:
    #print data['order']['id']
    #print listtransactions
    #print data['order']['id'] not in listtransactions
    if (str(data['id']) not in listtransactions):
        if ((data['order']['formSlug'] == 'change-florain-numerique-credit-unitaire') or
            (data['order']['formSlug'] == 'test-change-florain-numerique-credit-mensuel')):
            for item in data['items']:
                amount = item['amount']
            accountID = cyclos.getIdFromEmail(data['payer']['email'])
            amountCyclos = amount/100
            if (accountID != False):
                #print amountCyclos
                res = cyclos.setPaymentSystemtoUser(accountID, amountCyclos,"Transaction via HelloAsso Id : "+str(data['order']['id']))
                #res = {}
            #res['transactionNumber']="XXX"
                tmp = {
                    'date': data['date'],
                    'orderdate': data['order']['date'],
                    'orderid': data['order']['id'],
                    'transactionCyclos' : res['transactionNumber'],
                    'formulaire': data['order']['formSlug'],
                    'email': data['payer']['email'],
                    'amount': amountCyclos
                }
            else:
                tmp = {
                    'date': data['date'],
                    'orderdate': data['order']['date'],
                    'orderid': data['order']['id'],
                    'formulaire': data['order']['formSlug'],
                    'email': data['payer']['email'],
                    'amount': amountCyclos,
                    'error': 'email not found'
                }
            listtransactions[data['id']] = tmp
    print ""
#print listtransactions
with open(cfg.ha['transactions'], 'w') as outfile:
    json.dump(listtransactions, outfile, indent=4, sort_keys=False, separators=(',', ':'))