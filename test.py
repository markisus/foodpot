# Demo app to illustrate Python API functionality

import Ordrin, sys

print "Ordrin Python API Demo"

# remainder of app self-explanatory

Ordrin.api.initialize("GO-G43js4BGzQP2Ku8bTaA", "https://u-test.ordr.in")

uname = sys.argv[1]
  
# Ordrin.u.makeAcct(uname, "password", "fName", "lName")
Ordrin.api.setCurrAcct(uname, "password");
result = Ordrin.u.getCard("");

print result

# user()