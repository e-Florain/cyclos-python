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

cyclos = Cyclos()
with open(cfg.ha['transactions']) as data_file:
	listtransactions = json.load(data_file)

now = datetime.now()
last_hour_date_time = datetime.now() - timedelta(days = 2)
url = cfg.ha['url']+'?from='+last_hour_date_time.strftime("%Y-%m-%dT%H:%M:%S")
params = {'results_per_page': 1000}
r = requests.get(cfg.ha['url'], auth=(cfg.ha['user'], cfg.ha['password']), params=params)
result = json.loads(r.text)
if 'resources' in result:
    resources = result['resources']

for resource in resources:
    if (re.match('.*paiements.*', resource['url_receipt'])):
        if (resource['id'] not in listtransactions):
            print resource['id']+" "+resource['payer_email'].encode('utf-8')+" "+str(resource['amount'])
            accountID = cyclos.getIdFromEmail(resource['payer_email'])
            res = cyclos.setPaymentSystemtoUser(accountID, resource['amount'],"Transaction via HelloAsso Id : "+resource['id'])
            tmp = {resource['date'] : res['transactionNumber']}
            listtransactions[resource['id']] = tmp
        
print listtransactions
with open(cfg.ha['transactions'], 'w') as outfile:
    json.dump(listtransactions, outfile, indent=4, sort_keys=False, separators=(',', ':'))
