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
paiementLogger = logging.getLogger('mollie')
paiementLogger.setLevel(logging.DEBUG)
paiementLogger.propagate = False
fileHandler = RotatingFileHandler("{0}/{1}.log".format(LOG_PATH, 'mollie'), maxBytes=2000000,
                                  backupCount=1500)
fileHandler.setFormatter(logFormatter)
paiementLogger.addHandler(fileHandler)

class Mollie:

    def __init__(self, simulate=False):
        requests.packages.urllib3.disable_warnings()
        self.key = cfg.mollie['key']
        self.url = cfg.mollie['url']
        self.debug = cfg.mollie['debug']
        self.simulate = simulate
        requests.packages.urllib3.disable_warnings()

    def get_old_payments(self):
        with open(os.path.dirname(os.path.abspath(__file__))+'/'+cfg.mollie['transactions']) as data_file:
            listtransactions = json.load(data_file)
        #print(listtransactions)
        return listtransactions

    def get_payments(self):
        headers = {'Content-type': 'application/json', 'Authorization': 'Bearer '+self.key}
        url = cfg.mollie['url']+'/payments'
        params = {}
        try:
            resp = requests.get(url, params=params, headers=headers)
        except requests.exceptions.Timeout:
            paiementLogger.error(LOG_HEADER + '[-] Timeout')
        except requests.exceptions.TooManyRedirects:
            paiementLogger.error(LOG_HEADER + '[-] TooManyRedirects')
        except requests.exceptions.RequestException as e:
            paiementLogger.error(LOG_HEADER + '[-] Exception')
            raise SystemExit(e)
        if (resp.status_code != 200):
            paiementLogger.error(LOG_HEADER + '[-] status not 200 Mollie')
            exit
        result = json.loads(resp.text)
        return result['_embedded']['payments']

    def get_users(self):
        headers = {'Content-type': 'application/json', 'Authorization': 'Bearer '+self.key}
        url = cfg.mollie['url']+'/customers'
        params = {}
        try:
            resp = requests.get(url, params=params, headers=headers)
        except requests.exceptions.Timeout:
            paiementLogger.error(LOG_HEADER + '[-] Timeout')
        except requests.exceptions.TooManyRedirects:
            paiementLogger.error(LOG_HEADER + '[-] TooManyRedirects')
        except requests.exceptions.RequestException as e:
            paiementLogger.error(LOG_HEADER + '[-] Exception')
            raise SystemExit(e)
        if (resp.status_code != 200):
            paiementLogger.error(LOG_HEADER + '[-] status not 200 Mollie')
            exit
        result = json.loads(resp.text)
        #self.display_json(result['_embedded']['customers'])
        return result['_embedded']['customers']

    def get_user(self, id):
        headers = {'Content-type': 'application/json', 'Authorization': 'Bearer '+self.key}
        url = cfg.mollie['url']+'/customers/'+id
        params = {}
        try:
            resp = requests.get(url, params=params, headers=headers)
        except requests.exceptions.Timeout:
            paiementLogger.error(LOG_HEADER + '[-] Timeout')
        except requests.exceptions.TooManyRedirects:
            paiementLogger.error(LOG_HEADER + '[-] TooManyRedirects')
        except requests.exceptions.RequestException as e:
            paiementLogger.error(LOG_HEADER + '[-] Exception')
            raise SystemExit(e)
        if (resp.status_code != 200):
            paiementLogger.error(LOG_HEADER + '[-] status not 200 Mollie')
            exit
        result = json.loads(resp.text)
        #self.display_json(result)
        return result

    def setTransactionstoCyclos(self):
        cyclos = Cyclos()
        listtransactions = self.get_old_payments()
        payments = self.get_payments()
        for payment in payments:
            #self.display_json(payment)
            res = {}
            if (payment['id'] not in listtransactions):
                if 'paidAt' in payment:
                    if ((payment['description'] == "Change Florain") and (payment['status'] == "paid")):
                        tmp = {
                            'date': payment['paidAt'],
                            'orderdate': payment['createdAt'],
                            'orderid': payment['id'],
                            #'transactionCyclos' : res_object['transactionNumber'],
                            #'formulaire': data['order']['formSlug'],
                            #'email': data['payer']['email'],
                            #'client': payment['details']['consumerName'],
                            'state': payment['status'],
                            #'paymentMeans': data['paymentMeans'],
                            'description': payment['description'],
                            'method': payment['method'],
                            'amount': payment['amount']['value']
                        }
                        if 'customerId' in payment:
                            infoscustomer = self.get_user(payment['customerId'])
                            email = infoscustomer['email']
                        amount = payment['amount']['value']
                        accountID = cyclos.getIdFromEmail(email)
                        if (accountID == False):
                            paiementLogger.error(LOG_HEADER+"account cyclos not found")
                            return
                        print(accountID)
                        msglog = LOG_HEADER + '[-] '
                        if (self.simulate):
                            msglog += 'SIMULATE'
                        paiementLogger.info(msglog + ' PAIEMENT : id:'+ accountID+' amount:'+str(amount)+' Mollie:'+str(payment['id'])+' to: '+email)
                        #if ((not self.simulate) and (payment['mode'] != "test")):     
                            #res = cyclos.setPaymentSystemtoUser(accountID, amount,"Transaction via Mollie Id : "+str(payment['id']))
                            #print(res)
                            #res_object = json.loads(res.text)
                        #print(payment['amount']['value']+' '+payment['description']+' '+payment['paidAt']+' '+payment['method'])
   
                        listtransactions[payment['id']] = tmp

        with open(os.path.dirname(os.path.abspath(__file__))+'/'+cfg.mollie['transactions'], 'w') as outfile:
            json.dump(listtransactions, outfile, indent=4, sort_keys=False, separators=(',', ':'))


    def display_json(self, arr):
        print(json.dumps(arr, indent=4, sort_keys=True))