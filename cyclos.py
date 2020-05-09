#/usr/bin/python
# coding: utf-8
import requests
import json
from requests.auth import HTTPBasicAuth
import config as cfg

class Cyclos:

    def __init__(self):
        self.url = cfg.url
        self.user = cfg.user
        self.password = cfg.password
        self.systemIDNEF = cfg.systemIDNEF
        
    def getUsers(self):
        resp = requests.get(self.url+'/users', auth=HTTPBasicAuth(self.user, self.password), verify=False)
        self.displayJson(resp.text)

    def addUser(self):
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        data = {'username': 'toto1','name': 'Toto1', 'email': 'toto@gmail.com', 'group': 'MBN_Particuliers', "passwords": [
            {
            "type": "string",
            "value": "azerty",
            "checkConfirmation": True,
            "confirmationValue": "azerty",
            "forceChange": True
            }
        ],
        "skipActivationEmail": True,
        "addresses": [
            {
            "name": "Maison",
            "addressLine1": "5 rue du Pierre Desproges",
            "zip": "54000",
            "city": "Nancy",
            "country": "France",
            "defaultAddress": True
            }
        ]}
        resp = requests.post(self.url+'/users', auth=HTTPBasicAuth(self.user, self.password), verify=False, data=json.dumps(data), headers=headers)
        print resp
        self.displayJson(resp.text)

    def setPaymentSystemtoUser(self, user):
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        data = {'amount': '10', 'subject': user, 'type': 'MBNNEF.NEF_transfer_user', 'description': 'tefdsfdsfd0'}
        print data
        resp = requests.post(self.url+'/'+self.systemIDNEF+'/payments', auth=HTTPBasicAuth(self.user, self.password), verify=False, data=json.dumps(data), headers=headers)
        print resp
        self.displayJson(resp.text)

    def getPayments(self, user):
        resp = requests.get(self.url+'/'+user+'/payments/data-for-perform', auth=HTTPBasicAuth(self.user, self.password), verify=False)
        self.displayJson(resp.text)

    def getAddresses(self, user):
        resp = requests.get(self.url+'/'+user+'/addresses', auth=HTTPBasicAuth(self.user, self.password), verify=False)
        self.displayJson(resp.text)


    def createAddress(self, user):
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        data = {'name': 'Default', 'zip': '55210', 'city': 'Saint-Maurice-sous-les-côtes', 'country': 'FR', 'defaultaddress': True, 'addressLine1': '34 Rue de l\'Église'}
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