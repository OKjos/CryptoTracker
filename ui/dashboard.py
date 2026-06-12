from rich.console import Console
from rich.table import Table


def display(test):
    console = Console()
    table = Table(title="Crypto Table")

    table.add_column("Name", style="cyan")
    table.add_column("Price", style="blue")
    table.add_column("24hr Change", style="white")

    for coin, data in test.items():
        coinPrice = data.get("usd")
        coinChange = data.get("usd_24h_change")
        if coinChange > 0:
            changeStr = f"[green]{coinChange:.2f}%[/green]"
        elif coinChange < 0:
            changeStr = f"[red]{coinChange:.2f}%[/red]"
        table.add_row(str(coin), f"${coinPrice:,}", changeStr)

    console.print(table)

