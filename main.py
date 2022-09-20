import sqlite3, config
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from datetime import date

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/")
def index(request: Request):
    stock_filter = request.query_params.get('filter', False)
    
    connection = sqlite3.connect(config.DB_FILE)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    if stock_filter == 'new_closing_hights':
        cursor.execute(""" SELECT * FROM (
            SELECT symbol, name, stock_id, max(close), date
            FROM stock_price JOIN stock ON stock.id = stock_price.stock_id
            where stock_price.close < 20
            GROUP BY stock_id
            ORDER BY symbol
        ) WHERE date = (select max(date) from stock_price)
        """)
    elif stock_filter == 'new_closing_low':
        cursor.execute(""" SELECT * FROM (
            SELECT symbol, name, stock_id, min(close), date
            FROM stock_price JOIN stock ON stock.id = stock_price.stock_id
            where stock_price.close < 20
            GROUP BY stock_id
            ORDER BY symbol
        ) WHERE date = (select max(date) from stock_price)
        """)
    else:
        cursor.execute('SELECT id, symbol, name FROM stock ORDER BY symbol')

    rows = cursor.fetchall()

    return templates.TemplateResponse("index.html", {"request": request, "stocks": rows})

@app.get("/stock/{symbol}")
def stock_detail(request: Request, symbol):
    connection = sqlite3.connect(config.DB_FILE)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM strategy
    """)
    strategies = cursor.fetchall()

    cursor.execute('SELECT id, symbol, name FROM stock WHERE symbol = ?', (symbol,))
    row = cursor.fetchone()

    cursor.execute('SELECT * FROM stock_price WHERE stock_id = ? ORDER BY date DESC', (row['id'],))
    prices = cursor.fetchall()

    return templates.TemplateResponse("stock_detail.html", {"request": request, "stock": row, "bars": prices, "strategies": strategies})
     
