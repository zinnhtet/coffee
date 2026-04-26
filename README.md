# ☕ Coffee Shop Inventory & Sales Tracker

A Flask web app to manage daily coffee shop operations — track orders, 
sales, leftovers, and profits.

## Features
- 📦 Add and manage products by category
- 🛒 Take daily orders
- 📊 Track daily sales and leftovers
- 💰 Calculate daily profit (buy price vs sell price)
- 📈 Dashboard with weekly sales chart
- 🏆 Best and worst selling products

## Tech Stack
- Python / Flask
- SQLite
- HTML / CSS (Jinja2 templates)

## How to Run
1. Clone the repo
   git clone https://github.com/zinnhtet/coffee.git
   cd coffee

2. Install dependencies
   pip3 install flask cs50

3. Run the app
   flask run

4. Open http://127.0.0.1:5000

## Project Structure
- app.py         → main Flask routes
- database.py    → all database queries
- models.py      → data models
- templates/     → HTML pages
- static/        → CSS and assets
