import Ordrin

Ordrin.api.initialize("GO-G43js4BGzQP2Ku8bTaA", "https://u-test.ordr.in/")
Ordrin.api.setCurrAcct("markisus@gmail.com", "password")
addr = Ordrin.Address("65 School Road East", "Marlboro", "07746", "", "NJ", "5551231234", "")
Ordrin.u.updateCard("cc", "Mark Liu", "3566007770007321", "123", "12", "2014", addr)
#Ordrin.o.submit_less(restid="207", tray="375710/1", tip="0", first_name="Mark", last_name="Liu", dDate="10-03", dTime="13:00", address_nick="Texas", card_nick="cc")