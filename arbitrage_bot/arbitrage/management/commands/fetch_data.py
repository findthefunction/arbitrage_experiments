# arbitrage/management/commands/fetch_data.py

import time
import requests
import pandas as pd
from django.core.management.base import BaseCommand
from arbitrage.models import Price, Opportunity

TOKENS = {
    "SOL": "So11111111111111111111111111111111111111112",
    "USDC": "5i7qTpkW9CDxTnJ3rmPZCMH5zU9X6Z6mbcfYYGd5Pq6m",
}

DEX_APIS = {
    "Serum": "https://serum-api.bonfida.com/orderbooks/{symbol}",
    "Raydium": "https://api.raydium.io/v2/market/{symbol}/orderbook",
    "Orca": "https://api.orca.so/allPools",
    "Saber": "https://api.saber.so/token-accounts/{symbol}",
    "Mango Markets": "https://mango-transaction-log.herokuapp.com/stats/perp_markets",
}

def get_token_price_from_serum(symbol):
    try:
        url = DEX_APIS["Serum"].format(symbol=symbol)
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return (data['data']['bids'][0]['price'] + data['data']['asks'][0]['price']) / 2
    except (requests.RequestException, KeyError) as e:
        print(f"Error fetching price from Serum for {symbol}: {e}")
        return None

def get_token_price_from_raydium(symbol):
    try:
        url = DEX_APIS["Raydium"].format(symbol=symbol)
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return (data['bids'][0]['price'] + data['asks'][0]['price']) / 2
    except (requests.RequestException, KeyError) as e:
        print(f"Error fetching price from Raydium for {symbol}: {e}")
        return None

def get_token_price_from_orca():
    try:
        url = DEX_APIS["Orca"]
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data['pools'][0]['price']
    except (requests.RequestException, KeyError) as e:
        print(f"Error fetching price from Orca: {e}")
        return None

def get_token_price_from_saber(symbol):
    try:
        url = DEX_APIS["Saber"].format(symbol=symbol)
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return (data['bids'][0]['price'] + data['asks'][0]['price']) / 2
    except (requests.RequestException, KeyError) as e:
        print(f"Error fetching price from Saber for {symbol}: {e}")
        return None

def get_token_price_from_mango_markets():
    try:
        url = DEX_APIS["Mango Markets"]
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data[0]['price']
    except (requests.RequestException, KeyError) as e:
        print(f"Error fetching price from Mango Markets: {e}")
        return None

def fetch_prices():
    prices = []
    for token_symbol in TOKENS.keys():
        serum_price = get_token_price_from_serum(token_symbol)
        raydium_price = get_token_price_from_raydium(token_symbol)
        orca_price = get_token_price_from_orca()
        saber_price = get_token_price_from_saber(token_symbol)
        mango_price = get_token_price_from_mango_markets()

        price_data = {
            "token": token_symbol,
            "Serum": serum_price,
            "Raydium": raydium_price,
            "Orca": orca_price,
            "Saber": saber_price,
            "Mango Markets": mango_price,
            "timestamp": pd.Timestamp.now()
        }
        prices.append(price_data)

        # Store prices in the database
        for dex, price in price_data.items():
            if dex not in ["token", "timestamp"] and price is not None:
                Price.objects.create(token=token_symbol, dex=dex, price=price)

    return pd.DataFrame(prices)

def detect_arbitrage_opportunities(prices_df):
    opportunities = []
    for token, group in prices_df.groupby("token"):
        dex_prices = group.drop(columns=["token", "timestamp"]).iloc[0].dropna()
        sorted_prices = dex_prices.sort_values()
        if len(sorted_prices) > 1:
            buy_dex, buy_price = sorted_prices.index[0], sorted_prices.iloc[0]
            sell_dex, sell_price = sorted_prices.index[-1], sorted_prices.iloc[-1]
            if buy_price < sell_price:
                opportunity = {
                    "token": token,
                    "buy_dex": buy_dex,
                    "buy_price": buy_price,
                    "sell_dex": sell_dex,
                    "sell_price": sell_price,
                    "profit": sell_price - buy_price,
                    "timestamp": pd.Timestamp.now()
                }
                opportunities.append(opportunity)

                # Store opportunities in the database
                Opportunity.objects.create(
                    token=token,
                    buy_dex=buy_dex,
                    buy_price=buy_price,
                    sell_dex=sell_dex,
                    sell_price=sell_price,
                    profit=sell_price - buy_price
                )

    return pd.DataFrame(opportunities)

class Command(BaseCommand):
    help = 'Fetch prices and detect arbitrage opportunities'

    def handle(self, *args, **kwargs):
        while True:
            prices_df = fetch_prices()
            opportunities_df = detect_arbitrage_opportunities(prices_df)
            for _, opportunity in opportunities_df.iterrows():
                self.stdout.write(self.style.SUCCESS(
                    f"Arbitrage Opportunity: Buy {opportunity['token']} on {opportunity['buy_dex']} for {opportunity['buy_price']} and sell on {opportunity['sell_dex']} for {opportunity['sell_price']} (Profit: {opportunity['profit']})"
                ))
            time.sleep(60)  # Wait a minute before checking again
