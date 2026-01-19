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
from dateutil.relativedelta import relativedelta
import datetime
import config as cfg
import cyclos
from cyclos import Cyclos
from Odoo2Cyclos import Odoo2Cyclos

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

odooLogger = logging.getLogger('odoo')
odooLogger.setLevel(logging.DEBUG)
odooLogger.propagate = False
fileodooHandler = RotatingFileHandler("{0}/{1}.log".format(LOG_PATH, 'odoo'), maxBytes=2000000,
                                  backupCount=1500)
fileodooHandler.setFormatter(logFormatter)
odooLogger.addHandler(fileodooHandler)

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

    def get_old_chargebacks(self):
        with open(os.path.dirname(os.path.abspath(__file__))+'/'+cfg.mollie['chargebacks']) as data_file:
            listchargebacks = json.load(data_file)
        #print(listchargebacks)
        return listchargebacks

    def get_all_payments(self):
        list_payments = []
        headers = {'Content-type': 'application/json', 'Authorization': 'Bearer '+self.key}
        url = cfg.mollie['url']+'/payments?limit=150'
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
        list_payments = result['_embedded']['payments']
        while (result['_links']['next'] is not None):
            try:
                resp = requests.get(result['_links']['next']['href'], params=params, headers=headers)
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
            list_payments = list_payments + result['_embedded']['payments']
        #print(list_payments)
        return list_payments

    def get_all_chargebacks(self):
        list_chargebacks = []
        headers = {'Content-type': 'application/json', 'Authorization': 'Bearer '+self.key}
        url = cfg.mollie['url']+'/chargebacks?limit=150'
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
        list_chargebacks = result['_embedded']['chargebacks']
        while (result['_links']['next'] is not None):
            try:
                resp = requests.get(result['_links']['next']['href'], params=params, headers=headers)
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
            list_chargebacks = list_chargebacks + result['_embedded']['chargebacks']
            #print(len(list_chargebacks))
        return list_chargebacks

    def get_all_refunds(self):
        list_refunds = []
        headers = {'Content-type': 'application/json', 'Authorization': 'Bearer '+self.key}
        url = cfg.mollie['url']+'/refunds?limit=250'
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
        list_refunds = result['_embedded']['refunds']
        while (result['_links']['next'] is not None):
            try:
                resp = requests.get(result['_links']['next']['href'], params=params, headers=headers)
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
            list_refunds = list_refunds + result['_embedded']['refunds']
            #print(len(list_chargebacks))
        return list_refunds

    def get_payments(self, limit):
        list_payments = []
        headers = {'Content-type': 'application/json', 'Authorization': 'Bearer '+self.key}
        url = cfg.mollie['url']+'/payments?limit=150'
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
        list_payments = result['_embedded']['payments']
        while ((result['_links']['next'] is not None) and (len(list_payments) < limit)):
            try:
                resp = requests.get(result['_links']['next']['href'], params=params, headers=headers)
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
            list_payments = list_payments + result['_embedded']['payments']
            #print(len(list_payments))
        return list_payments

    def get_chargebacks(self, limit):
        list_chargebacks = []
        headers = {'Content-type': 'application/json', 'Authorization': 'Bearer '+self.key}
        url = cfg.mollie['url']+'/chargebacks?limit=150'
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
        list_chargebacks = result['_embedded']['chargebacks']
        while ((result['_links']['next'] is not None) and (len(list_chargebacks) < limit)):
            try:
                resp = requests.get(result['_links']['next']['href'], params=params, headers=headers)
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
            list_chargebacks = list_chargebacks + result['_embedded']['chargebacks']
            #print(len(list_chargebacks))
        return list_chargebacks

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
        msglog = LOG_HEADER + '[-] '
        listtransactions = self.get_old_payments()
        listchargebacks = self.get_old_chargebacks()
        payments = self.get_payments(500)
        chargebacks = self.get_chargebacks(500)
        for payment in payments:
            #paiementLogger.info(msglog + json.dumps(payment, indent=4, sort_keys=True))
            #self.display_json(payment)
            res = {}
            msglog = LOG_HEADER + '[-] '
            if (payment['id'] not in listtransactions):
                if 'paidAt' in payment:
                    changeCB = False
                    if (re.match("^Change CB.*", payment['description']) != None):
                        changeCB = True
                    if (((payment['description'] == "Change Florain") 
                    or changeCB)
                    and (payment['status'] == "paid")):
                        if ('amountChargedBack' in payment):
                            if (payment['amount']['value'] == payment['amountChargedBack']['value']):
                                #print(payment['amountChargedBack'])
                                continue
                            else:
                                amount = str(int(payment['amount']['value'])-int(payment['amountChargedBack']['value']))
                        else:
                            amount = payment['amount']['value']
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
                            'amount': amount
                        }
                        if 'customerId' in payment:
                            infoscustomer = self.get_user(payment['customerId'])
                            email = infoscustomer['email']
                        amount = payment['amount']['value']
                        accountID = cyclos.getIdFromEmail(email)
                        if (accountID == False):
                            paiementLogger.error(LOG_HEADER+"account cyclos not found "+email)
                            tmp['statusCyclos'] = "account cyclos not found "+email
                        #print(accountID)
                        if (self.simulate):
                            msglog += 'SIMULATE'
                        paiementLogger.info(msglog + ' PAIEMENT : id:'+ str(accountID)+' amount:'+str(amount)+' Mollie:'+str(payment['id'])+' to: '+email)
                        if ((not self.simulate) and (payment['mode'] != "test")):     
                            res = cyclos.setPaymentSystemtoUser(accountID, amount,"Transaction via Mollie Id : "+str(payment['id']))
                            #print(res)
                            res_object = json.loads(res.text)
                            #print(payment['amount']['value']+' '+payment['description']+' '+payment['paidAt']+' '+payment['method'])
                            if ('transactionNumber' in res_object):
                                tmp['transactionCyclos'] = res_object['transactionNumber']
                            else:
                                paiementLogger.error(LOG_HEADER+res.text)
                            listtransactions[payment['id']] = tmp
        
        for chargeback in chargebacks:
            res = {}
            if (chargeback['id'] not in listchargebacks):
                if (chargeback['paymentId'] in listtransactions):
                    for payment in payments:
                        if (payment['id'] == chargeback['paymentId']):
                            break
                    if payment['id'] in listtransactions:
                        tmp = {
                            'date': chargeback['createdAt'],
                            'id': chargeback['id'],
                            'description': chargeback['reason']['description'],
                            'code': chargeback['reason']['code'],
                            'amount': chargeback['amount']['value'],
                            'settlementAmount': chargeback['settlementAmount']['value']
                        }
                        if 'customerId' in payment:
                            infoscustomer = self.get_user(payment['customerId'])
                            email = infoscustomer['email']
                        amount = abs(float(chargeback['settlementAmount']['value']))
                        accountID = cyclos.getIdFromEmail(email)
                        if (accountID == False):
                            paiementLogger.error(LOG_HEADER+"account cyclos not found "+email)
                            tmp['statusCyclos'] = "account cyclos not found "+email
                        paiementLogger.info(msglog + ' PAIEMENT AFTER CHARGEBACK : id:'+ str(accountID)+' amount:'+str(amount)+' Mollie:'+str(chargeback['id'])+' to: '+email)
                        if ((not self.simulate) and (payment['mode'] != "test")):     
                            res = cyclos.setPaymentUsertoSystem(accountID, amount,"Transaction via Mollie Id : "+str(payment['id']))
                            res_object = json.loads(res.text)
                            if ('transactionNumber' in res_object):
                                tmp['transactionCyclos'] = res_object['transactionNumber']
                            else:
                                paiementLogger.error(LOG_HEADER+res.text)
                            listchargebacks[chargeback['id']] = tmp

        with open(os.path.dirname(os.path.abspath(__file__))+'/'+cfg.mollie['transactions'], 'w') as outfile:
            json.dump(listtransactions, outfile, indent=4, sort_keys=False, separators=(',', ':'))
        with open(os.path.dirname(os.path.abspath(__file__))+'/'+cfg.mollie['chargebacks'], 'w') as outfile:
            json.dump(listchargebacks, outfile, indent=4, sort_keys=False, separators=(',', ':'))

    def get_old_adhpayments(self):
        with open(os.path.dirname(os.path.abspath(__file__))+'/'+cfg.mollie['adhesions']) as data_file:
            listadhesions = json.load(data_file)
        #print(listadhesions)
        return listadhesions
    
    def get_old_adhesions_expired(self):
        with open(os.path.dirname(os.path.abspath(__file__))+'/'+cfg.mollie['adhesions_expired']) as data_file:
            listadhesions = json.load(data_file)
        #print(listadhesions)
        return listadhesions

    def checkPaiementAdhMollie(self, simulate):
        resultsAdhMensuelle={}
        resultsAdhAnnuelle={}
        payments = self.get_payments(500)
        for payment in payments:
            adhval = 0
            if (re.match('Adhésion Florain Mensuelle', payment['description']) is not None):
                if (payment['status'] == "paid"):
                    adhval=float(payment['amount']['value'])
                    infoscustomer = self.get_user(payment['customerId'])
                    if (infoscustomer['email'] not in resultsAdhMensuelle):
                        resultsAdhMensuelle[infoscustomer['email']] = {}
                        resultsAdhMensuelle[infoscustomer['email']]['date'] = payment['paidAt']
                        resultsAdhMensuelle[infoscustomer['email']]['amount'] = float(payment['amount']['value'])
                        resultsAdhMensuelle[infoscustomer['email']]['orderdate'] = payment['createdAt']
                        resultsAdhMensuelle[infoscustomer['email']]['paidAt'] = payment['paidAt']
                        resultsAdhMensuelle[infoscustomer['email']]['orderid'] = payment['id']
                        resultsAdhMensuelle[infoscustomer['email']]['state'] = payment['status']
                        resultsAdhMensuelle[infoscustomer['email']]['description'] = payment['description']
                        resultsAdhMensuelle[infoscustomer['email']]['method'] = payment['method']
                        #print(infoscustomer['email']+" "+str(adhval)+" "+payment['paidAt'])
            if (re.match('Adhésion Florain Annuelle', payment['description']) is not None):
                if (payment['status'] == "paid"):
                    adhval=float(payment['amount']['value'])
                    infoscustomer = self.get_user(payment['customerId'])
                    if (infoscustomer['email'] not in resultsAdhMensuelle):
                        resultsAdhAnnuelle[infoscustomer['email']] = {}
                        resultsAdhAnnuelle[infoscustomer['email']]['date'] = payment['paidAt']
                        resultsAdhAnnuelle[infoscustomer['email']]['amount'] = float(payment['amount']['value'])
                        resultsAdhAnnuelle[infoscustomer['email']]['orderdate'] = payment['createdAt']
                        resultsAdhAnnuelle[infoscustomer['email']]['paidAt'] = payment['paidAt']
                        resultsAdhAnnuelle[infoscustomer['email']]['orderid'] = payment['id']
                        resultsAdhAnnuelle[infoscustomer['email']]['state'] = payment['status']
                        resultsAdhAnnuelle[infoscustomer['email']]['description'] = payment['description']
                        resultsAdhAnnuelle[infoscustomer['email']]['method'] = payment['method']
                        #print(infoscustomer['email']+" "+str(adhval)+" "+payment['paidAt'])
        results={}
        results['AdhMensuelle'] = resultsAdhMensuelle
        results['AdhAnnuelle'] = resultsAdhAnnuelle
        #print(results['AdhAnnuelle'])
        return self.checkOdooAdhExpires(results, simulate)

    def checkOdooAdhExpires(self, resultsMollie, simulate):
        o2c = Odoo2Cyclos()
        listadhs = o2c.getOdooAdhs()
        listadhpayments=self.get_old_adhpayments()
        listadhexpired = self.get_old_adhesions_expired()
        datetoday = datetime.datetime.now()
        strtext=""
        for adh in listadhs:
            if (adh['account_cyclos'] == True):
                if ((adh['membership_stop'] is not None) and (adh['membership_stop'] != "none")):
                    m = re.search('(\d{2}\s+\w+\s+\d{4})', adh['membership_stop'])
                    if (m is not None):
                        dateadh = datetime.datetime.strptime(m.group(1), '%d %b %Y')
                        if (datetoday >= dateadh):
                            if (adh['email'] in resultsMollie['AdhMensuelle']):
                                date_format = '%Y-%m-%dT%H:%M:%S+00:00'
                                date_mollie = datetime.datetime.strptime(resultsMollie['AdhMensuelle'][adh['email']]['paidAt'], date_format)
                                date_adh_dec_1 = dateadh - relativedelta(months=1)
                                if (date_mollie > date_adh_dec_1):
                                    if (resultsMollie['AdhMensuelle'][adh['email']]['orderid'] not in listadhpayments):
                                        tmp = {
                                            'email': adh['email'],
                                            'date': resultsMollie['AdhMensuelle'][adh['email']]['date'],
                                            'orderdate': resultsMollie['AdhMensuelle'][adh['email']]['orderdate'],
                                            'orderid': resultsMollie['AdhMensuelle'][adh['email']]['orderid'],
                                            'state': resultsMollie['AdhMensuelle'][adh['email']]['state'],
                                            'description': resultsMollie['AdhMensuelle'][adh['email']]['description'],
                                            'method': resultsMollie['AdhMensuelle'][adh['email']]['method'],
                                            'amount': resultsMollie['AdhMensuelle'][adh['email']]['amount']
                                        }
                                        if (not simulate):
                                            tmp['simulate'] = False
                                            res = o2c.postOdooAdhMembership(adh['email'], adh['firstname']+" "+adh['lastname'], str(resultsMollie['AdhMensuelle'][adh['email']]['amount']))
                                            tmp['res'] = res
                                            if (res != 200):
                                                odooLogger.error(LOG_HEADER + '[-] postOdooAdhMembership AdhMensuelle '+adh['email']+' '+adh['firstname']+" "+str(resultsMollie['AdhMensuelle'][adh['email']]['amount']))
                                            else:
                                                strtext+='Ajout d\'une adhésion à '+adh['firstname']+' '+adh['lastname']+" - "+adh['email']+" d'un montant de "+str(resultsMollie['AdhMensuelle'][adh['email']]['amount'])+"\n"
                                        else:
                                            tmp['simulate'] = True
                                            strtext+='postOdooAdhMembership AdhMensuelle '+adh['email']+' '+adh['firstname']+" "+str(resultsMollie['AdhMensuelle'][adh['email']]['amount'])
                                            #print('postOdooAdhMembership AdhMensuelle '+adh['email']+' '+adh['firstname']+" "+str(resultsMollie['AdhMensuelle'][adh['email']]['amount']))
                                        odooLogger.info(LOG_HEADER + '[-] postOdooAdhMembership AdhMensuelle '+adh['email']+' '+adh['firstname']+" "+str(resultsMollie['AdhMensuelle'][adh['email']]['amount']))
                                        #print(adh['email']+" MENSUELLE "+resultsMollie['AdhMensuelle'][adh['email']]['date'])
                                        listadhpayments[resultsMollie['AdhMensuelle'][adh['email']]['orderid']] = tmp
                                else:
                                    if (adh['email'] not in listadhexpired):
                                        listadhexpired[adh['email']] = adh['lastname']+" "+adh['firstname']
                                    odooLogger.info(LOG_HEADER + '[-] Expired '+adh['email'])
                            elif (adh['email'] in resultsMollie['AdhAnnuelle']):
                                date_format = '%Y-%m-%dT%H:%M:%S+00:00'
                                date_mollie = datetime.datetime.strptime(resultsMollie['AdhAnnuelle'][adh['email']]['paidAt'], date_format)
                                date_adh_dec_1 = dateadh - relativedelta(months=1)
                                if (date_mollie > date_adh_dec_1):
                                    if (resultsMollie['AdhAnnuelle'][adh['email']]['orderid'] not in listadhpayments):
                                        tmp = {
                                            'email': adh['email'],
                                            'date': resultsMollie['AdhAnnuelle'][adh['email']]['date'],
                                            'orderdate': resultsMollie['AdhAnnuelle'][adh['email']]['orderdate'],
                                            'orderid': resultsMollie['AdhAnnuelle'][adh['email']]['orderid'],
                                            'state': resultsMollie['AdhAnnuelle'][adh['email']]['state'],
                                            'description': resultsMollie['AdhAnnuelle'][adh['email']]['description'],
                                            'method': resultsMollie['AdhAnnuelle'][adh['email']]['method'],
                                            'amount': resultsMollie['AdhAnnuelle'][adh['email']]['amount']
                                        }
                                        if (not simulate):
                                            tmp['simulate'] = False
                                            res = o2c.postOdooAdhMembership(adh['email'], adh['firstname']+" "+adh['lastname'], str(resultsMollie['AdhAnnuelle'][adh['email']]['amount']))
                                            tmp['res'] = res
                                            if (res != 200):
                                                odooLogger.error(LOG_HEADER + '[-] postOdooAdhMembership AdhAnnuelle '+adh['email']+' '+adh['firstname']+" "+str(resultsMollie['AdhAnnuelle'][adh['email']]['amount']))
                                            else:
                                                strtext+='Ajout d\'une adhésion à '+adh['firstname']+' '+adh['lastname']+" - "+adh['email']+" d'un montant de "+str(resultsMollie['AdhAnnuelle'][adh['email']]['amount'])+"\n"
                                        else:
                                            tmp['simulate'] = True
                                            strtext+='postOdooAdhMembership AdhAnnuelle '+adh['email']+' '+adh['firstname']+" "+str(resultsMollie['AdhAnnuelle'][adh['email']]['amount'])
                                            #print('postOdooAdhMembership AdhAnnuelle '+adh['email']+' '+adh['firstname']+" "+str(resultsMollie['AdhAnnuelle'][adh['email']]['amount']))
                                        odooLogger.info(LOG_HEADER + '[-] postOdooAdhMembership AdhAnnuelle '+adh['email']+' '+adh['firstname']+" "+str(resultsMollie['AdhAnnuelle'][adh['email']]['amount']))
                                        #print(adh['email']+" "+adh['firstname']+" "+adh['lastname']+" "+str(resultsMollie['AdhAnnuelle'][adh['email']]['amount'])+" ANNUELLE "+resultsMollie['AdhAnnuelle'][adh['email']]['date'])
                                        listadhpayments[resultsMollie['AdhAnnuelle'][adh['email']]['orderid']] = tmp
                                else:
                                    if (adh['email'] not in listadhexpired):
                                        listadhexpired[adh['email']] = adh['lastname']+" "+adh['firstname']
                                    odooLogger.info(LOG_HEADER + '[-] Expired '+adh['email'])
                            else:
                                if (adh['email'] not in listadhexpired):
                                    listadhexpired[adh['email']] = adh['lastname']+" "+adh['firstname']
                                odooLogger.info(LOG_HEADER + '[-] Expired '+adh['email'])
                        #else:
                            #if (adh['email'] in resultsMollie['AdhMensuelle']):
                            #    if (resultsMollie['AdhMensuelle'][adh['email']]['orderid'] not in listadhpayments):
                            #        print(adh['email']+" Add membership product supp")
                            #elif (adh['email'] in resultsMollie['AdhAnnuelle']):
                            #    if (resultsMollie['AdhAnnuelle'][adh['email']]['orderid'] not in listadhpayments):
                            #        print("ERROR : "+adh['email'])
        with open(os.path.dirname(os.path.abspath(__file__))+'/'+cfg.mollie['adhesions'], 'w') as outfile:
            json.dump(listadhpayments, outfile, indent=4, sort_keys=False, separators=(',', ':'))
        with open(os.path.dirname(os.path.abspath(__file__))+'/'+cfg.mollie['adhesions_expired'], 'w') as outfile:
            json.dump(listadhexpired, outfile, indent=4, sort_keys=False, separators=(',', ':'))    
        return strtext

    def display_json(self, arr):
        print(json.dumps(arr, indent=4, sort_keys=True))

