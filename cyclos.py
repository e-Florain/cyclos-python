#/usr/bin/python
# coding: utf-8
import requests
import json
from requests.auth import HTTPBasicAuth
import config as cfg

class Cyclos:

    def __init__(self):
        self.url = cfg.cyclos['url']
        self.user = cfg.cyclos['user']
        self.password = cfg.cyclos['password']
        requests.packages.urllib3.disable_warnings() 
       
    def getUser(self, user):
        resp = requests.get(self.url+'/users/'+user, auth=HTTPBasicAuth(self.user, self.password), verify=False)
        #self.displayJson(resp.text)    
        return json.loads(resp.text)

    def getUsers(self):
        resp = requests.get(self.url+'/users', auth=HTTPBasicAuth(self.user, self.password), verify=False)
        #self.displayJson(resp.text)
        return json.loads(resp.text)

    def getLoginFromEmail(self, email):
        users = self.getUsers()
        for user in users:
            userdetails = self.getUser(user['shortDisplay'])
            if (userdetails['email'].lower() == email.lower()):
                return user['shortDisplay']

    def getIdFromEmail(self, email):
        users = self.getUsers()
        for user in users:
            userdetails = self.getUser(user['shortDisplay'])
            if (userdetails['email'].lower() == email.lower()):
                return user['id']

    def addUser(self, username, name, email):
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        data = {'username': username, 'name': name, 'email': email, 'group': 'MBN_Particuliers', "passwords": [
            {
            "type": "login",
            "value": "azerty",
            "checkConfirmation": True,
            "confirmationValue": "azerty",
            "forceChange": False
            }
        ],
        "skipActivationEmail": True
        }
        resp = requests.post(self.url+'/users', auth=HTTPBasicAuth(self.user, self.password), verify=False, data=json.dumps(data), headers=headers)
        self.displayJson(resp.text)
        return resp.text

    def addPro(self, adh_id, username, email, addresses):
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        data = {"username": username,"name": username, "email": email, "group": "MBN_Pros", "passwords": [
            {
            "type": "login",
            "value": "1234",
            "checkConfirmation": True,
            "confirmationValue": "1234",
            "forceChange": True
            }
        ],
        "customValues":
            { 
            "Autorisation_eflorain_pro": "oui_eflorain_pro",
            "Autorisation_eflorain_part": "oui_eflorain_part",
            "Num_adherent_pro": adh_id
        },
        "skipActivationEmail": True,
        "acceptAgreement": True,
        "addresses": addresses
        }
        resp = requests.post(self.url+'/users', auth=HTTPBasicAuth(self.user, self.password), verify=False, data=json.dumps(data), headers=headers)
        self.displayJson(resp.text)
        return resp.text

    def getPasswords(self, user):
        resp = requests.get(self.url+'/'+user+'/passwords', auth=HTTPBasicAuth(self.user, self.password), verify=False)
        self.displayJson(resp.text)

    def setPaymentSystemtoUser(self, user, amount, description):
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        data = {'amount': amount, 'subject': user, 'type': 'MBNNEF.NEFtransferuser', 'description': description}      
        #resp = requests.post(self.url+'/'+self.systemIDNEF+'/payments', auth=HTTPBasicAuth(self.user, self.password), verify=False, data=json.dumps(data), headers=headers)
        resp = requests.post(self.url+'/system/payments', auth=HTTPBasicAuth(self.user, self.password), verify=False, data=json.dumps(data), headers=headers)
        #self.displayJson(resp.text)
        return json.loads(resp.text)

    def getPayments(self, user):
        resp = requests.get(self.url+'/'+user+'/payments/data-for-perform', auth=HTTPBasicAuth(self.user, self.password), verify=False)
        self.displayJson(resp.text)

    def getAddresses(self, user):
        resp = requests.get(self.url+'/'+user+'/addresses', auth=HTTPBasicAuth(self.user, self.password), verify=False)
        self.displayJson(resp.text)


    def createAddress(self, user):
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        data = {'name': 'Default', 'zip': '54200', 'city': 'Royaumeix', 'country': 'FR', 'defaultaddress': True, 'street': '10B rue d\'Alsace'}
        print(data)
        resp = requests.post(self.url+'/'+user+'/addresses', auth=HTTPBasicAuth(self.user, self.password), verify=False, data=json.dumps(data), headers=headers)
        print resp
        self.displayJson(resp.text)

    def setPaymentUsertoPro(self, user, pro, amount, description):
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        data = {'amount': amount, 'subject': pro, 'type': 'MBNPart.transfertUsertoPro', 'description': description}
        print data
        resp = requests.post(self.url+'/'+user+'/payments', auth=HTTPBasicAuth(self.user, self.password), verify=False, data=json.dumps(data), headers=headers)
        print resp
        self.displayJson(resp.text)

    def getTransfers(self):
        resp = requests.get(self.url+'/transfers', auth=HTTPBasicAuth(self.user, self.password), verify=False)
        self.displayJson(resp.text)

    def displayJson(self, json_text):
        json_object = json.loads(json_text)
        json_formatted_str = json.dumps(json_object, indent=2)
        print(json_formatted_str)

    def resetPassword(self, user):
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        data = {'w': 'email'}
        resp = requests.post(self.url+'/'+user+'/passwords/login/reset-and-send', auth=HTTPBasicAuth(self.user, self.password), verify=False, data=json.dumps(data), headers=headers)
        print resp
        #self.displayJson(resp.text)

    def changePassword(self, user, oldpassword, newpassword):
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        data = {'oldPassword': oldpassword, 'newPassword': newpassword, 'checkConfirmation': True, 'newPasswordConfirmation': newpassword, 'forceChange': True}
        print data
        resp = requests.post(self.url+'/'+user+'/passwords/login/change', auth=HTTPBasicAuth(self.user, self.password), verify=False, data=json.dumps(data), headers=headers)
        print resp
        #self.displayJson(resp.text)

    def enablePassword(self, user):
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        data = {}
        resp = requests.post(self.url+'/'+user+'/passwords/login/enable', auth=HTTPBasicAuth(self.user, self.password), verify=False, data=json.dumps(data), headers=headers)
        print resp
        self.displayJson(resp.text)

    def disablePassword(self, user):
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        data = {}
        resp = requests.post(self.url+'/'+user+'/passwords/login/disable', auth=HTTPBasicAuth(self.user, self.password), verify=False, data=json.dumps(data), headers=headers)
        print resp
        self.displayJson(resp.text)

    def generatePassword(self, user):
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        data = {}
        resp = requests.post(self.url+'/'+user+'/passwords/login/allow-generation', auth=HTTPBasicAuth(self.user, self.password), verify=False, data=json.dumps(data), headers=headers)
        print resp
        self.displayJson(resp.text)

    def getPasswords(self, user):
        resp = requests.get(self.url+'/'+user+'/passwords/login', auth=HTTPBasicAuth(self.user, self.password), verify=False)
        self.displayJson(resp.text)