import Ordrin

Ordrin.api.initialize("GO-G43js4BGzQP2Ku8bTaA", "https://u-test.ordr.in/")
Ordrin.api.setCurrAcct("markisus@gmail.com", "password")
place = Ordrin.Address("65 School Road East", "Marlboro", "07746", "", "NJ", "5551231234", "home")

result2 = Ordrin.u.updateCard("cc", "My card", "378282246310005", "123", "10", "2014", place)
print("\n\n" + result2)