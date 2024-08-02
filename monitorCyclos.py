#!/usr/bin/python3
# -*- coding: utf-8 -*-
import cyclos
import re
import logging
import json
import os
from cyclos import Cyclos
from mollie import Mollie
from pprint import pprint
import smtplib
from logging.handlers import RotatingFileHandler
from email.message import EmailMessage
import config as cfg

LOG_HEADER = " [" + __file__ + "] - "
LOG_PATH = os.path.dirname(os.path.abspath(__file__)) + '/log/'
logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
monitorLogger = logging.getLogger('monitor')
monitorLogger.setLevel(logging.DEBUG)
monitorLogger.propagate = False
fileHandler = RotatingFileHandler("{0}/{1}.log".format(LOG_PATH, 'monitor'), maxBytes=2000000,
                                  backupCount=1500)
fileHandler.setFormatter(logFormatter)
monitorLogger.addHandler(fileHandler)

def get_ignore_payments():
        with open(os.path.dirname(os.path.abspath(__file__))+'/'+cfg.cyclos['ignorePayments']) as data_file:
            listignorepayments = json.load(data_file)
        #print(listignorepayments)
        return listignorepayments

def checkBalancesCyclos(cyclos, strmsg):
    #info = cyclos.getBalances()
    #pprint(info['accountTypes'])
    listignorepayments = get_ignore_payments()
    total = 0
    info = cyclos.getUserBalancesSummary("user")
    total = total+float(info['total']['sum'])
    info = cyclos.getUserBalancesSummary("comptePro")
    total = total+float(info['total']['sum'])
    info = cyclos.getUserBalancesSummary("system")
    #print(total)
    info = cyclos.getAccount('system')
    totalinv = float(info[0]['status']['balance'])
    #get payments system
    listpayments = cyclos.getTransactions('system')
    #print(listpayments)
    totalreconversion = 0
    #totalchange = 0
    #totalchange2 = 0
    #nbchange = 0
    #for payment in listpayments:
    #    if (payment['type']['internalName'] == 'debit.toUser'):
    #        totalchange2+=float(payment['amount'])
        #if (re.match('Transaction via Mollie Id', payment['description']) is not None):
        #    totalchange+=float(payment['amount'])
        #    nbchange+=1
    #print(totalchange)
    #print(nbchange)
    #print(totalchange2)

    for payment in listpayments:
        # Reconversion papiers vers numérique
        if (payment['type']['internalName'] == 'debit.toPro'):
            if (payment['transactionNumber'] not in listignorepayments):
                totalreconversion = totalreconversion + float(payment['amount'])
        # Reconversion numérique vers euros
        if (payment['type']['internalName'] == 'comptePro.toDebit'):
            if (payment['transactionNumber'] not in listignorepayments):
                totalreconversion = totalreconversion + float(payment['amount'])
    sold = float(totalinv)+float(total)
    if (sold != 0):
        strmsg+="ERREUR CRITIQUE"+"\n"
        strmsg+="Total des soldes des comptes : "+str(total)+"\n"
        strmsg+="Solde du compte de débit : "+str(totalinv)+"\n"
    else:
        strmsg+="Total des soldes des comptes : "+str(total)+"\n"
        strmsg+="Solde du compte de débit : "+str(totalinv)+"\n"
    
    # On enlève 140 du remboursement de mortimer dubois
    # On enlève les paiements ignorés
    totalignorepayment = 0
    for key in listignorepayments.keys():
        if (listignorepayments[key]['type'] == 'toUser'):
            for payment in listpayments:
                if (payment['transactionNumber'] == key):
                    totalignorepayment = totalignorepayment + float(payment['amount'])
    totalinv = float(totalinv) - totalreconversion - totalignorepayment
    strmsg+="Total reconversion "+str(float(totalreconversion))+"\n"
    strmsg+="Total change dans Cyclos "+str(float(totalinv))+"\n"
    return float(totalinv),strmsg

def checkPaimentsMollie(mollie, strmsg):
    total=0
    list_payments = mollie.get_all_payments()
    list_chargebacks = mollie.get_all_chargebacks()
    list_refunds = mollie.get_all_refunds()
    for payment in list_payments:
        if (re.match('Change', payment['description']) is not None):
            if (payment['status'] == "paid"):
                total=total+float(payment['amount']['value'])
    for chargeback in list_chargebacks:
        for payment in list_payments:
            if (payment['id'] == chargeback['paymentId']):
                if (re.match('Change', payment['description']) is not None):
                    total = total-float(payment['amount']['value'])
    for refund in list_refunds:
        for payment in list_payments:
            if (payment['id'] == chargeback['paymentId']):
                if (re.match('Change', payment['description']) is not None):
                    total = total-float(payment['amount']['value'])
    strmsg+="Total Change via Mollie :"+str(total)+"\n"
    return total,strmsg

smtp = cfg.smtp['ip']
msg = EmailMessage()
cyclos = Cyclos()
strmsg = ""
totalCyclos, strmsg = checkBalancesCyclos(cyclos, strmsg)
mo = Mollie()
totalMollie, strmsg = checkPaimentsMollie(mo, strmsg)
monitorLogger.info(LOG_HEADER + '[-] '+strmsg)
if (abs(totalCyclos) != abs(totalMollie)):
    diff = abs(totalCyclos)-abs(totalMollie)
    strmsg+="ERREUR - Différence de "+str(diff)
    msg.set_content(strmsg)
    print(strmsg)
    msg['Subject'] = f'ATTENTION Erreur de balance'
    msg['From'] = "no-reply@eflorain.fr"
    msg['To'] = "tech@florain.fr"
    #msg['To'] = "groche@guigeek.org"
    #print(strmsg)
    if (strmsg != ""):
        s = smtplib.SMTP(smtp)
        s.send_message(msg)
        s.quit()
