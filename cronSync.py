#!/usr/bin/python3
# -*- coding: utf-8 -*-

from filelock import FileLock
from Odoo2Cyclos import Odoo2Cyclos
import smtplib
from email.message import EmailMessage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import random
import string
import json
import os
import config as cfg

o2c = Odoo2Cyclos()
keysjsons = dict()
letters = string.ascii_lowercase
url = cfg.hostname['url']
smtp = cfg.smtp['ip']

o2c.simulate = True
# Get Changes Adhs
filename = o2c.getChangesAdhs()
key = ''.join(random.choice(letters) for i in range(64))
keysjsons[key] = filename
str = ""
with open(os.path.dirname(os.path.abspath(__file__))+"/json/"+filename) as data_file:
    arr = json.load(data_file)
if bool(arr):
    with open(os.path.dirname(os.path.abspath(__file__))+"/json/"+filename) as fp:
        str = str+fp.read()
    str = str + "\n"
    str = str + "Pour valider ces changements, veuillez cliquer sur le lien suivant : "+url+"/allow/"+key
    str = str + "\n"
if (str != ""):
    str = str + "---------------------------------------------------------------------------------------\n"
    str = str + "---------------------------------------------------------------------------------------\n"

# Get Changes Adhs Pros
filename = o2c.getChangesAdhPros()
key = ''.join(random.choice(letters) for i in range(64))
keysjsons[key] = filename
with open(os.path.dirname(os.path.abspath(__file__))+"/json/"+filename) as data_file:
    arr = json.load(data_file)
if bool(arr):
    with open(os.path.dirname(os.path.abspath(__file__))+"/json/"+filename) as fp:
        str = str+fp.read()
    str = str + "\n"
    str = str + "Pour valider ces changements, veuillez cliquer sur le lien suivant : "+url+"/allow/"+key

with FileLock(os.path.dirname(os.path.abspath(__file__)) + "/myfile2.txt"):
    with open(os.path.dirname(os.path.abspath(__file__))+'/url.key', 'w') as outfile:
        json.dump(keysjsons, outfile, indent=4, sort_keys=False, separators=(',', ':'))
#print(str)
msg = MIMEMultipart()
msg.attach(MIMEText(str, "plain", "utf-8"))

#msg.set_content(str)
varfrom = "odoo@florain.fr"
varto = "tech@florain.fr"
msg['Subject'] = Header(f'Attention modifications à faire sur cyclos', "utf-8")
msg['From'] = varfrom
msg['To'] = varto
#msg['To'] = "groche@guigeek.org"

if (str != ""):
    s = smtplib.SMTP(smtp)
    s.sendmail(varfrom, varto, msg.as_string())
    s.quit()
