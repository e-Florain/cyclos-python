#!/usr/bin/python3
# -*- coding: utf-8 -*-
from mollie import Mollie
import smtplib
from email.message import EmailMessage
import config as cfg

str = ""
mo = Mollie()
smtp = cfg.smtp['ip']
msg = EmailMessage()
str = str + mo.checkPaiementAdhMollie(True)

msg.set_content(str)
msg['Subject'] = f'Adhésions renouvellement'
msg['From'] = "no-reply@eflorain.fr"
#msg['To'] = "tech@florain.fr"
msg['To'] = "groche@guigeek.org"

if (str != ""):
    s = smtplib.SMTP(smtp)
    s.send_message(msg)
    s.quit()