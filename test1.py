import Ordrin, sys

Ordrin.api.initialize("GO-G43js4BGzQP2Ku8bTaA", "https://u-test.ordr.in")

user = raw_input("Username:");

Ordrin.u.makeAcct(user, "password", "John", "Doe");

# print Ordrin.u.getAddress("home")
