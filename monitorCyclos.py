#!/usr/bin/python3
# -*- coding: utf-8 -*-
import cyclos
import re
from cyclos import Cyclos
from mollie import Mollie
from pprint import pprint

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
        if (payment['type']['internalName'] == 'debit.toPro'):
            if (payment['related']['user']['display'] != 'Le Florain'):
                totalreconversion = totalreconversion +float(payment['amount'])
    sold = float(totalinv)+float(total)
    if (sold != 0):
        print("ERREUR CRITIQUE")
        print("Total des soldes des comptes : "+str(total))
        print("Solde du compte de débit : "+str(totalinv))
    else:
        print("Total des soldes des comptes : "+str(total))
        print("Solde du compte de débit : "+str(totalinv))
    totalinv = float(totalinv) - totalreconversion
    return float(totalinv)

def checkPaimentsMollie(mollie):
    total=0
    list_payments = mollie.get_payments()
    for payment in list_payments:
        if (re.match('Change', payment['description']) is not None):
            if (payment['status'] == "paid"):
                total=total+float(payment['amount']['value'])
    print("Total Change via Mollie :"+str(total))
    return total

cyclos = Cyclos()
totalCyclos = checkBalancesCyclos(cyclos)
mo = Mollie()
totolMollie = checkPaimentsMollie(mo)
if (abs(totalCyclos) == abs(totolMollie)):
    print ("OK")
else:
    diff = abs(totalCyclos)-abs(totolMollie)
    print ("ERREUR : "+str(diff))