#!/usr/bin/python3
# -*- coding: utf-8 -*-

import cyclos
from cyclos import Cyclos
import re
import unidecode
import json
import csv
import config as cfg

cyclos = Cyclos()
with open('adhpro.csv', newline='') as csvfile:
    listadhpro = csv.reader(csvfile, delimiter=',', quotechar='"')
    for row in listadhpro:
        #print(', '.join(row))
        # Test si date d'adhésion présente pour 2020
        if (row[1] != ""):
            unaccented_string = unidecode.unidecode(row[4])
            #username = re.sub('[^A-Za-z0-9]+', '', unaccented_string).lower()
            #username = (username[:16]) if len(username) > 16 else username
                #username = result["orga_name"][0].lower()+result["orga_name"][1:].lower()
            #print (row[0]+" username "+username)
            id = "10"+row[0]
            regex=re.compile(r'[^@]+@[^@]+\.[^@]+')
            if not regex.match(row[10]):
                continue
            print (id+" "+username+" "+row[10])
            addresses = [
                {
                    "name": "Siege Social",
                    "street": row[6],
                    "zip": row[7],
                    "city": row[8],
                    "country": "FR",
                    "defaultAddress": True
                }
            ]
            result_json = cyclos.addPro(id, unaccented_string, row[10], addresses)
            result = json.loads(result_json)
            #if "user" in result:
            #    id = result["user"]["id"]
            #    cyclos.resetPassword(id)
            #print(id)