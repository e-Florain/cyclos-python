#!/usr/bin/python3
# -*- coding: utf-8 -*-

import psycopg2
import os
from cyclos import Cyclos
import argparse
import logging
from logging.handlers import RotatingFileHandler
import time
import unidecode
import json
import config as cfg

cyclosgrppro = "professionnels"
cyclosgrppart = "particuliers"

pgsql_headers = {
    "firstname": 50,
    "lastname": 51,
    "email": 29,
    "account_cyclos": 103
}

LOG_HEADER = " [" + __file__ + "] - "
LOG_PATH = os.path.dirname(os.path.abspath(__file__)) + '/log/'
logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
cyclosLogger = logging.getLogger('sync')
cyclosLogger.setLevel(logging.DEBUG)
cyclosLogger.propagate = False
fileHandler = RotatingFileHandler("{0}/{1}.log".format(LOG_PATH, 'sync'), maxBytes=2000000,
                                  backupCount=1500)
fileHandler.setFormatter(logFormatter)
cyclosLogger.addHandler(fileHandler)

def connect():
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # connect to the PostgreSQL server
        cyclosLogger.info(LOG_HEADER + '[-] '+'Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(
            host="localhost",
            user=cfg.db['user'],
            password=cfg.db['password'],
            database=cfg.db['name'])
        return conn
        
    except (Exception, psycopg2.DatabaseError) as error:
        cyclosLogger.error(LOG_HEADER + error)

def syncAdhs(connection, cyclos):
    """ Sync Adhs """
    cyclosLogger.info(LOG_HEADER + '[-] '+'Sync adhs ...')
    try:
        with connection.cursor() as cursor:
            # Create a new record
            sql = "SELECT * from res_partner where is_company='f';"
            cursor.execute(sql)
            resultsSQL = cursor.fetchall()
            for resultSQL in resultsSQL:
                #print(resultSQL)
                #print (resultSQL[50])
                result = {}
                if ((resultSQL[pgsql_headers['firstname']] != None) and (resultSQL[pgsql_headers['lastname']] != None)):
                    username = resultSQL[pgsql_headers['firstname']][0].lower()+resultSQL[pgsql_headers['lastname']].lower()
                    print(username)
                    #result_json = cyclos.addUser(username, result["firstname"]+" "+result["lastname"], result["email"])
                    #result = json.loads(result_json)
                    if "user" in result:
                        id = result["user"]["id"]
                        #cyclos.resetPassword(id)
                        print(id)
                    else:
                        if "propertyErrors" in result:
                            if "username" in result["propertyErrors"]:
                                err = result["propertyErrors"]["username"][0]
                                if (re.match(".*unique.*", err)):
                                    print("Utilisateur deja existant")
                                    # users_json = cyclos.getUsers()
                                    users = json.loads(users_json)
                                    print(users)
    finally:
        connection.close()


