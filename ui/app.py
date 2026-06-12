import customtkinter as ctk
from api.coingecko import coinGekoAPI
from db.database import dataBaseConnect, save_price, saved_coins, SQLData, get_coins, remove_coin, set_alert, get_alerts
from alerts.notifier import notiCheckFunction

SQLData()


class CryptoTracker(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Crypto Tracker")
        self.geometry("1100x750")
        self.minsize(800, 600)
        self.configure(fg_color="#0f1116")

        self.coinList = get_coins()
        self.setup_ui()
        self.update_loop()


    def setup_ui(self):
        self.main_frame = ctk.CTkFrame(self, fg_color="#0f1116")
        self.main_frame.pack(fill="both", expand=True)

        self.price_labels = {}
        self.remove_coin_row = {}
        self.alert_labels = {}

        header = ctk.CTkLabel(self.main_frame, text="Crypto Tracker", font=ctk.CTkFont(size=22, weight="bold"), text_color="#f5f5f5")
        header.pack(pady=(15, 10))

        self.start_up_frame = ctk.CTkFrame(self.main_frame, fg_color="#0f1116")
        self.start_up_frame.pack(fill="both", expand=True, padx=15)

        self.input_frame = ctk.CTkFrame(self.main_frame, fg_color="#1c1f26")
        self.input_frame.pack(fill="x", side="bottom", padx=15, pady=15)

        self.input_box = ctk.CTkEntry(self.input_frame, placeholder_text="Input Coin")
        self.input_box.pack(side="left", padx=10, pady=10)

        self.input_submit = ctk.CTkButton(self.input_frame, text="Add", command=self.add_coins)
        self.input_submit.pack(side="left", padx=(0, 10), pady=10)



        #For the currently saved coins
        for coin in self.coinList:
            self.create_coin_row(coin)


    # builds one coin's row: remove button, price label, alert status, high/low entries, apply button
    def create_coin_row(self, coin):
        row_frame = ctk.CTkFrame(self.start_up_frame, fg_color="#1c1f26", corner_radius=8)
        row_frame.pack(fill="x", pady=4)

        remove_btn = ctk.CTkButton(row_frame, text="Remove", width=70, fg_color="#8b2c2c", hover_color="#a83a3a", command=lambda c=coin: self.remove_coin(c))
        remove_btn.pack(side="left", padx=8, pady=8)

        show_coin = ctk.CTkLabel(row_frame, text=coin, font=ctk.CTkFont(size=14, weight="bold"), anchor="center", text_color="#f5f5f5")
        show_coin.pack(side="left", fill="x", expand=True, padx=10)

        alerts = get_alerts(coin)
        alert_label = ctk.CTkLabel(row_frame, text=self.format_alert_text(alerts), text_color="#9aa0a6")
        alert_label.pack(side="left", padx=10)

        high_entry = ctk.CTkEntry(row_frame, placeholder_text="High", width=70)
        high_entry.pack(side="left", padx=2)

        low_entry = ctk.CTkEntry(row_frame, placeholder_text="Low", width=70)
        low_entry.pack(side="left", padx=2)

        apply_btn = ctk.CTkButton(row_frame, text="Apply", width=60, fg_color="#2c6b4f", hover_color="#37835f", command=lambda c=coin, h=high_entry, l=low_entry: self.apply_alerts(c, h, l))
        apply_btn.pack(side="left", padx=8, pady=8)

        self.remove_coin_row[coin] = row_frame
        self.price_labels[coin] = show_coin
        self.alert_labels[coin] = alert_label


    # turns an alerts dict ({"above": .., "below": ..}) into display text like "High: 70,000  Low: 60,000"
    def format_alert_text(self, alerts):
        high = alerts["above"]
        low = alerts["below"]

        high_text = f"{high:,.0f}" if high is not None else "-"
        low_text = f"{low:,.0f}" if low is not None else "-"

        return f"High: {high_text}  Low: {low_text}"


    #For the new coins that the user adds
    def add_coins(self):
        new_coin = self.input_box.get().lower()
        self.coinList.append(new_coin)
        saved_coins(new_coin)

        self.create_coin_row(new_coin)

        self.input_box.delete(0, "end")

    def apply_alerts(self, coin, high_entry, low_entry):
        high_value = high_entry.get()
        low_value = low_entry.get()

        if high_value:
            set_alert(coin, "above", float(high_value))

        if low_value:
            set_alert(coin, "below", float(low_value))

        alerts = get_alerts(coin)
        self.alert_labels[coin].configure(text=self.format_alert_text(alerts))

    def remove_coin(self, coin):
        self.coinList.remove(coin)          # removes from the in-memory list
        self.remove_coin_row[coin].destroy() # removes the row (button+label) from the screen
        del self.remove_coin_row[coin]       # cleans up the dict entry
        del self.price_labels[coin]          # cleans up the other dict entry
        del self.alert_labels[coin]          # cleans up the alert status label entry
        remove_coin(coin)                    # deletes it from the database


    def update_prices(self):
        gettingCoins = coinGekoAPI(self.coinList)

        for coin in gettingCoins:
            getUSD_And_Change = gettingCoins[coin]
            change = getUSD_And_Change['usd_24h_change']

            # green + up arrow when the price is up over the last 24hrs, red + down arrow when its down
            arrow = "▲" if change >= 0 else "▼"
            change_color = "#3ddc84" if change >= 0 else "#ff5c5c"

            self.price_labels[coin].configure(
                text=f"{coin.upper()}   ${getUSD_And_Change['usd']:,.0f}   {arrow} {abs(change):.2f}%",
                text_color=change_color
            )
            save_price(coin, getUSD_And_Change['usd'], getUSD_And_Change['usd_24h_change'])

        notiCheckFunction(gettingCoins)

    def update_loop(self):
        self.update_prices()
        self.after(180000, self.update_loop)


app = CryptoTracker()
app.mainloop()