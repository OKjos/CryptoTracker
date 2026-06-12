# lets us talk to a local sqlite database file
import sqlite3
# lets us get the current time when saving prices
import datetime

# the name of the database file that will be created in the project folder
dataBaseFile = 'crypto.db'

# opens a connection to the database file, creates it if it doesnt exist yet
def dataBaseConnect():
    doesDataBaseFileExist = sqlite3.connect(dataBaseFile)
    return doesDataBaseFileExist

# creates the three tables if they dont already exist — runs once on startup
def SQLData():
    # open the notebook
    conn = dataBaseConnect()
    # pick up the pen
    cursor = conn.cursor()

    # create the prices table — stores every price we fetch with a timestamp
    cursor.execute("CREATE TABLE IF NOT EXISTS prices (id INTEGER PRIMARY KEY AUTOINCREMENT, coin TEXT, price REAL, timestamp TEXT)")
    # create the alerts table — stores the rules the user sets for notifications
    cursor.execute("CREATE TABLE IF NOT EXISTS alert (id INTEGER PRIMARY KEY AUTOINCREMENT, coin TEXT, condition TEXT, threshold REAL, triggered INTEGER)")
    # create the portfolio table — stores how much of each coin the user holds
    cursor.execute("CREATE TABLE IF NOT EXISTS portfolio (id INTEGER PRIMARY KEY AUTOINCREMENT, coin TEXT, amount REAL)")

    cursor.execute("CREATE TABLE IF NOT EXISTS watch_List_Coins (id INTEGER PRIMARY KEY AUTOINCREMENT, coin TEXT)")

    # save all the changes to the file
    conn.commit()
    # close the notebook
    conn.close()

# called every time we get a fresh price from coingecko — writes one row to the prices table
def save_price(coinName, price, hrExchange):
    # open the notebook
    conn = dataBaseConnect()
    # pick up the pen
    cursor = conn.cursor()

    # insert a new row with the coin name, price, and current timestamp — ? marks are safe placeholders
    cursor.execute("INSERT INTO prices (coin, price, timestamp) VALUES (?, ?, ?)", (coinName, price, datetime.datetime.now().isoformat()))

    # save the new row
    conn.commit()
    # close the notebook
    conn.close()

def saved_coins(coinName):
    conn = dataBaseConnect()
    cursor = conn.cursor()


    cursor.execute("INSERT INTO watch_List_Coins (coin) VALUES (?)", (coinName, ))

    conn.commit()
    conn.close()

def get_coins():
    conn = dataBaseConnect()
    cursor = conn.cursor()

    coins = []
    rows = cursor.execute("SELECT * FROM watch_List_Coins").fetchall()
    
    for row in rows:
        coins.append(row[1])

    conn.commit()
    conn.close()
    
    return coins

def remove_coin(coinName):
    conn = dataBaseConnect()
    cursor = conn.cursor()


    cursor.execute("DELETE FROM watch_List_Coins WHERE coin = ?", (coinName, ))

    conn.commit()
    conn.close()

# returns the current high/low alert thresholds for a coin, as a dict
def get_alerts(coinName):
    conn = dataBaseConnect()
    cursor = conn.cursor()

    alerts = {"above": None, "below": None}

    rows = cursor.execute("SELECT condition, threshold FROM alert WHERE coin = ?", (coinName, )).fetchall()
    for row in rows:
        alerts[row[0]] = row[1]

    conn.close()
    return alerts

# saves (or updates) the high/low alert threshold for a coin
def set_alert(coinName, condition, threshold):
    conn = dataBaseConnect()
    cursor = conn.cursor()

    # check if an alert with this coin + condition already exists
    existing = cursor.execute("SELECT id FROM alert WHERE coin = ? AND condition = ?", (coinName, condition)).fetchone()

    if existing:
        # update the existing alert and reset triggered so it can fire again
        cursor.execute("UPDATE alert SET threshold = ?, triggered = 0 WHERE id = ?", (threshold, existing[0]))
    else:
        # no alert yet for this coin + condition, so create one
        cursor.execute("INSERT INTO alert (coin, condition, threshold, triggered) VALUES (?, ?, ?, 0)", (coinName, condition, threshold))

    conn.commit()
    conn.close()