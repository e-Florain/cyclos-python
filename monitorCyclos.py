#!/usr/bin/python3
# -*- coding: utf-8 -*-
import cyclos
import re
from cyclos import Cyclos
from mollie import Mollie
from pprint import pprint
import smtplib
from email.message import EmailMessage
import config as cfg


def checkBalancesCyclos(cyclos, strmsg):
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
                totalreconversion = totalreconversion + float(payment['amount'])
	# Reconversion numérique vers euros
        if (payment['type']['internalName'] == 'comptePro.toDebit'):
            totalreconversion = totalreconversion + float(payment['amount'])
    #print(totalreconversion)
    sold = float(totalinv)+float(total)
    if (sold != 0):
        strmsg+="ERREUR CRITIQUE"+"\n"
        strmsg+="Total des soldes des comptes : "+str(total)+"\n"
        strmsg+="Solde du compte de débit : "+str(totalinv)+"\n"
    else:
        strmsg+="Total des soldes des comptes : "+str(total)+"\n"
        strmsg+="Solde du compte de débit : "+str(totalinv)+"\n"
    totalinv = float(totalinv) - totalreconversion
    return float(totalinv),strmsg

def checkPaimentsMollie(mollie, strmsg):
    total=0
    list_payments = mollie.get_all_payments()
    for payment in list_payments:
        if (re.match('Change', payment['description']) is not None):
            if (payment['status'] == "paid"):
                total=total+float(payment['amount']['value'])
    strmsg+="Total Change via Mollie :"+str(total)+"\n"
    return total,strmsg

smtp = cfg.smtp['ip']
msg = EmailMessage()
cyclos = Cyclos()
strmsg = ""
totalCyclos, strmsg = checkBalancesCyclos(cyclos, strmsg)
mo = Mollie()
totolMollie, strmsg = checkPaimentsMollie(mo, strmsg)
if (abs(totalCyclos) != abs(totolMollie)):
    diff = abs(totalCyclos)-abs(totolMollie)
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
