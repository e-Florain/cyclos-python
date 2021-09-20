#!/usr/bin/python3
# -*- coding: utf-8 -*-
import requests
import logging
import json
import re
import os
from logging.handlers import RotatingFileHandler
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta
import config as cfg
import cyclos
from cyclos import Cyclos

LOG_HEADER = " [" + __file__ + "] - "
LOG_PATH = os.path.dirname(os.path.abspath(__file__)) + '/log/'
logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
paiementLogger = logging.getLogger('paiement')
paiementLogger.setLevel(logging.DEBUG)
paiementLogger.propagate = False
fileHandler = RotatingFileHandler("{0}/{1}.log".format(LOG_PATH, 'paiement'), maxBytes=2000000,
                                  backupCount=1500)
fileHandler.setFormatter(logFormatter)
paiementLogger.addHandler(fileHandler)

class HelloAsso:

    def __init__(self, simulate=False):
        requests.packages.urllib3.disable_warnings()
        self.user = cfg.ha['user']
        self.password = cfg.ha['password']
        self.debug = cfg.ha['debug']
        self.simulate = simulate
        requests.packages.urllib3.disable_warnings()
        self.getToken()

    def getToken(self):
        url = 'https://api.helloasso.com/oauth2/token'
        headers = {'Content-type': 'application/x-www-form-urlencoded', 'Accept': 'text/plain'}
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.user,
            'client_secret': self.password
        }
        resp = requests.post(url, verify=False, data=data, headers=headers)
        result = json.loads(resp.text)
        token = result['access_token']
        self.token = token

    def displayJson(self, json_text):
        json_object = json.loads(json_text)
        json_formatted_str = json.dumps(json_object, indent=2)
        print(json_formatted_str)

    def setTransactionstoCyclos(self):
        cyclos = Cyclos()
        with open(cfg.ha['transactions']) as data_file:
            listtransactions = json.load(data_file)
        now = datetime.now()
        last_hour_date_time = datetime.now() - timedelta(days = 2)
        #url = cfg.ha['url']+'?from='+last_hour_date_time.strftime("%Y-%m-%dT%H:%M:%S")
        #url = 'https://api.helloasso.com/v5/organizations/le-florain'
        #params = {}
        #headers = {'Content-type': 'application/json', 'Authorization': 'Bearer '+token}
        #resp = requests.get(url, params=params, headers=headers)
        now = datetime.now()
        last_hour_date_time = datetime.now() - timedelta(days = 90)
        #url = cfg.ha['url']+'?from='+last_hour_date_time.strftime("%Y-%m-%dT%H:%M:%S")
        url = cfg.ha['url']+'/payments'+'?pageSize=100&from='+last_hour_date_time.strftime("%Y-%m-%dT%H:%M:%S")
        params = {}
        headers = {'Content-type': 'application/json', 'Authorization': 'Bearer '+self.token}
        try:
            resp = requests.get(url, params=params, headers=headers)
        except requests.exceptions.Timeout:
            paiementLogger.error(LOG_HEADER + '[-] Timeout')
        except requests.exceptions.TooManyRedirects:
            paiementLogger.error(LOG_HEADER + '[-] TooManyRedirects')
        except requests.exceptions.RequestException as e:
            paiementLogger.error(LOG_HEADER + '[-] Exception')
            raise SystemExit(e)
        if (resp.status_code != "200"):
            paiementLogger.error(LOG_HEADER + '[-] status not 200 HelloAsso')
            exit
        result = json.loads(resp.text)
        if 'data' not in result:
            print (result)
            exit
        for data in result['data']:
            #print data['order']['id']
            #print listtransactions
            #print data['order']['id'] not in listtransactions
            paiementLogger.info(LOG_HEADER + '[-] '+str(data))
            if (str(data['id']) not in listtransactions):
                if ((data['order']['formSlug'] == 'change-florain-numerique-credit-unitaire') or
                    (data['order']['formSlug'] == 'test-change-florain-numerique-credit-mensuel')):
                    #for item in data['items']:
                    #    amount = item['amount']
                    amount = data['amount']
                    accountID = cyclos.getIdFromEmail(data['payer']['email'])
                    amountCyclos = amount/100
                    res = {}
                    if (accountID != False):
                        if (data['state'] == "Authorized"):
                            paiementLogger.info('')
                            msglog = LOG_HEADER + '[-] '
                            if (self.simulate):
                                msglog += 'SIMULATE'
                            paiementLogger.info(msglog + ' PAIEMENT : id:'+ accountID+' amount:'+str(amountCyclos)+' helloassoid:'+str(data['order']['id']))
                            if (not self.simulate):     
                                res = cyclos.setPaymentSystemtoUser(accountID, amountCyclos,"Transaction via HelloAsso Id : "+str(data['order']['id']))
                                #print(res)
                                res_object = json.loads(res.text)
                                #print(res_object['transactionNumber'])
		   #res = {}
                    #res['transactionNumber']="XXX"
                                if ('transactionNumber' in res_object):
                                    tmp = {
                                        'date': data['date'],
                                        'orderdate': data['order']['date'],
                                        'orderid': data['order']['id'],
                                        'transactionCyclos' : res_object['transactionNumber'],
                                        'formulaire': data['order']['formSlug'],
                                        'email': data['payer']['email'],
                                        'state': data['state'],
                                        'paymentMeans': data['paymentMeans'],
                                        'amount': amountCyclos
                                    }
                                else:
                                    if ('text' in res):
                                        paiementLogger.error(LOG_HEADER + '[-] '+(res.text).encode('utf-8'))
                                    else:
                                        paiementLogger.error(LOG_HEADER + '[-] '+str(res))
                                    tmp = {
                                        'date': data['date'],
                                        'orderdate': data['order']['date'],
                                        'orderid': data['order']['id'],
                                        'transactionCyclos' : 'None',
                                        'formulaire': data['order']['formSlug'],
                                        'email': data['payer']['email'],
                                        'state': data['state'],
                                        'paymentMeans': data['paymentMeans'],
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
                                'state': data['state'],
                                'paymentMeans': data['paymentMeans'],
                                'error': 'paiement not Authorized'
                            }
                    else:
                        tmp = {
                            'date': data['date'],
                            'orderdate': data['order']['date'],
                            'orderid': data['order']['id'],
                            'formulaire': data['order']['formSlug'],
                            'email': data['payer']['email'],
                            'amount': amountCyclos,
                            'state': data['state'],
                            'paymentMeans': data['paymentMeans'],
                            'error': 'email not found'
                        }
                    listtransactions[data['id']] = tmp
            print ("")
        #print listtransactions
        with open(cfg.ha['transactions'], 'w') as outfile:
            json.dump(listtransactions, outfile, indent=4, sort_keys=False, separators=(',', ':'))
