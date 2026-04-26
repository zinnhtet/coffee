from flask import Flask, render_template , request, redirect
import sqlite3
from models import Products, Orders, Sales
from cs50 import SQL

from database import (get_all_products, add_new_product, add_order,
                      review_sales, get_daily_data, sale_calculation,
                      get_sales, get_best_worst_products, order_history,
                      get_all_time_stats, get_all_time_best_worst,
                      get_weekly_sales, categories)

app = Flask(__name__)

db = SQL("sqlite:///coffee.db")

options = [ "review", "dailysale"]

#######
########
#########



@app.route("/")
def index():
    products = get_all_products() # Fetch all products from DB
    return render_template("index.html", products=products)

@app.route("/result", methods=["POST"])
def result():

    products = get_all_products() # Fetch all products from DB
    order_date = request.form.get("order_date")  # get the date first cus all these data will have the same date
    selected_products = []  # bring an empty list to store the datas
    total_ordered = 0

    error = False

    for product in products:
        selected = request.form.get(f"{product.name}_confirm")
        quantity = request.form.get(f"{product.name}_qty")

        if selected == "selected":
            try:
                quantity = int(quantity)
            except (TypeError, ValueError):
                quantity = 0

            if quantity > 0:
                total = round(quantity * product.price, 2)
                product_id = product.id           # ← used for DB

                total_ordered += total          # for the total amount of the order

                # Insert into database
                add_order(order_date, product_id, quantity)

                selected_products.append((order_date, product.name, quantity, total)) # for python and template on web
            else:
                error = True


    # AFTER loop finishes
    if error:
        return render_template("error.html")

    return render_template("result.html", selected_products=selected_products, order_date=order_date, products= products, total_ordered=total_ordered)


@app.route("/date", methods=["GET", "POST"])
def date_selection():
    order_date = request.form.get("order_date")  # get the date first cus all these data will have the same date
    option = request.form.get("select_date")

    if request.method == "POST":
        if option == "review":
            return redirect(f"/review?date={order_date}")
        elif option == "dailysale":
            return redirect(f"/dailysale?date={order_date}")
    return render_template("date.html", order_date=order_date, options= options)


@app.route("/review", methods=["GET", "POST"])
def review():
    order_date = request.args.get("date") # works for both GET and POST
    orders = review_sales(order_date)
    return render_template("review.html", orders=orders, order_date=order_date)


@app.route("/edit", methods=["GET", "POST"])
def edit():
    products = get_all_products() # Fetch all products from DB
    categories = list(set([product.category for product in products])) #  create categories list HERE

    id = request.form.get("id")

    if id:
        db.execute("DELETE FROM products WHERE ID = ?", id)
        return render_template("success.html")
    return render_template("edit.html", products=products, categories=categories)
    # delete function is done but edit function like editing prices is in need

@app.route("/newproduct", methods=["GET", "POST"])
def newproduct():
        products = get_all_products() # Fetch all products from DB
        newproductsindex = []

        if request.method == "POST":

            name = request.form.get("name")
            category = request.form.get("category")
            price = request.form.get("price")

            try:
                price = float(price)
            except (TypeError, ValueError):
                return render_template("error.html", message="Invalid price")

            sell_price = request.form.get("sell_price")
            try:
                sell_price = float(sell_price)
            except (TypeError, ValueError):
                return render_template("error.html", message="Invalid sell price")

            if not name or not category or not price or not sell_price:
                return render_template("error.html")

            # call your function to insert into DB
            add_new_product(name, category, price, sell_price)
            newproductsindex.append((name, category, price, sell_price))
            return render_template("success.html", category=category, newproductsindex=newproductsindex)

        # GET request → show the form
        return render_template("newproduct.html",categories=categories, products=products)

@app.route("/dailysale",methods=["GET", "POST"])
def dailysale():
    # in this case u have to unpack cus u return at the end of this function in order to use those datas
    products, orders, order_date = get_daily_data()

    calculation = []
    if request.method == "POST":
        for order in orders:

            product_id = request.form.get(f"product_id_{order.id}")
            leftover = request.form.get(f"leftover_{order.id}")

            try:
                leftover = int(leftover)
            except (TypeError, ValueError):
                leftover = 0

            if leftover >=  0:
                sale_calculation(order.date, product_id, leftover)

                calculation.append((order.date, order.product_id, leftover))
        return redirect(f"/total?date={order_date}")
    return render_template("dailysale.html", orders=orders, order_date=order_date, products= products )


@app.route("/total", methods=["GET"])
def totalamount():
    order_date = request.args.get("date")
    sales = get_sales(order_date)
    orders = review_sales(order_date)
    products = get_all_products()
    results = get_best_worst_products(order_date)

    order_lookup = {order.product_name: order.quantity for order in orders}
    price_lookup = {product.name: product.price for product in products}

    total_ordered = 0
    total_leftover = 0

    for order in orders:
        price = price_lookup[order.product_name]
        total_ordered += price * order.quantity

    for sale in sales:
        price = price_lookup[sale.product_name]
        total_leftover += price * sale.quantity

    total_sales = total_ordered - total_leftover
    best = results[0] if results else None
    worst = results[-1] if results else None

    return render_template("total.html",
        sales=sales,
        order_lookup=order_lookup,
        order_date=order_date,
        total_ordered=total_ordered,      #
        total_leftover=total_leftover,    #
        total_sales=total_sales,          #
        best=best,                        #
        worst=worst)

@app.route("/stats", methods=["GET"])
def stats():
    order_date = request.args.get("date")
    results = get_best_worst_products(order_date)
    sales = get_sales(order_date)
    products = get_all_products()
    orders = review_sales(order_date)

    best = results[0] if results else None
    worst = results[-1] if results else None

    total_ordered = 0
    total_leftover = 0
    total_profit = 0

    # now lookup has BOTH prices
    buy_price_lookup  = {product.name: product.price for product in products}
    sell_price_lookup = {product.name: product.sell_price for product in products}
    order_lookup = {order.product_name: order.quantity for order in orders}

    for order in orders:
        buy_price = buy_price_lookup[order.product_name]
        total_ordered += buy_price * order.quantity

    for sale in sales:
        buy_price  = buy_price_lookup[sale.product_name]
        sell_price = sell_price_lookup[sale.product_name]
        sold = order_lookup[sale.product_name] - sale.quantity  # ordered - leftover = sold

        total_leftover += buy_price * sale.quantity
        total_profit   += (sold * sell_price) - (sold * buy_price)  # profit per product

    total_sales = total_ordered - total_leftover

    return render_template("stats.html",
        results=results, best=best, worst=worst,
        order_date=order_date, products=products,
        orders=orders, sales=sales,
        total_ordered=total_ordered,
        total_leftover=total_leftover,
        total_sales=total_sales,
        total_profit=total_profit)   #  new

@app.route("/dashboard", methods=["GET"])
def dashboard():
    total_ordered, total_leftover, total_sales = get_all_time_stats()
    results = get_all_time_best_worst()
    dates, amounts = get_weekly_sales()

    best = results[0] if results else None
    worst = results[-1] if results else None

    return render_template("dashboard.html",
        total_ordered=total_ordered,
        total_leftover=total_leftover,
        total_sales=total_sales,
        results=results,
        dates=dates,
        amounts=amounts,
        best=best,
        worst=worst)
