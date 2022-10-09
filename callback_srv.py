#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import logging
import os
import re
import time
import json
from logging.handlers import RotatingFileHandler
import threading  # launch server in a thread
import requests  # make http request to shutdown web server
from flask import Flask
from flask import request
import time, signal
from cherrypy import wsgiserver
from filelock import FileLock
from mollie import Mollie
from Odoo2Cyclos import Odoo2Cyclos

LOG_HEADER = " [" + __file__ + "] - "
p = re.compile("\w+(\d)")
LOG_PATH = os.path.dirname(os.path.abspath(__file__)) + '/log/'
logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
webLogger = logging.getLogger('callback_srv')
webLogger.setLevel(logging.DEBUG)
webLogger.propagate = False
fileHandler = RotatingFileHandler("{0}/{1}.log".format(LOG_PATH, 'callback_srv'), maxBytes=2000000,
                                  backupCount=1500)
fileHandler.setFormatter(logFormatter)
webLogger.addHandler(fileHandler)

app = Flask(__name__)
mo = Mollie()
o2c = Odoo2Cyclos()

@app.route('/')
def getPaiements():
    webLogger.info(LOG_HEADER + '[/] GET')
    with FileLock("myfile.txt"):
        mo.setTransactionstoCyclos()
        return '200'

@app.route('/', methods=['POST'])
def postPaiements():
    webLogger.info(LOG_HEADER + '[/] POST')
    with FileLock("myfile.txt"):
        mo.setTransactionstoCyclos()
        return '200'

@app.route('/paiement', methods=['POST'])
def paiement():
    webLogger.info(LOG_HEADER + '[/paiement] POST')
    data = request.form.to_dict()
    #print(data, request, type(request))
    with FileLock("myfile.txt"):
        mo.setTransactionstoCyclos()
        return '200'

@app.route('/allow/<string:argkey>')
def changeCyclos(argkey):
    webLogger.info(LOG_HEADER + '[/allow/'+argkey+'] GET')
    with open(os.path.dirname(os.path.abspath(__file__))+"/url.key") as keysjsons:
        arr = json.loads(keysjsons.read())
        for key, value in arr.items():
            #print(key+" "+value)
            if (argkey == key):
                if (re.match('\d{8}-\d{6}-adhpros-changes\.json', value) is not None):
                    webLogger.info(LOG_HEADER + 'o2c apply adhpros '+value)
                    print('o2c apply adhpros '+value)
                    o2c.applyChangesAdhPros(value)
                else:
                    webLogger.info(LOG_HEADER + 'o2c apply adhs '+value)
                    o2c.applyChangesAdhs(value)
                print("OK - "+value)
                # todo : apply json
                # todo : delete filename from json
                return "200"
    return "503"

d = wsgiserver.WSGIPathInfoDispatcher({'/': app})
server = wsgiserver.CherryPyWSGIServer(('0.0.0.0', 80), d)

if __name__ == '__main__':
    try:
        webLogger.info(LOG_HEADER + '[starting server]')
        server.start()
    except KeyboardInterrupt:
        webLogger.info(LOG_HEADER + '[stopping server]')
        server.stop()
