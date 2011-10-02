import os.path
import Ordrin
import time
import json
import urllib2
import tornado.ioloop
import tornado.web
import tornado.template

loader = tornado.template.Loader(os.path.join(os.path.dirname(__file__), "res", "templates"))

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

#Initialize Ordrin
api_key = "GO-G43js4BGzQP2Ku8bTaA"
u_url = "https://u-test.ordr.in/u/"


class MainPage(tornado.web.RequestHandler):
    def get(self):
        self.write(loader.load("index.html").generate(test="Test"))


listener_callbacks = []

class Order(tornado.web.RequestHandler):
    #Placeholder for testing purposes
    def get(self):
        self.post()
    
    def post(self):
        #address = json.loads(address)
        #place = Ordrin.Address()
        order_amount = 1000
        if foodpot.amount > order_amount:
            foodpot.subtract_amount(order_amount)
            self.write("You won a free meal")
            #Make the order with the company's CC
        else:
            foodpot.add_amount(int(order_amount*.01))
            self.write("You did not win a free meal")
            #Make the order with the user's CC
        while listener_callbacks:
            callback = listener_callbacks.pop()
            callback.notify(foodpot.amount)

        
class ListenPot(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self, unique_string=None):
        if not unique_string:
            self.redirect("/listen/" + str(int(time.time())) +"/")
        listener_callbacks.append(self)
    
    def notify(self, amount):
        if self.request.connection.stream.closed() or self._finished:
            return
        self.write(str(amount))
        self.finish()


application = tornado.web.Application([
                                       (r"/", MainPage),
                                       (r"/order/?", Order),
                                       (r"/listen/?", ListenPot),
                                       (r"/listen/(\d+)/?", ListenPot),
                                       ],
                                      static_path= os.path.join(os.path.dirname(__file__), "res", "static")
                                      )
if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()