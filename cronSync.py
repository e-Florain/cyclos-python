#!/usr/bin/python3
# -*- coding: utf-8 -*-

from Odoo2Cyclos import Odoo2Cyclos
import smtplib
from email.message import EmailMessage

o2c = Odoo2Cyclos()

msg = EmailMessage()
o2c.simulate = True
filename = o2c.getChangesAdhs()
print(filename)
str = ""
with open("json/"+filename) as fp:
    str = str+fp.read()

str = str + "\n"
filename = o2c.getChangesAdhPros()
print(filename)
with open("json/"+filename) as fp:
    str = str+fp.read()

print(str)
msg.set_content(str)
# me == the sender's email address
# you == the recipient's email address
msg['Subject'] = f'Attention modifications à faire sur cyclos'
msg['From'] = "odoo@eflorain.fr"
msg['To'] = "groche@guigeek.org"

# Send the message via our own SMTP server.
s = smtplib.SMTP('192.168.100.1')
#s.send_message(msg)
s.quit()