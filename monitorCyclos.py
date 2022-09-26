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
    #print(totalinv)
    sold = float(totalinv)+float(total)
    if (sold != 0):
        print("ERREUR")
        print("Total des soldes des comptes : "+str(total))
        print("Solde du compte de débit : "+str(totalinv))
    else:
        print("Total des soldes des comptes : "+str(total))
        print("Solde du compte de débit : "+str(totalinv))

def checkPaimentsMollie(mollie):
    total=0
    list_payments = mollie.get_payments()
    for payment in list_payments:
        if (re.match('Change', payment['description']) is not None):
            if (payment['status'] == "paid"):
                total=total+float(payment['amount']['value'])
    print("Total Change via Mollie :"+str(total))

cyclos = Cyclos()
checkBalancesCyclos(cyclos)
mo = Mollie()
checkPaimentsMollie(mo)