def getChangesAdhs(connection, cyclos):
    cyclosLogger.info(LOG_HEADER + '[-] '+'getChangesAdhs')
    changesDB = dict()
    listUsersSQL = getUserSQL("adhs")
    #print(listUsersSQL)
    listUsersCyclos = getUsersCyclos(cyclos, cyclosgrppart)
    #print(listUsersCyclos)
    for k, v in listUsersCyclos.items():
        #print(k)
        #print(v)
        if (k not in listUsersSQL):
            #print("DELETE")
            #print(k)
            changes = dict()
            listchanges = list()
            changes['dbtochange'] = 'cyclos'
            changes['type'] = 'delete'
            listchanges.append(changes)
            changesDB[k] = listchanges
        #break
    for k, v in listUsersSQL.items():
        #print("CREATE "+k)
        if (v[pgsql_headers['account_cyclos']]):
            if (k not in listUsersCyclos):
                #print("CREATE")
                #print(v)    
                lastname_unaccented = unidecode.unidecode(v[pgsql_headers['lastname']])
                firstname_unaccented = unidecode.unidecode(v[pgsql_headers['firstname']])
                changes = dict()
                listchanges = list()
                changes['type'] = 'create'
                changes['dbtochange'] = 'cyclos'
                infostocreate = dict()
                infostocreate['email'] = v[pgsql_headers['email']]
                #infostocreate['adh_id'] = v['adh_id']
                infostocreate['name'] = firstname_unaccented+" "+lastname_unaccented
                changes['infos'] = infostocreate
                listchanges.append(changes)
                changesDB[k] = listchanges
            else:
                #print("COMPARE")
                changed = False
                changes = dict()
                listchanges = list()
                lastname_unaccented = unidecode.unidecode(v[pgsql_headers['lastname']])
                firstname_unaccented = unidecode.unidecode(v[pgsql_headers['firstname']])
                name = firstname_unaccented+" "+lastname_unaccented
                if (name != unidecode.unidecode(listUsersCyclos[k]["display"])):
                    #print (listUsersCyclos[k]["display"])
                    changes['field'] = 'display'
                    changes['newvalue'] = unidecode.unidecode(v["orga_name"])
                    changes['oldvalue'] = unidecode.unidecode(listUsersCyclos[k]["display"])
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

