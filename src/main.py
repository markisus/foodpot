import os.path
import Ordrin
import time
import random
import json
import urllib2
import tornado.ioloop
import tornado.web
import tornado.template
import threading

loader = tornado.template.Loader(os.path.join(os.path.dirname(__file__), "res", "templates"))

#Constants
restid = "207"
tray="375710/1"
tip="0"
dDate="10-03"
dTime="13:00"
api_key = "GO-G43js4BGzQP2Ku8bTaA"
order_amount = 1099

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

def make_loser_query(callback_method, username, password, address_nick, card_nick):
    def loser_query():
        Ordrin.api.initialize(api_key, "https://o-test.ordr.in/")
        Ordrin.api.setCurrAcct(username, password)            
        result = Ordrin.o.submit_less(restid, tray, str(random.randint(0,9999999)), dDate, dTime, card_nick, address_nick)
        loop = tornado.ioloop.IOLoop.instance()
        def callback():
            callback_method(result)
        loop.add_callback(callback)
    return loser_query

def make_winner_query(callback_method, username, password, address_nick):
    def winner_query():
        Ordrin.api.initialize(api_key, "https://u-test.ordr.in/")
        Ordrin.api.setCurrAcct(username, password)
        addr_json = Ordrin.u.getAddress(address_nick)
        Ordrin.api.initialize(api_key, "https://o-test.ordr.in/")            
        #Log in as Mark and pay for the user's meal
        Ordrin.api.setCurrAcct("marksisus@gmail.com", "password")
        result = Ordrin.o.submit_complete(restid, tray, str(random.randint(0,9999999)), dDate, dTime, "cc", 
                                          addr=addr_json['addr'], 
                                          city=addr_json['city'], 
                                          state=addr_json['state'], 
                                          zip=addr_json['zip'], 
                                          phone=addr_json['phone'])
        loop = tornado.ioloop.IOLoop.instance()
        def callback():
            callback_method(result)
        loop.add_callback(callback)
    return winner_query()

class Order(tornado.web.RequestHandler):
    #Placeholder for testing purposes
    def get(self):
        self.post()
        
    @tornado.web.asynchronous   
    def post(self):
        username = self.get_argument("username")
        password = self.get_argument("password")
        address_nick = self.get_argument("address_nick")
        card_nick = self.get_argument("card_nick")
        
        if foodpot.amount > order_amount:
            foodpot.subtract_amount(order_amount)
            self.notify_foodpot_listeners()
            #Make the order with the company's CC
            threaded_call = make_winner_query(self.notify_winner, username, password, address_nick)
            thread = threading.Thread(target=threaded_call)
            thread.start()
            
        else:                
            #Make the order with the user's CC
            threaded_call = make_loser_query(self.notify_loser, username, password, address_nick, card_nick)
            thread = threading.Thread(target=threaded_call)
            thread.start()

    def notify_foodpot_listeners(self):
        while listener_callbacks:
            callback = listener_callbacks.pop()
            print("Notifying listener " + str(callback.id))
            callback.notify(foodpot.amount)
        
    def notify_winner(self, data):
        print("Notifying winner " + str(data))
        if self.request.connection.stream.closed() or self._finished:
            return
        if data['_error'] == 1:
            self.write("11")
            self.finish()
        else:
            print("Writing 10")
            self.write("10")
            self.finish()
        
    def notify_loser(self, data):
        print("Notifying loser " + str(data))
        if self.request.connection.stream.closed() or self._finished:
            return
        if data['_error'] == 1:
            self.write("01")
            self.finish()
        else:
            foodpot.add_amount(int(order_amount*.01))
            self.notify_foodpot_listeners()
            print("Writing 00")
            self.write("00")
            self.finish()
        
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

def generate_info_query(callback_method, username, password):
    def get_addresses_and_ccards():
        Ordrin.api.initialize(api_key, "https://u-test.ordr.in/")
        Ordrin.api.setCurrAcct(username, password)
        addresses = Ordrin.u.getAddress()
        creditcards = Ordrin.u.getCard()
        info = json.dumps({"addresses":addresses, "creditcards":creditcards})
        loop = tornado.ioloop.IOLoop.instance()
        def callback():
            callback_method(info)
        loop.add_callback(callback)
    return get_addresses_and_ccards
    

class Info(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def post(self):
        username = self.get_argument("username")
        password = self.get_argument("password")
        threaded_call = generate_info_query(self.notify, username, password)
        thread = threading.Thread(target=threaded_call)
        thread.start()
    
    def notify(self, info):
        print("Inside Info.notify, info is " + info)
        if self.request.connection.stream.closed() or self._finished:
            return
        self.write(info)
        self.finish()
        
class FakeMessage(tornado.web.RequestHandler):
    def post(self):
        self.write("This is the guy who runs localtunnel. YOU ARE BANNED! GO AWAY")
        
application = tornado.web.Application([
                                       (r"/", MainPage),
                                       (r"/order/?", Order),
                                       (r"/listen/?", ListenRandomizer),
                                       (r"/listen/(\d+)/?", ListenPot),
                                       (r'/currentpot/?', CurrentPot),
                                       (r'/info/?', Info),
                                       (r'/callbacks/geo/london/', FakeMessage)
                                       ],
                                      static_path= os.path.join(os.path.dirname(__file__), "res", "static")
                                      )
if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()