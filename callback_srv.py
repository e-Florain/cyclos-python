#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import logging
import os
import re
import time
import json
from logging.handlers import RotatingFileHandler
import threading  # launch server in a thread
import requests  # make http request to shutdown web server
from flask import Flask
from flask import request
import time, signal
from cherrypy import wsgiserver
from filelock import FileLock
from mollie import Mollie
from cyclos import Cyclos
from Odoo2Cyclos import Odoo2Cyclos

LOG_HEADER = " [" + __file__ + "] - "
p = re.compile("\w+(\d)")
LOG_PATH = os.path.dirname(os.path.abspath(__file__)) + '/log/'
logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
webLogger = logging.getLogger('callback_srv')
webLogger.setLevel(logging.DEBUG)
webLogger.propagate = False
fileHandler = RotatingFileHandler("{0}/{1}.log".format(LOG_PATH, 'callback_srv'), maxBytes=2000000,
                                  backupCount=1500)
fileHandler.setFormatter(logFormatter)
webLogger.addHandler(fileHandler)

app = Flask(__name__)
mo = Mollie()
cyclos = Cyclos()
o2c = Odoo2Cyclos()

def checkBalancesCyclos(cyclos):
    #info = cyclos.getBalances()
    #pprint(info['accountTypes'])
    total = 0
    info = cyclos.getUserBalancesSummary("user")
    total = total+float(info['total']['sum'])
    info = cyclos.getUserBalancesSummary("comptePro")
    total = total+float(info['total']['sum'])
    info = cyclos.getUserBalancesSummary("system")
    #print(total)
    info = cyclos.getAccount('system')
    totalinv = info[0]['status']['balance']

    #get payments system
    listpayments = cyclos.getTransactions('system')
    #print(listpayments)
    totalreconversion = 0
    for payment in listpayments:
        # Reconversion papiers vers numérique
        if (payment['type']['internalName'] == 'debit.toPro'):
            if (payment['related']['user']['display'] != 'Le Florain'):
                totalreconversion = totalreconversion +float(payment['amount'])
        # Reconversion numérique vers euros
        if (payment['type']['internalName'] == 'comptePro.toDebit'):
            totalreconversion = totalreconversion + float(payment['amount'])
    sold = float(totalinv)+float(total)
    if (sold != 0):
        webLogger.info(LOG_HEADER + '[checkBalancesCyclos] ERREUR CRITIQUE '+str(total)+' '+str(totalinv))
        #webLogger.info(LOG_HEADER + '[/monitor] GET')
        #print("Total des soldes des comptes : "+str(total))
        #print("Solde du compte de débit : "+str(totalinv))
    totalinv = float(totalinv) - totalreconversion
    return float(totalinv)

def checkPaimentsMollie(mollie):
    total=0
    list_payments = mollie.get_payments(500)
    for payment in list_payments:
        if (re.match('Change', payment['description']) is not None):
            if (payment['status'] == "paid"):
                total=total+float(payment['amount']['value'])
    #print("Total Change via Mollie :"
    return total

@app.route('/')
def getPaiements():
    webLogger.info(LOG_HEADER + '[/] GET')
    with FileLock(os.path.dirname(os.path.abspath(__file__)) + "/myfile.txt"):
        #time.sleep(20000)
        mo.setTransactionstoCyclos()
        return '200'

@app.route('/', methods=['POST'])
def postPaiements():
    webLogger.info(LOG_HEADER + '[/] POST')
    with FileLock(os.path.dirname(os.path.abspath(__file__)) + "/myfile.txt"):
        mo.setTransactionstoCyclos()
        return '200'

@app.route('/paiement', methods=['POST'])
def paiement():
    webLogger.info(LOG_HEADER + '[/paiement] POST')
    data = request.form.to_dict()
    #print(data, request, type(request))
    with FileLock(os.path.dirname(os.path.abspath(__file__)) + "/myfile.txt"):
        mo.setTransactionstoCyclos()
        return '200'

@app.route('/allow/<string:argkey>')
def changeCyclos(argkey):
    with FileLock(os.path.dirname(os.path.abspath(__file__)) + "/myfile2.txt"):
        newarr = {}
        webLogger.info(LOG_HEADER + '[/allow/'+argkey+'] GET')
        with open(os.path.dirname(os.path.abspath(__file__))+"/url.key") as keysjsons:
            arr = json.loads(keysjsons.read())
            for key, value in arr.items():
                #print(key+" "+value)
                if (argkey == key):
                    if (re.match('\d{8}-\d{6}-adhpros-changes\.json', value) is not None):
                        webLogger.info(LOG_HEADER + 'o2c apply adhpros '+value)
                        o2c.applyChangesAdhPros(value)
                    else:
                        webLogger.info(LOG_HEADER + 'o2c apply adhs '+value)
                        o2c.applyChangesAdhs(value)
                else:
                    newarr[key] = value
            with open(os.path.dirname(os.path.abspath(__file__))+'/url.key', 'w') as outfile:
                json.dump(newarr, outfile, indent=4, sort_keys=False, separators=(',', ':'))
            return "200"
    return "503"

@app.route('/monitor')
def monitor():
    webLogger.info(LOG_HEADER + '[/monitor] GET')
    totalCyclos = checkBalancesCyclos(cyclos)
    totolMollie = checkPaimentsMollie(mo)
    if (abs(totalCyclos) == abs(totolMollie)):
        return ("OK")
    else:
        diff = abs(totalCyclos)-abs(totolMollie)
        return ("ERREUR : "+str(diff))

d = wsgiserver.WSGIPathInfoDispatcher({'/': app})
server = wsgiserver.CherryPyWSGIServer(('0.0.0.0', 80), d)

if __name__ == '__main__':
    try:
        webLogger.info(LOG_HEADER + '[starting server]')
        server.start()
    except KeyboardInterrupt:
        webLogger.info(LOG_HEADER + '[stopping server]')
        server.stop()