def getChangesAdhPros(connection, cyclos):
    cyclosLogger.info(LOG_HEADER + '[-] '+'getChangesAdhPros')
    changesDB = dict()
    listUsersSQL = getUserSQL("adhpros")
    #print(listUsersSQL)
    listUsersCyclos = getUsersCyclos(cyclos, cyclosgrppro)
    #print(listUsersCyclos)
    for k, v in listUsersCyclos.items():
        #print(k)
        #print(v)
        if (k not in listUsersSQL):
            #print("DELETE")
            #print(k)
            changes = dict()
            listchanges = list()
            changes['dbtochange'] = 'cyclos'
            changes['type'] = 'delete'
            listchanges.append(changes)
            changesDB[k] = listchanges
        #break
    for k, v in listUsersSQL.items():
        #print("CREATE "+k)
        if (v["cyclos_account"]):
            if (k not in listUsersCyclos):
                #print("CREATE")         
                unaccented_string = unidecode.unidecode(v["orga_name"])
                addresses = [
                    {
                    "name": "Siege Social",
                    "street": v["address"],
                    "zip": v["postcode"],
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
                infostocreate['adh_id'] = v['adh_id']
                infostocreate['name'] = unaccented_string
                addresses = [
                    {
                        "name": "Siege Social",
                        "street": v['address'],
                        "zip": v['postcode'],
                        "city": v['city'],
                        "country": "FR",
                        "defaultAddress": True
                    }
                ]
                infostocreate['addresses'] = addresses
                changes['infos'] = infostocreate
                listchanges.append(changes)
                changesDB[k] = listchanges
            else:
                #print("COMPARE")
                changed = False
                changes = dict()
                listchanges = list()
                if (unidecode.unidecode(v["orga_name"]) != unidecode.unidecode(listUsersCyclos[k]["display"])):
                    #print (listUsersCyclos[k]["display"])
                    changes['field'] = 'display'
                    changes['newvalue'] = unidecode.unidecode(v["orga_name"])
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

def applyChangesAdhPros(connection, cyclos):
    cyclosLogger.info(LOG_HEADER + '[-] '+'applyChangesAdhPros')
    with open(os.path.dirname(os.path.abspath(__file__)) +'/json/'+jsonfile) as data_file:
        datas = json.load(data_file)
        for k, v in datas.items():
            for changes in v:
                if (changes['dbtochange'] == "cyclos"):
                    if (changes['type'] == "delete"):
                        print("delete "+k)
                        id = cyclos.getIdFromEmail(k)
                        if (id == False):
                             cyclosLogger.info(LOG_HEADER + '[-] impossible de trouver '+k)
                        else:
                            cyclos.disableUser(id)
                    if (changes['type'] == "modify"):
                        print("modify "+k)
                        #id = cyclos.getIdFromEmail(k)
                        #data={changes['field']: changes['newvalue']}
                        data={"name": changes['newvalue'], "username": k, "email": k, "hiddenFields": "", "customValues": {}}
                        cyclos.putUser(k, data)
                    if (changes['type'] == "create"):
                        print("create "+k)
                        infos = changes['infos']
                        result_json = cyclos.addPro(infos['adh_id'], infos['name'], infos['email'], infos['addresses'])
                        print (result_json)

def applyChangesAdhs(connection, cyclos):
    cyclosLogger.info(LOG_HEADER + '[-] '+'applyChangesAdhs')
    with open(os.path.dirname(os.path.abspath(__file__)) +'/json/'+jsonfile) as data_file:
        datas = json.load(data_file)
        for k, v in datas.items():
            for changes in v:
                if (changes['dbtochange'] == "cyclos"):
                    if (changes['type'] == "delete"):
                        print("delete "+k)
                        id = cyclos.getIdFromEmail(k)
                        if (id == False):
                             cyclosLogger.info(LOG_HEADER + '[-] impossible de trouver '+k)
                        else:
                            cyclos.disableUser(id)
                    if (changes['type'] == "modify"):
                        print("modify "+k)
                        #id = cyclos.getIdFromEmail(k)
                        #data={changes['field']: changes['newvalue']}
                        data={"name": changes['newvalue'], "username": k, "email": k}
                        cyclos.putUser(k, data)
                    if (changes['type'] == "create"):
                        print("create "+k)
                        infos = changes['infos']
                        result_json = cyclos.addUser(infos['email'], infos['name'], infos['email'])
                        #print (result_json)

def getUserSQL(type):
    cyclosLogger.info(LOG_HEADER + '[-] '+'getUserSQL '+type)
    listusers=dict()
    try:
        with connection.cursor() as cursor:
            if (type == "adhs"):
                sql = "SELECT * from res_partner where active='t' and account_cyclos='t' and is_company='f'"
            if (type == "adhpros"):
                sql = "SELECT * from res_partner where active='t' and account_cyclos='t' and is_company='t'"
            cursor.execute(sql)
            resultsSQL = cursor.fetchall()
            for resultSQL in resultsSQL:
                #print(resultSQL)
                if (resultSQL[pgsql_headers['email']] != None):
                    listusers[resultSQL[pgsql_headers['email']]] = resultSQL
            return listusers
    finally:
        connection.close()


def getUsersCyclos(cyclos, group):
    cyclosLogger.info(LOG_HEADER + '[-] '+'getUsersCyclos')
    listusers=dict()
    users = cyclos.getUsers(group)
    #print(users)
    for user in users:
        userinfo = cyclos.getUser(user['id'])
        listusers[user['email']] = userinfo
    return listusers

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-p", "--adhpros", action="store_true")
    group.add_argument("-a", "--adhs", action="store_true")
    parser.add_argument("-apply", type=str, help="applique la synchronisation du json fournie en parametre")
    parser.add_argument("-simulate", help="simule et affiche la liste des informations qui seront modifées",
        action="store_true")
    args = parser.parse_args()
    if args.apply:
        apply = True
        jsonfile = args.apply
        #jsonfile = args.jsonfile
    else:
        apply = False
    if args.simulate:
        simulate = True
    else:
        simulate = False
    connection = connect()
    cyclos = Cyclos()
    if (simulate):
        if (args.adhpros):
            getChangesAdhPros(connection, cyclos)
        if (args.adhs):
            getChangesAdhs(connection, cyclos)
    if (apply):
        if (args.adhpros):
            applyChangesAdhPros(connection, cyclos)
        if (args.adhs):
            applyChangesAdhs(connection, cyclos)


#if __name__ == '__main__':
#    conn = connect()
#    cyclos = "test"
#    syncAdhs(conn, cyclos)