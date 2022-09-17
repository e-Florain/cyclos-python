#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import requests
from requests.auth import HTTPBasicAuth
import smtplib
import qrcode
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
import logging
from logging.handlers import RotatingFileHandler
import time
import unidecode
from datetime import datetime
import re
import json
import string
import random
import config as cfg
import importlib.util
from cyclos import Cyclos
#cyclos = importlib.util.spec_from_file_location("cyclos", "../cyclos.py")
#cyclosvar = importlib.util.module_from_spec(cyclos)
#cyclos.loader.exec_module(cyclosvar)
#test = cyclosvar.Cyclos()

#cyclosgrppro = "professionnels"
#cyclosgrppart = "particuliers"

LOG_HEADER = " [" + __file__ + "] - "
LOG_PATH = os.path.dirname(os.path.abspath(__file__)) + '/log/'
logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
odoo2cyclosLogger = logging.getLogger('odoo2cyclos')
odoo2cyclosLogger.setLevel(logging.DEBUG)
odoo2cyclosLogger.propagate = False
fileHandler = RotatingFileHandler("{0}/{1}.log".format(LOG_PATH, 'odoo2cyclos'), maxBytes=2000000,
                                  backupCount=1500)
fileHandler.setFormatter(logFormatter)
odoo2cyclosLogger.addHandler(fileHandler)

