#!/usr/bin/python3
# -*- coding: utf-8 -*-

import pymysql
import pymysql.cursors
import cyclos
import argparse
from cyclos import Cyclos
import re
import os
import unidecode
import json
import config as cfg

def connect():
    connection = pymysql.connect(host='localhost',
        user=cfg.db['user'],
        password=cfg.db['password'],
        db=cfg.db['name'],
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor)
    return connection


def syncAdhs(connection, cyclos):
    try:
        with connection.cursor() as cursor:
            # Create a new record
            sql = "SELECT * from adhs"
            cursor.execute(sql)
            results = cursor.fetchall()
            for result in results:
                print(result)
                username = result["firstname"][0].lower()+result["lastname"].lower()
                result_json = cyclos.addUser(username, result["firstname"]+" "+result["lastname"], result["email"])
                result = json.loads(result_json)
                if "user" in result:
                    id = result["user"]["id"]
                    cyclos.resetPassword(id)
                    print(id)
                else:
                    if "username" in result["propertyErrors"]:
                        err = result["propertyErrors"]["username"][0]
                        if (re.match(".*unique.*", err)):
                            print("Utilisateur deja existant")
                            users_json = cyclos.getUsers()
                            users = json.loads(users_json)
                            print(users)

    finally:
        connection.close()

#
#
# changesDB = array(
# mail => array(
#       'dbtochange' => sql or cyclos
#       'fieldtochange' => 
#       'lastmodified' =>
#       'oldvalue' =>
#       'newvalue' =>
#       'type' => create or modify
#   )
# )
#
def getChangesAdhPros(connection, cyclos):
    changesDB = dict()
    listUsersSQL = getUserSQL()
    #print(listUsersSQL)
    listUsersCyclos = getUsersCyclos(cyclos, "MBN_Pros")
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
                #if (not simulate):
                #    result_json = cyclos.addPro(v["adh_id"], unaccented_string, v["email"], addresses)
                #    result = json.loads(result_json)
                #    if "user" in result:
                #        id = result["user"]["id"]
                #        cyclos.resetPassword(id)
                #        print (id)
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
    with open(os.path.dirname(os.path.abspath(__file__)) +'/json/changes.json', 'w') as outfile:
        json.dump(changesDB, outfile, indent=4, sort_keys=False, separators=(',', ':'))

def applyChangesAdhPros(connection, cyclos):
    with open(os.path.dirname(os.path.abspath(__file__)) +'/json/changes.json') as data_file:
        datas = json.load(data_file)
        for k, v in datas.items():
            for changes in v:
                if (changes['dbtochange'] == "cyclos"):
                    if (changes['type'] == "delete"):
                        print("delete "+k)
                        id = cyclos.getIdFromEmail(k)
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
                        result_json = cyclos.addPro(infos['adh_id'], infos['name'], infos['email'], infos['addresses'])
                        print (result_json)
            #break
            #print(k)
            #print(v)


def getUserSQL():
    listusers=dict()
    try:
        with connection.cursor() as cursor:
            # Create a new record
            sql = "SELECT * from adhpros"
            cursor.execute(sql)
            results = cursor.fetchall()
            #print(results)
            for result in results:
                #print (result["cyclos_account"])
                listusers[result['email']] = result
            return listusers
    finally:
        connection.close()
    

def getUsersCyclos(cyclos, group):
    listusers=dict()
    users = cyclos.getUsers(group)
    for user in users:
        #print user
        userinfo = cyclos.getUser(user['id'])
        #print (userinfo)
        #print (user['shortDisplay'])
        listusers[user['shortDisplay']] = userinfo
    return listusers

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-apply", help="applique la synchronisation précédément simulée",
        action="store_true")
    #parser.add_argument("-days", help="efface les messages plus vieux que le nombre de jours precises", type=int)
    parser.add_argument("-simulate", help="simule et affiche la liste des informations qui seront modifées",
        action="store_true")
    args = parser.parse_args()
    if args.apply:
        apply = True
    else:
        apply = False
    if args.simulate:
        simulate = True
    else:
        simulate = False
    connection = connect()
    cyclos = Cyclos()
    if (simulate):
        getChangesAdhPros(connection, cyclos)
    if (apply):
        applyChangesAdhPros(connection, cyclos)