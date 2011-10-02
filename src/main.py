import os.path
import Ordrin
import time
import random
import json
import urllib2
import tornado.ioloop
import tornado.web
import tornado.template

loader = tornado.template.Loader(os.path.join(os.path.dirname(__file__), "res", "templates"))

#Constants
restid = "207"
tray="375710/1"
tip="0"
dDate="10-03"
dTime="13:00"
api_key = "GO-G43js4BGzQP2Ku8bTaA"

#The foodpot keeps track of how much money is available
class FoodPot:
    def __init__(self):
        self.amount = 0
    
    def add_amount(self, amount):
        self.amount += amount
        
    def subtract_amount(self, amount):
        self.amount -= amount
        if self.amount < 0:
            self.amount += amount
            raise ValueError("This makes the pot negative")

foodpot = FoodPot()

class MainPage(tornado.web.RequestHandler):
    def get(self):
        print("Inside main page!")
        self.write(loader.load("index.html").generate(test="Test"))

listener_callbacks = []

class Order(tornado.web.RequestHandler):
    #Placeholder for testing purposes
    def get(self):
        self.post()
    
    def post(self):
        username = self.get_argument("username")
        password = self.get_argument("password")
        address_nick = self.get_argument("address_nick")
        card_nick = self.get_argument("card_nick")
        
        order_amount = 1000
        if foodpot.amount > order_amount:
            #Make the order with the company's CC
            #First ask for the user's address
            Ordrin.api.initialize(api_key, "https://u-test.ordr.in/")
            Ordrin.api.setCurrAcct(username, password)
            addr_json = Ordrin.u.getAddress(address_nick)
            
            Ordrin.api.initialize(api_key, "https://o-test.ordr.in/")            
            #Log in as Mark and pay for the user's meal
            Ordrin.api.setCurrAcct("marksisus@gmail.com", "password")
            result = Ordrin.o.submit_complete(restid, tray, tip, dDate, dTime, card_nick, 
                                              addr=addr_json['addr'], 
                                              city=addr_json['city'], 
                                              state=addr_json['state'], 
                                              zip=addr_json['zip'], 
                                              phone=addr_json['phone'])
            #Todo:Check for errors
            foodpot.subtract_amount(order_amount)
            self.write("10")            
            
        else:
                
            #Make the order with the user's CC
            Ordrin.api.initialize(api_key, "https://o-test.ordr.in/")
            Ordrin.api.setCurrAcct(username, password)            
            Ordrin.o.submit_less(restid, tray, tip, dDate, dTime, card_nick, address_nick)
            foodpot.add_amount(int(order_amount*.01))
            
            self.write("00")
            
        while listener_callbacks:
            callback = listener_callbacks.pop()
            print("Notifying listener " + str(callback.id))
            callback.notify(foodpot.amount)

class ListenRandomizer(tornado.web.RequestHandler):
    def get(self):
        randomstring = str(time.time()).replace(".", "") + str(random.randint(0,9999999))
        print("In randomizer... => " + randomstring)
        self.redirect("/listen/" + randomstring +"/")
   
class ListenPot(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self, unique_string):
        self.id = unique_string
        print("Unique listener: " + str(unique_string))
        listener_callbacks.append(self)
    
    def notify(self, amount):
        if self.request.connection.stream.closed() or self._finished:
            return
        self.write(str(amount))
        self.finish()

class CurrentPot(tornado.web.RequestHandler):
    def get(self):
        self.write(str(foodpot.amount))

class Info(tornado.web.RequestHandler):
    def post(self):
        username = self.get_argument("username")
        password = self.get_argument("password")

        Ordrin.api.initialize(api_key, "https://u-test.ordr.in/")
        Ordrin.api.setCurrAcct(username, password)
        addresses = Ordrin.u.getAddress()
        creditcards = Ordrin.u.getCard()
        info = {"addresses":addresses, "creditcards":creditcards}
        self.write(json.dumps(info))
        
application = tornado.web.Application([
                                       (r"/", MainPage),
                                       (r"/order/?", Order),
                                       (r"/listen/?", ListenRandomizer),
                                       (r"/listen/(\d+)/?", ListenPot),
                                       (r'/currentpot/?', CurrentPot),
                                       (r'/info/?', Info),
                                       ],
                                      static_path= os.path.join(os.path.dirname(__file__), "res", "static")
                                      )
if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()