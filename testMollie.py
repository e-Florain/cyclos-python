#!/usr/bin/python3
# -*- coding: utf-8 -*-
from mollie import Mollie

mo = Mollie()
mo.setTransactionstoCyclos()
#mo.get_old_payments()