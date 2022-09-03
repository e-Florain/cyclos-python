#!/usr/bin/python3
# -*- coding: utf-8 -*-

from Odoo2Cyclos import Odoo2Cyclos
import smtplib
from email.message import EmailMessage
import random
import string
import json
import os

o2c = Odoo2Cyclos()
keysjsons = dict()
letters = string.ascii_lowercase

msg = EmailMessage()
o2c.simulate = True
filename = o2c.getChangesAdhs()
key = ''.join(random.choice(letters) for i in range(64))
keysjsons[key] = filename
str = ""
with open(os.path.dirname(os.path.abspath(__file__))+"/json/"+filename) as fp:
    str = str+fp.read()
str = str + "\n"
str = str + "Pour valider ces changements, veuillez cliquer sur le lien suivant : http://10.0.3.184:8080/allow/"+key
str = str + "\n"
filename = o2c.getChangesAdhPros()
key = ''.join(random.choice(letters) for i in range(64))
keysjsons[key] = filename
with open(os.path.dirname(os.path.abspath(__file__))+"/json/"+filename) as fp:
    str = str+fp.read()
str = str + "\n"
str = str + "Pour valider ces changements, veuillez cliquer sur le lien suivant : http://10.0.3.184:8080/allow/"+key

with open(os.path.dirname(os.path.abspath(__file__))+'/url.key', 'w') as outfile:
    json.dump(keysjsons, outfile, indent=4, sort_keys=False, separators=(',', ':'))
print(str)
msg.set_content(str)
# me == the sender's email address
# you == the recipient's email address
msg['Subject'] = f'Attention modifications à faire sur cyclos'
msg['From'] = "odoo@eflorain.fr"
msg['To'] = "groche@guigeek.org"

# Send the message via our own SMTP server.
s = smtplib.SMTP('192.168.100.15')
#s.send_message(msg)
s.quit()