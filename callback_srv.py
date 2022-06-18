#!/usr/bin/env python

import sys
import logging
import os
import re
import time
from logging.handlers import RotatingFileHandler
import threading  # launch server in a thread
import requests  # make http request to shutdown web server
from flask import Flask
from flask import request
import time, signal
from cherrypy import wsgiserver
from helloasso import HelloAsso
from filelock import FileLock
from mollie import Mollie

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
ha = HelloAsso()
mo = Mollie()

@app.route('/')
def hello_world():
    webLogger.info(LOG_HEADER + '[/] GET')
    #ha.setTransactionstoCyclos()
    mo.setTransactionstoCyclos()
    return 'Check Paiments - 200 - OK'

@app.route('/paiement', methods=['POST'])
def paiement():
    data = request.form.to_dict()
    #print(data, request, type(request))
    with FileLock("myfile.txt"):
        ha.getToken()
        webLogger.info(LOG_HEADER + '[/paiement] POST')
        ha.setTransactionstoCyclos()
        mo.setTransactionstoCyclos()
        return "200 - OK"

d = wsgiserver.WSGIPathInfoDispatcher({'/': app})
server = wsgiserver.CherryPyWSGIServer(('0.0.0.0', 80), d)

if __name__ == '__main__':
    try:
        webLogger.info(LOG_HEADER + '[starting server]')
        server.start()
    except KeyboardInterrupt:
        webLogger.info(LOG_HEADER + '[stopping server]')
        server.stop()
