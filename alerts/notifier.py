# lets us send desktop popup notifications
from plyer import notification
# lets us connect to the database to read alerts
from db.database import dataBaseConnect

# sends a desktop popup with the coin name as the title and a message describing what happened
def notiFunction(coin, message):
    notification.notify(title=f"{coin}", message=f"{message}")

# runs every time fresh prices come in — checks if any saved alerts have been triggered
def notiCheckFunction(currPrice):
    # open the database and pick up the pen
    conn = dataBaseConnect()
    cursor = conn.cursor()

# each row is one alert saved in the database — a tuple of 5 values in this order:
# row[0] — the id (auto assigned by sqlite, we dont use it here)
# row[1] — the coin name (eg. "bitcoin")
# row[2] — the condition, either "above" or "below"
# row[3] — the threshold, the price limit the user set
# row[4] — triggered, 0 means not yet fired, 1 means already fired
    # fetch every alert row from the database as a list
    alerts = cursor.execute("SELECT * FROM alert").fetchall()
    # go through each alert one at a time
    for row in alerts:
        # currPrice is a dict like {"bitcoin": {"usd": ..., "usd_24h_change": ...}}
        # so pull out just this alert's coin price before comparing
        coinData = currPrice.get(row[1])
        if coinData is None:
            continue
        coinPrice = coinData.get("usd")

        # if the alert is set to fire when price goes above the limit and it has
        if row[2] == "above" and coinPrice > row[3]:
            notiFunction(row[1], f"High limit")
        # if the alert is set to fire when price drops below the limit and it has
        if row[2] == "below" and coinPrice < row[3]:
            notiFunction(row[1], f"Low limit")

    # close the database once all alerts have been checked
    conn.close()