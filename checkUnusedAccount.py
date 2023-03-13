#!/usr/bin/python3
# -*- coding: utf-8 -*-

import cyclos
from cyclos import Cyclos
from datetime import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
import smtplib
from email.message import EmailMessage
import config as cfg

cyclos = Cyclos()
smtp = cfg.smtp['ip']
msg = EmailMessage()
str = "Comptes sans connexion depuis 3 mois"
str = str + "\n"

three_months = datetime.today() + relativedelta(months=-3)
#allusers = cyclos.getAllUsers()
allusers = cyclos.getUsers('particuliers')
for user in allusers:
    user = cyclos.getUser(user['id'])
    if 'lastLogin' in user:
        datetime_object = datetime.strptime(user['lastLogin'][0:19], '%Y-%m-%dT%H:%M:%S')
        if (datetime_object < three_months):
            #print(user['email']+" "+user['lastLogin'])
            str = str + user['email']+" "+user['lastLogin']
            str = str + "\n"

msg.set_content(str)
msg['Subject'] = f'Comptes non utilisés depuis longtemps'
msg['From'] = "no-reply@eflorain.fr"
#msg['To'] = "tech@florain.fr"
msg['To'] = "groche@guigeek.org"

if (str != ""):
    s = smtplib.SMTP(smtp)
    s.send_message(msg)
    s.quit()