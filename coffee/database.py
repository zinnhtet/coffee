# database.py
import sqlite3
from flask import request
from models import Products, Orders, Sales


categories = ["Bread", "Pastry", "Sandwich", "Drinks", "Cakes", "Other"]

# function to connect the database
def get_connection():
    conn = sqlite3.connect("coffee.db") #opens the database file
    conn.row_factory = sqlite3.Row #optinal but useful: now u can access column by name
    return conn # give the connection back so that ur program can use it

def get_all_products():
    conn = get_connection() #call the function and connect to sqlite
    cursor =conn.cursor() #create a cursor object to read and write from the database

    #get products
    cursor.execute ("SELECT * FROM products" )
    rows = cursor.fetchall () #fetch all results from that query and store them in rows like name=crossiant important

    #create an empty list called products then loop starts the put the data as a row with .append
    products = []
    for row in rows:
        product = Products(row["id"], row["name"], row["category"], row["price"], row["sell_price"])
        products.append(product)
    # this id, name, category, price are the column names in the database and they are used to create a product object with the Products class defined in models.py

    conn.close()
    #close the database connection

    return products

#this function is only to add product
def add_new_product(name, category, price, sell_price):
    conn = get_connection() #connect to SQLite
    cursor =conn.cursor() #create a cursor object to read and write from the database

    cursor.execute(
        "INSERT INTO products (name, category, price, sell_price) VALUES (?, ?, ?, ?)",
        (name, category, price, sell_price)
    )

    conn.commit() # VERY IMPORTANT date are saved cus of this line
    conn.close()

    return name,category, price, sell_price

#this function is only to insert data
def add_order(date, product_id, quantity):
    conn = get_connection() #connect to SQLite
    cursor =conn.cursor() #create a cursor object to read and write from the database

    cursor.execute(
        "INSERT INTO orders (date, product_id, quantity) VALUES (?, ?, ?)",
        (date, product_id,quantity)
    )

    conn.commit() # VERY IMPORTANT date are saved cus of this line
    conn.close()

#this function below isnt used anywhere BUT LATER u dont need to write no more
def order_history():
    conn = get_connection() #call the function and connect to sqlite
    cursor =conn.cursor() #create a cursor object to read and write from the database

    # the most important part product.id is replaced by product.name cus two table became together
    cursor.execute("""
    SELECT orders.id, orders.date, orders.quantity, products.name AS product_name
    FROM orders
    JOIN products ON orders.product_id = products.id
    """)
    rows = cursor.fetchall () #fetch all results from that query and store them in rows like name=crossiant important

    orders = []
    for row in rows:
        order = Orders(row["id"], row["date"], row["name"], row["quantity"], row["product_id"])
        orders.append(order)

    conn.close()
    #close the database connection
    return orders

def review_sales(order_date):
    conn = get_connection() #call the function and connect to sqlite
    cursor =conn.cursor() #create a cursor object to read and write from the database

    # the most important part product.id is replaced by product.name cus two table became together
    cursor.execute("""
        SELECT orders.id, orders.date, orders.quantity, orders.product_id, products.name AS product_name
        FROM orders
        JOIN products ON orders.product_id = products.id
        WHERE orders.date = ?
        """, (order_date,))

    rows = cursor.fetchall () #fetch all results from that query and store them in rows like name=crossiant important

    orders = []
    for row in rows:
        order = Orders(row["id"], row["date"], row["product_name"], row["quantity"], row["product_id"])
        orders.append(order)

    conn.close()
    #close the database connection
    return orders

def get_daily_data():
    """Helper function to fetch products and orders for a given date."""
    products = get_all_products()
    order_date = request.args.get("date")
    orders = review_sales(order_date)
    return products, orders, order_date


def sale_calculation(date, product_id, quantity):
    conn = get_connection() #connect to SQLite
    cursor =conn.cursor() #create a cursor object to read and write from the database

    cursor.execute(
        "INSERT INTO sales (date, product_id, quantity) VALUES (?, ?, ?)",
        (date, product_id,quantity)
    )

    conn.commit() # VERY IMPORTANT date are saved cus of this line
    conn.close()

def get_sales(order_date):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT sales.id, sales.date, sales.quantity, products.name AS product_name
        FROM sales
        JOIN products ON sales.product_id = products.id
        WHERE sales.date = ?
    """, (order_date,))

    rows = cursor.fetchall()

    sales = []
    for row in rows:
        sale = Sales(row["id"], row["date"], row["product_name"], row["quantity"])
        sales.append(sale)

    conn.close()
    return sales

def get_best_worst_products(order_date):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            products.name AS product_name,
            orders.quantity AS ordered,
            sales.quantity AS leftover,
            (orders.quantity - sales.quantity) AS sold
        FROM orders
        JOIN products ON orders.product_id = products.id
        JOIN sales ON sales.product_id = orders.product_id
            AND sales.date = orders.date
        WHERE orders.date = ?
        ORDER BY sold DESC
    """, (order_date,))

    rows = cursor.fetchall()
    results = []
    for row in rows:
        results.append({
            "product_name": row["product_name"],
            "ordered": row["ordered"],
            "leftover": row["leftover"],
            "sold": row["sold"]
        })

    conn.close()
    return results

def get_all_time_stats():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT SUM(orders.quantity * products.price) AS total_ordered FROM orders
                   JOIN products ON orders.product_id = products.id
    """)
    total_ordered = cursor.fetchone()[0] or 0

    cursor.execute("""
        SELECT SUM(sales.quantity * products.price) AS total_leftover
        FROM sales
        JOIN products ON sales.product_id = products.id
    """)
    total_leftover = cursor.fetchone()["total_leftover"] or 0

    conn.close()
    total_sales = total_ordered - total_leftover
    return round(total_ordered, 2), round(total_leftover, 2), round(total_sales, 2)

def get_all_time_best_worst():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            products.name AS product_name,
            SUM(orders.quantity) AS ordered,
            SUM(sales.quantity) AS leftover,
            SUM(orders.quantity - sales.quantity) AS sold
        FROM orders
        JOIN products ON orders.product_id = products.id
        JOIN sales ON sales.product_id = orders.product_id
            AND sales.date = orders.date
        GROUP BY products.name
        ORDER BY sold DESC
    """)

    rows = cursor.fetchall()
    results = []
    for row in rows:
        results.append({
            "product_name": row["product_name"],
            "ordered": row["ordered"],
            "leftover": row["leftover"],
            "sold": row["sold"]
        })

    conn.close()
    return results

def get_weekly_sales():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            orders.date,
            SUM((orders.quantity - sales.quantity) * products.price) AS daily_sales
        FROM orders
        JOIN products ON orders.product_id = products.id
        JOIN sales ON sales.product_id = orders.product_id
            AND sales.date = orders.date
        GROUP BY orders.date
        ORDER BY orders.date ASC
    """)

    rows = cursor.fetchall()
    dates = []
    amounts = []
    for row in rows:
        dates.append(row["date"])
        amounts.append(round(row["daily_sales"], 2))

    conn.close()
    return dates, amounts

