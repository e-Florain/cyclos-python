#!/usr/bin/python3
# -*- coding: utf-8 -*-

import pymysql
import pymysql.cursors
import cyclos
from cyclos import Cyclos
import re
import unidecode
import json

def connect():
    connection = pymysql.connect(host='localhost',
        user='root',
        password='xxxx',
        db='florain',
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
                    print id
                else:
                    if "username" in result["propertyErrors"]:
                        err = result["propertyErrors"]["username"][0]
                        if (re.match(".*unique.*", err)):
                            print "Utilisateur deja existant"
                            users_json = cyclos.getUsers()
                            users = json.loads(users_json)
                            print  

    finally:
        connection.close()

def syncAdhpros(connection, cyclos):
    try:
        with connection.cursor() as cursor:
            # Create a new record
            sql = "SELECT * from adhpros"
            cursor.execute(sql)
            results = cursor.fetchall()
            for result in results:
                print(result)
                unaccented_string = unidecode.unidecode(result["orga_name"])
                username = re.sub('[^A-Za-z0-9]+', '', unaccented_string).lower()
                username = (username[:16]) if len(username) > 16 else username
                #username = result["orga_name"][0].lower()+result["orga_name"][1:].lower()
                print "username "+username
                print len(username)
                addresses = [
                    {
                    "name": "Siege Social",
                    "street": result["address"],
                    "zip": result["postcode"],
                    "city": result["city"],
                    "country": "FR",
                    "defaultAddress": True
                    }
                ]
                #print addresses
                result_json = cyclos.addPro(result["adh_id"], username, result["email"], addresses)
                result = json.loads(result_json)
                if "user" in result:
                    id = result["user"]["id"]
                    cyclos.resetPassword(id)
                    print id
    finally:
        connection.close()

connection = connect()
cyclos = Cyclos()
#syncAdhpros(connection, cyclos)
syncAdhs(connection, cyclos)
#cyclos.getPasswords("GROTest01")

#cyclos.changePassword("larbrevike","", "1234")
#cyclos.changePassword("ledomainedessave","", "1234")
#cyclos.enablePassword("ledomainedessave")
#cyclos.getPasswords("larbrevike")
#cyclos.getUsers()
#cyclos.getUser("4190760854218714008")
#cyclos.resetPassword("4190760854218714008")
#cyclos.getPasswords("4190760854218714008")

#syncAdhs(connection, cyclos)
#cyclos.getPasswords("larbrevike")
#cyclos.resetPassword("larbrevike")

#curl --user adminAPI:1234 -XGET "http://192.168.100.5:8080/api/larbrevike/passwords/login"
#
#cyclos.setPaymentSystemtoUser("goroche", 50)