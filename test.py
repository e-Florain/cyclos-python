import cyclos
from cyclos import Cyclos

cyclos = Cyclos()
#cyclos.getUsers()

#OK
#cyclos.getPayments("system")

#NOK
#cyclos.getAddresses("Mirabio")

#NOK
#yclos.createAddress("Mirabio")

#OK
#cyclos.addUser()

#NOK
cyclos.setPaymentSystemtoUser("GROTest01")

#OK
#cyclos.setPaymentUsertoPro("GROTest01", "Mirabio", "40", "this is a test")

#OK
#cyclos.getTransfers()