"""     def get_old_adhesions(self):
        with open(os.path.dirname(os.path.abspath(__file__))+'/'+cfg.mollie['adhesions']) as data_file:
            listadhesions = json.load(data_file)
        return listadhesions

    def checkAdhesion(self):
        o2c = Odoo2Cyclos()
        listadhesions = self.get_old_adhesions()
        #print(listadhesions)
        payments = self.get_payments(50)
        for payment in payments:
            res = {}
            if (payment['id'] not in listadhesions):
                if (re.match("^Adhésion Florain Mensuelle", payment['description']) != None):
                    if 'paidAt' in payment:
                        infoscustomer = self.get_user(payment['customerId'])
                        listadhs = o2c.getOdooAdhs()
                        for adh in listadhs:
                            if (adh['email'] == infoscustomer['email']):
                                if ((adh['membership_state'] != "paid") and 
                                (adh['membership_state'] != "waiting") and 
                                (adh['membership_state'] != "invoiced")):
                                    print(infoscustomer['email'])
                                    print(payment['details']['consumerName'])
                                    tmp = {
                                        'date': payment['paidAt'],
                                        'orderid': payment['id'],
                                        'email': infoscustomer['email'],
                                        'name': payment['details']['consumerName'],
                                        'state': payment['status'],
                                        'description': payment['description'],
                                        'method': payment['method'],
                                        'amount': payment['amount']['value']
                                    }
                                    #o2c.postOdooAdhMembership(infoscustomer['email'], payment['details']['consumerName'], payment['amount']['value'])
                                    listadhesions[payment['id']] = tmp
                                break
                if (re.match("^Adhésion Florain Annuelle", payment['description']) != None):
                    if 'paidAt' in payment:
                        infoscustomer = self.get_user(payment['customerId'])
                        listadhs = o2c.getOdooAdhs()
                        for adh in listadhs:
                            if (adh['email'] == infoscustomer['email']):
                                if ((adh['membership_state'] != "paid") and 
                                (adh['membership_state'] != "waiting") and 
                                (adh['membership_state'] != "invoiced")):
                                    print(infoscustomer['email'])
                                    print(payment['details']['consumerName'])
                                    tmp = {
                                        'date': payment['paidAt'],
                                        'orderid': payment['id'],
                                        'email': infoscustomer['email'],
                                        'name': payment['details']['consumerName'],
                                        'state': payment['status'],
                                        'description': payment['description'],
                                        'method': payment['method'],
                                        'amount': payment['amount']['value']
                                    }
                                    #o2c.postOdooAdhMembership(infoscustomer['email'], payment['details']['consumerName'], payment['amount']['value'])
                                    listadhesions[payment['id']] = tmp
                                break

        with open(os.path.dirname(os.path.abspath(__file__))+'/'+cfg.mollie['adhesions'], 'w') as outfile:
            json.dump(listadhesions, outfile, indent=4, sort_keys=False, separators=(',', ':')) """