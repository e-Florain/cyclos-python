#/usr/bin/python
# coding: utf-8
import requests
import json
import logging
import os
from logging.handlers import RotatingFileHandler
from requests.auth import HTTPBasicAuth
import config as cfg

LOG_HEADER = " [" + __file__ + "] - "
LOG_PATH = os.path.dirname(os.path.abspath(__file__)) + '/log/'
logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
cyclosLogger = logging.getLogger('cyclos')
cyclosLogger.setLevel(logging.DEBUG)
cyclosLogger.propagate = False
fileHandler = RotatingFileHandler("{0}/{1}.log".format(LOG_PATH, 'cyclos'), maxBytes=2000000,
                                  backupCount=1500)
fileHandler.setFormatter(logFormatter)
cyclosLogger.addHandler(fileHandler)

class Cyclos:

    def __init__(self):
        self.url = cfg.cyclos['url']
        self.user = cfg.cyclos['user']
        self.password = cfg.cyclos['password']
        self.debug = cfg.cyclos['debug']
        self.grpPro = "professionnels"
        requests.packages.urllib3.disable_warnings()
    
    def getAuth(self):
        cyclosLogger.info(LOG_HEADER + '[-] '+'auth')
        resp = requests.get(self.url+'/auth', auth=HTTPBasicAuth(self.user, self.password), verify=False)
        if (not resp.ok):
            cyclosLogger.error(LOG_HEADER + resp.text)
        if (self.debug):
            cyclosLogger.debug(LOG_HEADER + resp.text)
        auth = json.loads(resp.text)
        if (auth["user"]["shortDisplay"] == "adminAPI"):
            return True
        else:
            return False

    def getUser(self, user):
        cyclosLogger.info(LOG_HEADER + '[-] '+'getUser/'+user)
        resp = requests.get(self.url+'/users/'+user, auth=HTTPBasicAuth(self.user, self.password), verify=False)
        if (not resp.ok):
            cyclosLogger.error(LOG_HEADER + resp.text)
        if (self.debug):
            cyclosLogger.debug(LOG_HEADER + resp.text)
        return json.loads(resp.text)

    def getAccount(self, id):
        cyclosLogger.info(LOG_HEADER + '[-] '+'getAccount/'+id)
        resp = requests.get(self.url+'/'+id+'/accounts/', auth=HTTPBasicAuth(self.user, self.password), verify=False)
        if (not resp.ok):
            cyclosLogger.error(LOG_HEADER + resp.text)
        if (self.debug):
            cyclosLogger.debug(LOG_HEADER + resp.text)
        return json.loads(resp.text)

    def getBalances(self):
        cyclosLogger.info(LOG_HEADER + '[-] '+'getBalances')
        resp = requests.get(self.url+'/accounts/data-for-user-balances', auth=HTTPBasicAuth(self.user, self.password), verify=False)
        if (not resp.ok):
            cyclosLogger.error(LOG_HEADER + resp.text)
        if (self.debug):
            cyclosLogger.debug(LOG_HEADER + resp.text)
        return json.loads(resp.text)

    def getUserBalancesSummary(self,id):
        cyclosLogger.info(LOG_HEADER + '[-] '+'getUserBalancesSummary/'+id)
        resp = requests.get(self.url+'/accounts/'+id+'/user-balances/summary?statuses=active&statuses=blocked&statuses=disabled&statuses=pending&statuses=purged&statuses=removed', auth=HTTPBasicAuth(self.user, self.password), verify=False)
        if (not resp.ok):
            cyclosLogger.error(LOG_HEADER + resp.text)
        if (self.debug):
            cyclosLogger.debug(LOG_HEADER + resp.text)
        return json.loads(resp.text)

    def getUserDateForEdit(self, user):
        cyclosLogger.info(LOG_HEADER + '[-] '+'getUserDateForEdit/'+user)
        resp = requests.get(self.url+'/users/'+user+'/data-for-edit-profile', auth=HTTPBasicAuth(self.user, self.password), verify=False)
        if (not resp.ok):
            cyclosLogger.error(LOG_HEADER + resp.text)
        if (self.debug):
            cyclosLogger.debug(LOG_HEADER + resp.text)
        #self.displayJson(resp.text)
        return json.loads(resp.text)

    def getAdhPro(self, email):
        cyclosLogger.info(LOG_HEADER + '[-] '+'getAdhPro/'+email)
        users = self.getUsers(self.grpPro)
        for user in users:
            if (user['email'] == email):
                return self.getUser(user['id'])

    def putUser(self, email, data):
        cyclosLogger.info(LOG_HEADER + '[-] '+'putUser/'+email+'/'+str(data))
        #print(data)
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        id = self.getIdFromEmail(email)
        if (id != False):
            resp = requests.put(self.url+'/users/'+id, auth=HTTPBasicAuth(self.user, self.password), verify=False, data=json.dumps(data), headers=headers)
            if (not resp.ok):
                cyclosLogger.error(LOG_HEADER + resp.text)
            if (self.debug):
                cyclosLogger.debug(LOG_HEADER + resp.text)
            return resp.text
        else:
            cyclosLogger.error(LOG_HEADER + "User not found")
        #print(resp.text)
        #self.displayJson(resp.text)

    def postUser(self, email, data):
        cyclosLogger.info(LOG_HEADER + '[-] '+'postUser/'+email+'/profile '+str(data))
        #print(data)
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        id = self.getIdFromEmail(email)
        resp = requests.post(self.url+'/users/'+id+'/profile', auth=HTTPBasicAuth(self.user, self.password), verify=False, data=json.dumps(data), headers=headers)
        if (not resp.ok):
            cyclosLogger.error(LOG_HEADER + resp.text)
        if (self.debug):
            cyclosLogger.debug(LOG_HEADER + resp.text)
        self.displayJson(resp.text)

    def getAllUsers(self):
        cyclosLogger.info(LOG_HEADER + 'getAllUsers')
        resp = requests.get(self.url+'/users?pageSize=10000', auth=HTTPBasicAuth(self.user, self.password), verify=False)
        if (not resp.ok):
            cyclosLogger.error(LOG_HEADER + resp.text)
        if (self.debug):
            cyclosLogger.debug(LOG_HEADER + resp.text)
        return json.loads(resp.text)

    def getUsers(self, group):
        cyclosLogger.info(LOG_HEADER + 'getUsers/'+group)
        resp = requests.get(self.url+'/users?groups='+group+'&pageSize=10000&statuses=active&statuses=active&statuses=blocked&statuses=pending', auth=HTTPBasicAuth(self.user, self.password), verify=False)
        if (not resp.ok):
            cyclosLogger.error(LOG_HEADER + resp.text)
        if (self.debug):
            cyclosLogger.debug(LOG_HEADER + resp.text)
        #self.displayJson(resp.text)
        return json.loads(resp.text)

    def getLoginFromEmail(self, email):
        cyclosLogger.info(LOG_HEADER + '[-] '+'getLoginFromEmail/'+email)
        users = self.getUsers()
        for user in users:
            userdetails = self.getUser(user['shortDisplay'])
            if (userdetails['email'].lower() == email.lower()):
                return user['shortDisplay']

    def getIdFromEmail(self, email):
        cyclosLogger.info(LOG_HEADER + '[-] '+'getIdFromEmail/'+email)
        users = self.getAllUsers()
        for user in users:
            userdetails = self.getUser(user['email'])
            if (userdetails['email'].lower() == email.lower()):
                return user['id']
        return False

    def addUser(self, username, name, email, password, numAdhPart, datefinadh):
        cyclosLogger.info(LOG_HEADER + '[-] '+'addUser/'+username+'/'+email+'/'+name)
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        data = {'username': username, 'name': name, 'email': email, 'group': 'particuliers', "passwords": [
            {
            "type": "login",
            "value": password,
            #"checkConfirmation": True,
            "confirmationValue": password,
            "forceChange": True
            }
        ],
            "customValues": {
                "DateFinAdhesion": datefinadh,
                "Num_adherent_part": numAdhPart
            },
            "skipActivationEmail": True
        }
        resp = requests.post(self.url+'/users', auth=HTTPBasicAuth(self.user, self.password), verify=False, data=json.dumps(data), headers=headers)
        if (not resp.ok):
            cyclosLogger.error(LOG_HEADER + resp.text)
        if (self.debug):
            cyclosLogger.debug(LOG_HEADER + resp.text)
        if (resp.status_code != 201):
            cyclosLogger.error(LOG_HEADER + email + " " + resp.text)
        return resp.text

    def addPro(self, name, email, password, addresses):
        cyclosLogger.info(LOG_HEADER + '[-] '+'addPro/'+name+'/'+email+'/'+str(addresses))
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        data = {"username": email, "name": name, "email": email, "group": "professionnels", "passwords": [
            {
            "type": "login",
            "value": password,
            "checkConfirmation": True,
            "confirmationValue": password,
            "forceChange": True
            }
        ],
        "customValues":
            { 
        },
        "skipActivationEmail": True,
        "acceptAgreement": True,
        "addresses": addresses
        }
        resp = requests.post(self.url+'/users', auth=HTTPBasicAuth(self.user, self.password), verify=False, data=json.dumps(data), headers=headers)
        if (self.debug):
            cyclosLogger.debug(LOG_HEADER + resp.text)
        if (not resp.ok):
            cyclosLogger.error(LOG_HEADER + email + " " + resp.text)
        return resp.text

    def getUserStatus(self, user):
        cyclosLogger.info(LOG_HEADER + '[-] '+'getUserStatus/'+user)
        resp = requests.get(self.url+'/'+user+'/status', auth=HTTPBasicAuth(self.user, self.password), verify=False)
        if (not resp.ok):
            cyclosLogger.error(LOG_HEADER + resp.text)
        if (self.debug):
            cyclosLogger.debug(LOG_HEADER + resp.text)

    def disableUser(self, user):
        cyclosLogger.info(LOG_HEADER + '[-] '+'disableUser/'+user)
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        data = {"status": "disabled"}
        resp = requests.post(self.url+'/'+user+'/status', auth=HTTPBasicAuth(self.user, self.password), verify=False, data=json.dumps(data), headers=headers)
        if (not resp.ok):
            cyclosLogger.error(LOG_HEADER + resp.text)
        if (self.debug):
            cyclosLogger.debug(LOG_HEADER + resp.text)

    def delUser(self, user):
        cyclosLogger.info(LOG_HEADER + '[-] '+'delUser/'+user)
        resp = requests.delete(self.url+'/users/'+user, auth=HTTPBasicAuth(self.user, self.password), verify=False)
        if (not resp.ok):
            cyclosLogger.error(LOG_HEADER + resp.text)
        if (self.debug):
            cyclosLogger.debug(LOG_HEADER + resp.text)

    def getPasswords(self, user):
        cyclosLogger.info(LOG_HEADER + '[-] '+'getPasswords/'+user)
        resp = requests.get(self.url+'/'+user+'/passwords', auth=HTTPBasicAuth(self.user, self.password), verify=False)
        if (not resp.ok):
            cyclosLogger.error(LOG_HEADER + resp.text)
        if (self.debug):
            cyclosLogger.debug(LOG_HEADER + resp.text)

    def setPaymentSystemtoUser(self, accountID, amount, description):
        cyclosLogger.info(LOG_HEADER + '[-] '+'setPaymentSystemtoUser/'+str(accountID)+'/'+str(amount)+'/'+description)
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        #id = self.getIdFromEmail(email)
        data = {'amount': amount, 'subject': accountID, 'type': 'debit.toUser', 'description': description}      
        #resp = requests.post(self.url+'/'+self.systemIDNEF+'/payments', auth=HTTPBasicAuth(self.user, self.password), verify=False, data=json.dumps(data), headers=headers)
        resp = requests.post(self.url+'/system/payments', auth=HTTPBasicAuth(self.user, self.password), verify=False, data=json.dumps(data), headers=headers)
        if (not resp.ok):
            cyclosLogger.error(LOG_HEADER + resp.text)
        if (self.debug):
            cyclosLogger.debug(LOG_HEADER + resp.text)
        return resp

    def getPayments(self, user):
        cyclosLogger.info(LOG_HEADER + '[-] '+'getPayments/'+user)
        resp = requests.get(self.url+'/'+user+'/payments/data-for-perform', auth=HTTPBasicAuth(self.user, self.password), verify=False)
        if (not resp.ok):
            cyclosLogger.error(LOG_HEADER + resp.text)
        if (self.debug):
            cyclosLogger.debug(LOG_HEADER + resp.text)
        return json.loads(resp.text)

    def getAddresses(self, user):
        cyclosLogger.info(LOG_HEADER + '[-] '+'getAddresses/'+user)
        resp = requests.get(self.url+'/'+user+'/addresses', auth=HTTPBasicAuth(self.user, self.password), verify=False)
        if (not resp.ok):
            cyclosLogger.error(LOG_HEADER + resp.text)
        if (self.debug):
            cyclosLogger.debug(LOG_HEADER + resp.text)


    def createAddress(self, user):
        cyclosLogger.info(LOG_HEADER + '[-] '+'createAddress/'+user)
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        data = {'name': 'Default', 'zip': '54200', 'city': 'Royaumeix', 'country': 'FR', 'defaultaddress': True, 'street': '10B rue d\'Alsace'}
        resp = requests.post(self.url+'/'+user+'/addresses', auth=HTTPBasicAuth(self.user, self.password), verify=False, data=json.dumps(data), headers=headers)
        if (not resp.ok):
            cyclosLogger.error(LOG_HEADER + resp.text)
        if (self.debug):
            cyclosLogger.debug(LOG_HEADER + resp.text)

    def setPaymentUsertoPro(self, user, pro, amount, description):
        cyclosLogger.info(LOG_HEADER + '[-] '+'setPaymentUsertoPro/'+user+'/'+pro+'/'+amount+'/'+description)
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        data = {'amount': amount, 'subject': pro, 'type': 'MBNPart.transfertUsertoPro', 'description': description}
        resp = requests.post(self.url+'/'+user+'/payments', auth=HTTPBasicAuth(self.user, self.password), verify=False, data=json.dumps(data), headers=headers)
        if (not resp.ok):
            cyclosLogger.error(LOG_HEADER + resp.text)
        if (self.debug):
            cyclosLogger.debug(LOG_HEADER + resp.text)

    def getTransactions(self, user):
        cyclosLogger.info(LOG_HEADER + '[-] '+'getTransactions/'+user)
        resp = requests.get(self.url+'/'+user+'/transactions', auth=HTTPBasicAuth(self.user, self.password), verify=False)
        if (not resp.ok):
            cyclosLogger.error(LOG_HEADER + resp.text)
        if (self.debug):
            cyclosLogger.debug(LOG_HEADER + resp.text)
        return json.loads(resp.text)

    def getTransfers(self):
        cyclosLogger.info(LOG_HEADER + '[-] '+'getTransfers')
        resp = requests.get(self.url+'/transfers', auth=HTTPBasicAuth(self.user, self.password), verify=False)
        if (not resp.ok):
            cyclosLogger.error(LOG_HEADER + resp.text)
        if (self.debug):
            cyclosLogger.debug(LOG_HEADER + resp.text)

    def displayJson(self, json_text):
        #cyclosLogger.info(LOG_HEADER + '[-] '+'putUser/'+email+'/'+data)
        json_object = json.loads(json_text)
        json_formatted_str = json.dumps(json_object, indent=2)
        print(json_formatted_str)

    def formatJson(self, json_text):
        json_object = json.loads(json_text)
        json_formatted_str = json.dumps(json_object, indent=2)
        return json_formatted_str

    def resetPassword(self, user):
        cyclosLogger.info(LOG_HEADER + '[-] '+'resetPassword/'+user)
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        data = {'w': 'email'}
        resp = requests.post(self.url+'/'+user+'/passwords/login/reset-and-send', auth=HTTPBasicAuth(self.user, self.password), verify=False, data=json.dumps(data), headers=headers)
        if (not resp.ok):
            cyclosLogger.error(LOG_HEADER + resp.text)
        if (self.debug):
            cyclosLogger.debug(LOG_HEADER + resp.text)

    def changePassword(self, user, oldpassword, newpassword):
        cyclosLogger.info(LOG_HEADER + '[-] '+'changePassword/'+user)
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        data = {'oldPassword': oldpassword, 'newPassword': newpassword, 'checkConfirmation': True, 'newPasswordConfirmation': newpassword, 'forceChange': True}
        print(data)
        resp = requests.post(self.url+'/'+user+'/passwords/login/change', auth=HTTPBasicAuth(self.user, self.password), verify=False, data=json.dumps(data), headers=headers)
        if (not resp.ok):
            cyclosLogger.error(LOG_HEADER + resp.text)
        if (self.debug):
            cyclosLogger.debug(LOG_HEADER + resp.text)

    def enablePassword(self, user):
        cyclosLogger.info(LOG_HEADER + '[-] '+'putUser/'+user)
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        data = {}
        resp = requests.post(self.url+'/'+user+'/passwords/login/enable', auth=HTTPBasicAuth(self.user, self.password), verify=False, data=json.dumps(data), headers=headers)
        if (not resp.ok):
            cyclosLogger.error(LOG_HEADER + resp.text)
        if (self.debug):
            cyclosLogger.debug(LOG_HEADER + resp.text)

    def disablePassword(self, user):
        cyclosLogger.info(LOG_HEADER + '[-] '+'putUser/'+user)
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        data = {}
        resp = requests.post(self.url+'/'+user+'/passwords/login/disable', auth=HTTPBasicAuth(self.user, self.password), verify=False, data=json.dumps(data), headers=headers)
        if (not resp.ok):
            cyclosLogger.error(LOG_HEADER + resp.text)
        if (self.debug):
            cyclosLogger.debug(LOG_HEADER + resp.text)

    def allowGeneratePassword(self, user):
        cyclosLogger.info(LOG_HEADER + '[-] '+'allowGeneratePassword/'+user)
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        data = {}
        resp = requests.post(self.url+'/'+user+'/passwords/login/allow-generation', auth=HTTPBasicAuth(self.user, self.password), verify=False, data=json.dumps(data), headers=headers)
        if (not resp.ok):
            cyclosLogger.error(LOG_HEADER + resp.text)
        if (self.debug):
            cyclosLogger.debug(LOG_HEADER + resp.text)

    def generatePassword(self):
        cyclosLogger.info(LOG_HEADER + '[-] '+'generatePassword')
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        data = {}
        resp = requests.post(self.url+'/passwords/login/generate', auth=HTTPBasicAuth(self.user, self.password), verify=False, data=json.dumps(data), headers=headers)
        if (not resp.ok):
            cyclosLogger.error(LOG_HEADER + resp.text)
        if (self.debug):
            cyclosLogger.debug(LOG_HEADER + resp.text)
        print (resp.text)     

    def getPasswords(self, user):
        cyclosLogger.info(LOG_HEADER + '[-] '+'putUser/'+user)
        resp = requests.get(self.url+'/'+user+'/passwords/login', auth=HTTPBasicAuth(self.user, self.password), verify=False)
        if (not resp.ok):
            cyclosLogger.error(LOG_HEADER + resp.text)
        if (self.debug):
            cyclosLogger.debug(LOG_HEADER + resp.text)
