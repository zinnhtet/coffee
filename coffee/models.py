# models.py

class Products :
    def __init__(self, id, name, category, price, sell_price):
        self.id = id
        self.name = name
        self.category = category
        self.price = price
        self.sell_price = sell_price

#This is the attribute name inside the class.
#	It doesn’t have to match the database column.
#	It’s what your Python code and templates will use.
# at this point nothing is created yet — just a blueprint sitting there

class Orders :
    def __init__(self, id, date, product_name, quantity, product_id=None):
        self.id = id
        self.date = date
        self.product_name = product_name
        self.quantity = quantity
        self.product_id = product_id

class Sales:
    def __init__(self, id, date, product_name, quantity):
        self.id = id
        self.date = date
        self.product_name = product_name
        self.quantity = quantity

