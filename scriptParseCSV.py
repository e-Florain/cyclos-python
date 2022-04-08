import csv
import json
import psycopg2
import config as cfg

def parsePart(statusmembership="active"):
    results=[]
    assos = loadAssos()
    with open('AdhFlorain_Part3.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        i=0
        for row in reader:
            #print(i)
            temp={}
            if (statusmembership == "active"):
                if ((row[4] != "") and (row[4] != "X") and (row[3] != "")):
                    temp['Référence interne'] = row[0]
                    temp['Nom'] = row[4]
                    temp['Prénom'] = row[5]
                    temp['Téléphone'] = row[8].replace('.', '')
                    temp['Courriel'] = row[7]
                    temp['Membre libre'] = "Non"
                    if (row[9] == "31"):
                        row[9] = "0"
                    if (row[9] == ""):
                        row[9] = "0"
                    temp['Asso'] = assos[row[9]]
                    results.append(temp)
            else:
                if ((row[4] != "") and (row[4] != "X") and (row[3] == "")):
                    temp['Référence interne'] = row[0]
                    temp['Nom'] = row[4]
                    temp['Prénom'] = row[5]
                    temp['Téléphone'] = row[8].replace('.', '')
                    temp['Courriel'] = row[7]
                    temp['Membre libre'] = "Non"
                    if (row[9] == "31"):
                        row[9] = "0"
                    if (row[9] == ""):
                        row[9] = "0"
                    temp['Asso'] = assos[row[9]]
                    results.append(temp)
            i+=1
    #for result in results:
    #    if (len(result) > 0):
    #        print(result)
    return results

def exportResults(results, filename):
    with open(filename, 'w') as f:
        keys=results[3].keys()
        #print(keys)
        for key in keys:
            f.write("%s," % key)
        f.write("\n")
        for result in results:
            for key in keys:
                if (len(result) > 0):
                    #print(result)
                    f.write("%s," % result[key])
            if (len(result) > 0):
                f.write("\n")

def parsePro(statusmembership="active"):
    results=[]
    with open('AdhFlorain_Pro3.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            temp={}
            if (statusmembership == "active"):
                if ((row[5] != "") and (row[5] != "X") and (row[4] != "")):
                    temp['Nom'] = row[5]
                    temp['Notes'] = row[8]
                    temp['Rue'] = row[9].replace(',', '');
                    temp['Code postal'] = row[10]
                    temp['Ville'] = row[11]
                    temp['Téléphone'] = row[12]
                    temp['Courriel'] = row[13]
                    temp['Membre libre'] = "Non"   
                    temp['Est une entreprise'] = "1"
                    if (row[13] == "association"):
                        temp['Est une association'] = "1"
                    else:
                        temp['Est une association'] = "0"
                    #print(temp)
                    results.append(temp)
            else:
                if ((row[5] != "") and (row[5] != "X") and (row[4] == "")):
                    temp['Nom'] = row[5]
                    temp['Notes'] = row[8]
                    temp['Rue'] = row[9].replace(',', '');
                    temp['Code postal'] = row[10]
                    temp['Ville'] = row[11]
                    temp['Téléphone'] = row[12]
                    temp['Courriel'] = row[13]
                    temp['Membre libre'] = "Non"
                    temp['Est une entreprise'] = "1"
                    if (row[13] == "association"):
                        temp['Est une association'] = "1"
                    else:
                        temp['Est une association'] = "0"
                    #print(temp)
                    results.append(temp)
    return results

def getOdooAdhs():
    connection = connect()
    if (connection != None):
        try:
            with connection.cursor() as cursor:
                sql = "SELECT id,ref from res_partner where is_company='f' and active='t' and membership_state='waiting'"
                #print(sql)
                cursor.execute(sql)
                resultsSQL = cursor.fetchall()

                cursor.execute("SELECT * from res_partner LIMIT 0")
                colnames = [desc[0] for desc in cursor.description]
                return (colnames, resultsSQL)
        finally:
            connection.close()

def connect():
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # connect to the PostgreSQL server
        conn = psycopg2.connect(
            host="localhost",
            user=cfg.db['user'],
            password=cfg.db['password'],
            database=cfg.db['name'])
        return conn        
    except (Exception, psycopg2.DatabaseError) as error:
        print(str(error))

def parseOdooAdhs():
    results=[]
    adhs = getOdooAdhs()
    for adh in adhs[1]:
        temp={}
        temp['ref'] = adh[1]
        temp['id'] = adh[0]
        results.append(temp)
    #print (results)
    return results

def loadAssos():
    with open("associations.json") as data_file:
        data = json.load(data_file)
        #print(data)
        return data


""" def updateOdooAdhsMemberships(adhsodoo, adhscsv):
    connection = connect()
    for adhcsv in adhscsv:
        if 'Montant' in adhcsv:
            if (adhcsv['Montant'] != ''):
                amount = int(adhcsv['Montant'].replace('€', ''))
                ref = adhcsv['Référence interne']
                #print(ref+" "+str(amount))
                for adhodoo in adhsodoo:
                    #print("odoo "+adhodoo['ref'])
                    if (str(ref) == str(adhodoo['ref'])):
                        #print(str(adhodoo['id'])+' '+ref)
                        sql = "update account_invoice set amount_untaxed="+str(amount)+" where partner_id="+str(adhodoo['id'])+";"
                        print(sql)
                        sql = "update account_invoice set amount_untaxed_signed="+str(amount)+" where partner_id="+str(adhodoo['id'])+";"
                        print(sql)
                        sql = "update account_invoice set amount_total="+str(amount)+" where partner_id="+str(adhodoo['id'])+";"
                        print(sql)
                        sql = "update account_invoice set amount_total_signed="+str(amount)+" where partner_id="+str(adhodoo['id'])+";"
                        print(sql)
                        sql = "update account_invoice set amount_total_company_signed="+str(amount)+" where partner_id="+str(adhodoo['id'])+";"
                        print(sql)
                        sql = "update account_invoice set residual="+str(amount)+" where partner_id="+str(adhodoo['id'])+";"
                        print(sql)
                        sql = "update account_invoice set residual_signed="+str(amount)+" where partner_id="+str(adhodoo['id'])+";"
                        print(sql)
                        sql = "update account_invoice set residual_company_signed="+str(amount)+" where partner_id="+str(adhodoo['id'])+";"
                        print(sql)
                        #if (connection != None):
                        #    try:
                        #        with connection.cursor() as cursor:
                        #            cursor.execute(sql)
                        #    finally:
                        #        connection.close()
                #print(sql)
                #cursor.execute(sql) """

if __name__ == '__main__':
    adhscsv = parsePart("active")
    exportResults(adhscsv, "eggs2022.csv")
    adhscsv = parsePart("false")
    exportResults(adhscsv, "eggs.csv")
    adhspro = parsePro("active")
    exportResults(adhspro, "eggspros2022.csv")
    adhspro = parsePro("false")
    exportResults(adhspro, "eggspros.csv")
    
    #adhsodoo = parseOdooAdhs()
    #updateOdooAdhsMemberships(adhsodoo, adhscsv)