#!/usr/bin/python3
# -*- coding: utf-8 -*-
import cyclos
import re
import json
from datetime import date
import datetime
from dateutil.relativedelta import relativedelta
import config as cfg
from cyclos import Cyclos
from mollie import Mollie
from Odoo2Cyclos import Odoo2Cyclos
from pprint import pprint
import requests

debug=False

def get_old_payments(self):
    with open(os.path.dirname(os.path.abspath(__file__))+'/'+cfg.mollie['adhtransactions']) as data_file:
        listadhtransactions = json.load(data_file)
    return listadhtransactions

def checkPaimentsMollie(mollie):
    resultsAdhMensuelle={}
    resultsAdhAnnuelle={}
    payments = mollie.get_payments(500)
    for payment in payments:
        adhval = 0
        if (re.match('Adhésion Florain Mensuelle', payment['description']) is not None):
            if (payment['status'] == "paid"):
                adhval=float(payment['amount']['value'])
                infoscustomer = mollie.get_user(payment['customerId'])
                if (infoscustomer['email'] not in resultsAdhMensuelle):
                    resultsAdhMensuelle[infoscustomer['email']] = {}
                    resultsAdhMensuelle[infoscustomer['email']]['paidAt'] = payment['paidAt']
                    resultsAdhMensuelle[infoscustomer['email']]['amount'] = adhval
                #print(infoscustomer['email']+" "+str(adhval)+" "+payment['paidAt'])
        if (re.match('Adhésion Florain Annuelle', payment['description']) is not None):
            if (payment['status'] == "paid"):
                adhval=float(payment['amount']['value'])
                infoscustomer = mollie.get_user(payment['customerId'])
                if (infoscustomer['email'] not in resultsAdhAnnuelle):
                    resultsAdhAnnuelle[infoscustomer['email']] = {}
                    resultsAdhAnnuelle[infoscustomer['email']]['paidAt'] = payment['paidAt']
                    resultsAdhAnnuelle[infoscustomer['email']]['amount'] = adhval
                #print(infoscustomer['email']+" "+str(adhval)+" "+payment['paidAt'])
    results={}
    results['AdhMensuelle'] = resultsAdhMensuelle
    results['AdhAnnuelle'] = resultsAdhAnnuelle
    return results
    #strmsg+="Total Change via Mollie :"+str(total)+"\n"
    #return total

def checkOdooAdhExpires(listadhs, resultsMollie):
    datetoday = datetime.datetime.now()
    for adh in listadhs:
        #print(adh)
        if (adh['account_cyclos'] == True):
            if ((adh['membership_stop'] is not None) and (adh['membership_stop'] != "none")):
                m = re.search('(\d{2}\s+\w+\s+\d{4})', adh['membership_stop'])
                if (m is not None):
                    dateadh = datetime.datetime.strptime(m.group(1), '%d %b %Y')
                    if (datetoday >= dateadh):
                        #print(dateadh.isoformat())
                        #print(adh['email'])
                        if (adh['email'] in resultsMollie['AdhMensuelle']):
                            print(adh['email']+" MENSUELLE "+resultsMollie['AdhMensuelle'][adh['email']]['paidAt']+" "+adh['membership_stop'])
                            #date_str_prlevmt = '2023-02-28 14:30:00'
                            #date_str_mollie = '2023-08-22T22:54:23+00:00'
                            date_str_mollie = resultsMollie['AdhMensuelle'][adh['email']]['paidAt']
                            date_format = '%Y-%m-%dT%H:%M:%S+00:00'
                            date_obj_mollie = datetime.datetime.strptime(date_str_mollie, date_format)
                            date_str_odoo = adh['membership_stop']
                            date_format2 = '%a, %d %b %Y %H:%M:%S %Z'
                            date_obj_odoo = datetime.datetime.strptime(date_str_odoo, date_format2)
                            #print(date_obj_mollie)
                            #print(date_obj_odoo)
                            date_obj_mollie_dec_1 = date_obj_odoo - relativedelta(months=1)
                            #print(date_obj_mollie_dec_1)
                            if (date_obj_mollie > date_obj_mollie_dec_1):
                                print("Add membership "+adh['email']+" "+adh['firstname']+" "+adh['lastname']+" "+str(resultsMollie['AdhMensuelle'][adh['email']]['amount']))
                                if not debug:
                                    res = o2c.postOdooAdhMembership(adh['email'], adh['firstname']+" "+adh['lastname'], str(resultsMollie['AdhMensuelle'][adh['email']]['amount']))
                                    print(res)
                        elif (adh['email'] in resultsMollie['AdhAnnuelle']):
                            print(adh['email']+" ANNUELLE "+resultsMollie['AdhAnnuelle'][adh['email']]['paidAt']+" "+adh['membership_stop'])
                        else:
                            print(adh['email']+" NONE")

def display_json(self, arr):
        print(json.dumps(arr, indent=4, sort_keys=True))

o2c = Odoo2Cyclos()
listadhs = o2c.getOdooAdhs()
mo = Mollie()
resultsMollie = checkPaimentsMollie(mo)
#print(resultsMollie)
checkOdooAdhExpires(listadhs, resultsMollie)


#for adh in listadhs:
#    if (adh['account_cyclos']):
#        print(adh['email'])
#        print(adh['membership_stop'])
#        print(adh['membership_state'])