class Odoo2Cyclos:
    
    def __init__(self, simulate=False):
        self.url = cfg.florapi['url']
        self.key = cfg.florapi['key']
        self.smtp = cfg.smtp['ip']
        self.cyclosgrppro = "professionnels"
        self.cyclosgrppart = "particuliers"
        self.nextcloud_url = cfg.nextcloud['url']
        self.nextcloud_login = cfg.nextcloud['login']
        self.nextcloud_password = cfg.nextcloud['password']
        self.nextcloud_path = cfg.nextcloud['path']
        self.simulate = simulate
        #self.cyclos = cyclosvar.Cyclos()
        self.cyclos = Cyclos()
        #self.grpPro = "professionnels"
        requests.packages.urllib3.disable_warnings()
    
    def is_valid(self, password):
        special_char = "!@%/()=?+.-"
        password_characters = string.ascii_letters + string.digits + special_char
        if len(password) < 8:
            return False
        if not any(c in password for c in special_char):
            return False
        if not any(c.isdigit() for c in password):
            return False
        if not any(c.islower() for c in password):
            return False
        if not any(c.isupper() for c in password):
            return False
        return True 

    def displayJson(self, json_text):
        #cyclosLogger.info(LOG_HEADER + '[-] '+'putUser/'+email+'/'+data)
        json_object = json.loads(json_text)
        json_formatted_str = json.dumps(json_object, indent=2)
        print(json_formatted_str)

    def getOdooAdhs(self, params={}):
        odoo2cyclosLogger.info(LOG_HEADER + '[-] '+'getOdooAdhs')
        headers = {'x-api-key': self.key, 'Content-type': 'application/json', 'Accept': 'text/plain'}
        resp = requests.get(self.url+'/getAdhs', params=params, headers=headers, verify=False)
        #print(resp.text)
        try:
            #self.displayJson(resp.text)
            return json.loads(resp.text)
        except ValueError as e:
            print(resp.text)
            return False
        
    def getOdooAdhpros(self, params={}):
        odoo2cyclosLogger.info(LOG_HEADER + '[-] '+'getOdooAdhpros')
        headers = {'x-api-key': self.key, 'Content-type': 'application/json', 'Accept': 'text/plain'}
        resp = requests.get(self.url+'/getAdhpros', headers=headers, verify=False)
        #print(resp.text)
        return json.loads(resp.text)

    def syncAdhs(self, cyclos):
        """ Sync Adhs """
        odoo2cyclosLogger.info(LOG_HEADER + '[-] '+'Sync adhs ...')
        listadhs = self.getOdooAdhs()
        result = {}
        for adh in listadhs:
            if ((adh['firstname'] != None) and (adh['lastname'] != None)):
                username = adh['firstname'][0].lower()+adh['lastname'].lower()
                #print(username)
                #result_json = cyclos.addUser(username, result["firstname"]+" "+result["lastname"], result["email"])
                #result = json.loads(result_json)
                if "user" in result:
                    id = result["user"]["id"]
                    #cyclos.resetPassword(id)
                    #print(id)
                else:
                    if "propertyErrors" in result:
                        if "username" in result["propertyErrors"]:
                            err = result["propertyErrors"]["username"][0]
                            if (re.match(".*unique.*", err)):
                                print("Utilisateur deja existant")
                                # users_json = cyclos.getUsers()
                                users = json.loads(users_json)
                                print(users)

    def getChangesAdhs(self):
        odoo2cyclosLogger.info(LOG_HEADER + '[-] '+'getChangesAdhs')
        changesDB = dict()
        listUsersOdoo = self.getUsersOdoo("adhs")
        #print(listUsersOdoo)
        listUsersCyclos = self.getUsersCyclos(self.cyclosgrppart)
        #print(listUsersCyclos)
        for k, v in listUsersCyclos.items():
            #print(k)
            #print(v)
            if (k not in listUsersOdoo):
                #print("DELETE")
                #print(k)
                changes = dict()
                listchanges = list()
                changes['dbtochange'] = 'cyclos'
                changes['type'] = 'delete'
                listchanges.append(changes)
                changesDB[k] = listchanges
            #break
        for k, v in listUsersOdoo.items():
            #print("CREATE "+k)
            if (v['account_cyclos']):
                if (k not in listUsersCyclos):
                    #print("CREATE")
                    #print(v)    
                    lastname_unaccented = unidecode.unidecode(v['lastname'])
                    firstname_unaccented = unidecode.unidecode(v['firstname'])
                    changes = dict()
                    listchanges = list()
                    changes['type'] = 'create'
                    changes['dbtochange'] = 'cyclos'
                    infostocreate = dict()
                    #if (v['email']) == "null":
                    #    next;
                    infostocreate['email'] = v['email']
                    res = re.match('\w{3}, \d{2} \w{3} \d{4}', str(v["membership_stop"]))
                    if (res != None):
                        date_object = datetime.strptime(v["membership_stop"],"%a, %d %b %Y %H:%M:%S %Z")
                        infostocreate['DateFinAdhesion'] = date_object.strftime("%Y-%m-%d")
                    else:
                        infostocreate['DateFinAdhesion'] = ""
                    infostocreate['Num_adherent_part'] = v['ref']
                    #infostocreate['adh_id'] = v['adh_id']
                    infostocreate['name'] = firstname_unaccented+" "+lastname_unaccented
                    changes['infos'] = infostocreate
                    listchanges.append(changes)
                    changesDB[k] = listchanges
                else:
                    #print("COMPARE")
                    if (listUsersCyclos[k]['status'] == 'active'):
                        changed = False
                        changes = dict()
                        listchanges = list()
                        lastname_unaccented = unidecode.unidecode(v['lastname'])
                        firstname_unaccented = unidecode.unidecode(v['firstname'])
                        name = firstname_unaccented+" "+lastname_unaccented
                        if (name != unidecode.unidecode(listUsersCyclos[k]["display"])):
                            #print (listUsersCyclos[k]["display"])
                            changes['field'] = 'display'
                            changes['newvalue'] = name
                            changes['oldvalue'] = unidecode.unidecode(listUsersCyclos[k]["display"])
                            changes['type'] = 'modify'
                            # A changer par la suite avec la date de modification
                            changes['dbtochange'] = 'cyclos'
                            changed = True
                            listchanges.append(changes)
                        if not 'customValues' in listUsersCyclos[k]:
                            # DateFinAdhesion
                            res = re.match('\w{3}, \d{2} \w{3} \d{4}', str(v["membership_stop"]))
                            if (res != None):
                                date_object = datetime.strptime(v["membership_stop"],"%a, %d %b %Y %H:%M:%S %Z")
                                datefinadh = date_object.strftime("%Y-%m-%d")
                            else:
                                datefinadh = ""
                            changes['field'] = 'DateFinAdhesion'
                            changes['newvalue'] = datefinadh
                            changes['oldvalue'] = ""
                            changes['type'] = 'modify'
                            changes['dbtochange'] = 'cyclos'
                            changed = True
                            listchanges.append(changes)
                            # Num_adherent_part
                            changes['field'] = 'Num_adherent_part'
                            changes['newvalue'] = v['ref']
                            changes['oldvalue'] = ""
                            changes['type'] = 'modify'
                            changes['dbtochange'] = 'cyclos'
                            changed = True
                            listchanges.append(changes)
                        else:
                            for customvalue in listUsersCyclos[k]['customValues']:
                                if (customvalue['field']['internalName'] == "DateFinAdhesion"):
                                    res = re.match('\w{3}, \d{2} \w{3} \d{4}', str(v["membership_stop"]))
                                    if (res != None):
                                        date_object = datetime.strptime(v["membership_stop"],"%a, %d %b %Y %H:%M:%S %Z")
                                        datefinadh = date_object.strftime("%Y-%m-%d")
                                        res2 = re.match('^'+datefinadh, customvalue['dateValue'])
                                        if (res2 == None):
                                            changes['field'] = 'DateFinAdhesion'
                                            changes['newvalue'] = datefinadh
                                            changes['oldvalue'] = customvalue['dateValue']
                                            changes['type'] = 'modify'
                                            # A changer par la suite avec la date de modification
                                            changes['dbtochange'] = 'cyclos'
                                            changed = True
                                            listchanges.append(changes)
                                if (customvalue['field']['internalName'] == "Num_adherent_part"):
                                    if (customvalue['integerValue'] != int(v['ref'])):
                                        changes['field'] = 'Num_adherent_part'  
                                        changes['newvalue'] = int(v['ref'])
                                        changes['oldvalue'] = customvalue['integerValue']
                                        changes['type'] = 'modify'
                                        # A changer par la suite avec la date de modification
                                        changes['dbtochange'] = 'cyclos'
                                        changed = True
                                        listchanges.append(changes)
                        if (changed):
                            changesDB[k] = listchanges
        #print(changesDB)
        jsonfilename = time.strftime("%Y%m%d-%H%M%S")+'-adhs-changes.json'
        #print(jsonfilename)
        with open(os.path.dirname(os.path.abspath(__file__)) +'/json/'+jsonfilename, 'w') as outfile:
            json.dump(changesDB, outfile, indent=4, sort_keys=False, separators=(',', ':'))
        return jsonfilename

    def getChangesAdhPros(self):
        odoo2cyclosLogger.info(LOG_HEADER + '[-] '+'getChangesAdhPros')
        changesDB = dict()
        listUsersOdoo = self.getUsersOdoo("adhpros")
        #print(listUsersOdoo)
        listUsersCyclos = self.getUsersCyclos(self.cyclosgrppro)
        #print(listUsersCyclos)
        for k, v in listUsersCyclos.items():
            #print(k)
            #print(v)
            if (k not in listUsersOdoo):
                #print("DELETE")
                #print(k)
                changes = dict()
                listchanges = list()
                changes['dbtochange'] = 'cyclos'
                changes['type'] = 'delete'
                listchanges.append(changes)
                changesDB[k] = listchanges
            #break
        for k, v in listUsersOdoo.items():
            #print (v)
            #print("CREATE "+k)
            if (v["account_cyclos"]):
                if (k not in listUsersCyclos):
                    #print("CREATE")         
                    unaccented_string = unidecode.unidecode(v["name"])
                    addresses = [
                        {
                        "name": "Siege Social",
                        "street": v["street"],
                        "zip": v["zip"],
                        "city": v["city"],
                        "country": "FR",
                        "defaultAddress": True
                        }
                    ]
                    changes = dict()
                    listchanges = list()
                    changes['type'] = 'create'
                    changes['dbtochange'] = 'cyclos'
                    infostocreate = dict()
                    infostocreate['email'] = v['email']
                    #infostocreate['adh_id'] = v['adh_id']
                    infostocreate['name'] = unaccented_string
                    infostocreate['addresses'] = addresses
                    changes['infos'] = infostocreate
                    listchanges.append(changes)
                    changesDB[k] = listchanges
                else:
                    #print("COMPARE")
                    changed = False
                    changes = dict()
                    listchanges = list()
                    if (unidecode.unidecode(v["name"]) != unidecode.unidecode(listUsersCyclos[k]["display"])):
                        #print (listUsersCyclos[k]["display"])
                        changes['field'] = 'display'
                        changes['newvalue'] = unidecode.unidecode(v["name"])
                        changes['oldvalue'] = unidecode.unidecode(listUsersCyclos[k]["display"])
                        changes['type'] = 'modify'
                        # A changer par la suite avec la date de modification
                        changes['dbtochange'] = 'cyclos'
                        changed = True
                        listchanges.append(changes)
                    if (changed):
                        changesDB[k] = listchanges
        #print(changesDB)
        jsonfilename = time.strftime("%Y%m%d-%H%M%S")+'-adhpros-changes.json'
        #print(jsonfilename)
        with open(os.path.dirname(os.path.abspath(__file__)) +'/json/'+jsonfilename, 'w') as outfile:
            json.dump(changesDB, outfile, indent=4, sort_keys=False, separators=(',', ':'))
        return jsonfilename

    def applyChangesAdhPros(self, jsonfile):
        odoo2cyclosLogger.info(LOG_HEADER + '[-] '+'applyChangesAdhPros')
        with open(os.path.dirname(os.path.abspath(__file__)) +'/json/'+jsonfile) as data_file:
            datas = json.load(data_file)
            for k, v in datas.items():
                for changes in v:
                    if (changes['dbtochange'] == "cyclos"):
                        """if (changes['type'] == "delete"):
                            print("delete "+k)
                            id = self.cyclos.getIdFromEmail(k)
                            if (id == False):
                                odoo2cyclosLogger.info(LOG_HEADER + '[-] impossible de trouver '+k)
                            else:
                                self.cyclos.disableUser(id)"""
                        """if (changes['type'] == "modify"):
                            print("modify "+k)
                            #id = cyclos.getIdFromEmail(k)
                            #data={changes['field']: changes['newvalue']}
                            #data={"name": changes['newvalue'], "username": k, "email": k, "hiddenFields": [], "customValues": {}}.
                            data={"name": changes['newvalue'], "username": k, "email": k}
                            #data={"name": changes['newvalue']}
                            self.cyclos.putUser(k, data)"""
                        if (changes['type'] == "create"):
                            print("create "+k)
                            infos = changes['infos']
                            length = 8
                            special_char = "!@%/()=?+.-"
                            password_characters = string.ascii_letters + string.digits + special_char
                            password_string = ''
                            while not self.is_valid(password_string):
                                password_string = "".join([random.choice(password_characters)
                                                for n in range(length)])
                            result_json = self.cyclos.addPro(infos['name'], infos['email'], password_string, infos['addresses'])
                            name = infos['name'].replace('/', '_')
                            self.generateRandomQR(name, infos['email'])
                            self.sendMailPro(infos['email'], password_string, name)

    def applyChangesAdhs(self, jsonfile):
        odoo2cyclosLogger.info(LOG_HEADER + '[-] '+'applyChangesAdhs')
        with open(os.path.dirname(os.path.abspath(__file__)) +'/json/'+jsonfile) as data_file:
            datas = json.load(data_file)
            for k, v in datas.items():
                for changes in v:
                    if (changes['dbtochange'] == "cyclos"):
                        """if (changes['type'] == "delete"):
                            print("delete "+k)
                            id = self.cyclos.getIdFromEmail(k)
                            if (id == False):
                                odoo2cyclosLogger.info(LOG_HEADER + '[-] impossible de trouver '+k)
                            else:
                                self.cyclos.disableUser(id)"""
                        if (changes['type'] == "modify"):
                            #print("modify "+k)
                            data = self.cyclos.getUserDateForEdit(k)
                            data['user']['name'] = changes['newvalue']
                            #data={changes['field']: changes['newvalue']}
                            #data={"name": changes['newvalue'], "username": k, "email": k}
                            self.cyclos.putUser(k, data['user'])
                        if (changes['type'] == "create"):
                            if (k != "null"):
                                #print("create "+k)
                                infos = changes['infos']
                                length = 8
                                special_char = "!@%/()=?+.-"
                                password_characters = string.ascii_letters + string.digits + special_char
                                password_string = ''
                                while not self.is_valid(password_string):
                                    password_string = "".join([random.choice(password_characters)
                                                    for n in range(length)])
                                result_json = self.cyclos.addUser(infos['email'], infos['name'], infos['email'], password_string, infos['Num_adherent_part'], infos['DateFinAdhesion'])
                                self.sendMailPart(infos['email'], password_string)

    def getUsersOdoo(self, type):
        odoo2cyclosLogger.info(LOG_HEADER + '[-] '+'getUsersOdoo '+type)
        listusersbyemail=dict()
        params = {"account_cyclos": 't'}
        if (type=="adhs"):
            listusers = self.getOdooAdhs(params=params)
        if (type=="adhpros"):
            listusers = self.getOdooAdhpros(params=params)
        for user in listusers:
            listusersbyemail[user['email']] = user
        return listusersbyemail

    def postQrCode(self, name):
        requests.packages.urllib3.disable_warnings()
        headers = {'Content-type': 'image/png'}
        fullurl = self.nextcloud_url + self.nextcloud_path + "/" + name
        fp = open(os.path.dirname(os.path.abspath(__file__)) + "/" + name, "rb")
        resp = requests.request("PUT", fullurl, auth=HTTPBasicAuth(self.nextcloud_login, self.nextcloud_password), data=fp.read(), verify=False, headers=headers)

    def generateRandomQR(self, name, email):
        qr = qrcode.QRCode(version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(email)
        qr.make(fit=True)
        img = qr.make_image()
        img.save(os.path.dirname(os.path.abspath(__file__)) + "/" + name+".png")
        self.postQrCode(name+".png")

    def sendMailPart(self, email, password):
        odoo2cyclosLogger.info(LOG_HEADER + '[-] '+'sendMail')
        msg = MIMEMultipart()
        str = "Bonjour,<br>"
        str = str + "Voici vos identifiants :<br>"
        str = str + "<b>Login</b> : "+email+"<br>"
        str = str + "<b>Mot de passe</b> : "+password+"<br>"
        str = str + "<b>URL de connexion</b> : <a href=\"https://cyclos.florain.fr\">https://cyclos.florain.fr</a><br>"
        msgText = MIMEText('%s' % (str), 'html')
        msg.attach(msgText)

        msg['Subject'] = f'Florain : vos identifiants'
        msg['From'] = "no-reply@eflorain.fr"
        msg['To'] = email
        s = smtplib.SMTP(self.smtp)
        #s.send_message(msg)
        s.sendmail(msg['From'], msg['To'], msg.as_string())
        s.quit()

    def sendMailPro(self, email, password, name):
        odoo2cyclosLogger.info(LOG_HEADER + '[-] '+'sendMail')
        msg = MIMEMultipart()
        str = "Bonjour,<br>"
        str = str + "Voici vos identifiants :<br>"
        str = str + "<b>Login</b> : "+email+"<br>"
        str = str + "<b>Mot de passe</b> : "+password+"<br>"
        str = str + "<b>URL de connexion</b> : https://cyclos.florain.fr<br>"
        str = str +"<br> Vous trouverez également en pièce jointe votre QRCode "
        str = str +"qui permettra à vos clients de vous identifier dans Cyclos plus facilement"
        msgText = MIMEText('%s' % (str), 'html')
        msg.attach(msgText)
        with open(os.path.dirname(os.path.abspath(__file__)) +'/'+name+'.png', 'rb') as fp:
            img = MIMEImage(fp.read())
            img.add_header('Content-Disposition', 'attachment', filename="QRCode.png")
            msg.attach(img)

        msg['Subject'] = f'Florain : vos identifiants'
        msg['From'] = "no-reply@eflorain.fr"
        msg['To'] = email
        s = smtplib.SMTP(self.smtp)
        #s.send_message(msg)
        s.sendmail(msg['From'], msg['To'], msg.as_string())
        s.quit()

    def getUsersCyclos(self, group):
        odoo2cyclosLogger.info(LOG_HEADER + '[-] '+'getUsersCyclos')
        listusers=dict()
        users = self.cyclos.getUsers(group)
        #print(users)
        for user in users:
            userinfo = self.cyclos.getUser(user['id'])
            listusers[user['email']] = userinfo
        return listusers
