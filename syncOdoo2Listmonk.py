#!/usr/bin/python3
# -*- coding: utf-8 -*-
from Odoo2Cyclos import Odoo2Cyclos
import re
import os
import csv
import logging
from logging.handlers import RotatingFileHandler

LOG_HEADER = " [" + __file__ + "] - "
LOG_PATH = os.path.dirname(os.path.abspath(__file__)) + '/log/'
logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
odoo2listmonkLogger = logging.getLogger('odoo2listmonk')
odoo2listmonkLogger.setLevel(logging.DEBUG)
odoo2listmonkLogger.propagate = False
fileHandler = RotatingFileHandler("{0}/{1}.log".format(LOG_PATH, 'odoo2listmonk'), maxBytes=2000000,
                                  backupCount=1500)
fileHandler.setFormatter(logFormatter)
odoo2listmonkLogger.addHandler(fileHandler)

mlc_emails = []
o2c = Odoo2Cyclos()
res = o2c.getMembersListmonk()

for infos in res['data']['results']:
    for list in infos['lists']:
        if (list['name'] == 'Mlc'):
            if (infos['email'] not in mlc_emails):
                mlc_emails.append(infos['email'])

# csv_emails = []
# with open('Subscribers.csv', newline='') as csvfile:
#         reader = csv.reader(csvfile, delimiter=',')
#         i=0
#         for row in reader:
#             csv_emails.append(row[0])

params = {"accept_newsletter": 't'}
res2 = o2c.getOdooAdhs(params=params)
odoo2listmonkLogger.info(LOG_HEADER + '[-] '+'Check Odoo in Listmonk')
for res in res2:
    if (res['email'] != None):
        email = res['email'].strip().lower()
        if (email not in mlc_emails):
            if (re.match(r'^([a-zA-Z0-9._%-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})$', email)):
                odoo2listmonkLogger.info(LOG_HEADER + '[-] '+'putMembersListmonk '+email)
                name = res['lastname']+" "+res['firstname']
                data = {'email': email, 'name': name}
                o2c.putMembersListmonk(data)

# print("### Test Mailman3 in Listmonk ###")
# for res in csv_emails:
#     email = res.strip().lower()
#     if (email not in mlc_emails):
#         if (re.match(r'^([a-zA-Z0-9._%-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})$', email)):
#             print(email)

