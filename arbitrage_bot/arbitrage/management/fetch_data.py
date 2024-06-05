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
    url = DEX_APIS["Serum"].format(symbol=symbol)
    response = requests.get(url)
    data = response.json()
    return (data['data']['bids'][0]['price'] + data['data']['asks'][0]['price']) / 2

def get_token_price_from_raydium(symbol):
    url = DEX_APIS["Raydium"].format(symbol=symbol)
    response = requests.get(url)
    data = response.json()
    return (data['bids'][0]['price'] + data['asks'][0]['price']) / 2

def get_token_price_from_orca():
    url = DEX_APIS["Orca"]
    response = requests.get(url)
    data = response.json()
    # Example parsing, you need to find the right pool and price based on the structure of the response
    return data['pools'][0]['price']

def get_token_price_from_saber(symbol):
    url = DEX_APIS["Saber"].format(symbol=symbol)
    response = requests.get(url)
    data = response.json()
    return (data['bids'][0]['price'] + data['asks'][0]['price']) / 2

def get_token_price_from_mango_markets():
    url = DEX_APIS["Mango Markets"]
    response = requests.get(url)
    data = response.json()
    # Example parsing, you need to find the right market and price based on the structure of the response
    return data[0]['price']

def fetch_prices():
    prices = {}
    for token_symbol in TOKENS.keys():
        try:
            serum_price = get_token_price_from_serum(token_symbol)
            raydium_price = get_token_price_from_raydium(token_symbol)
            orca_price = get_token_price_from_orca()
            saber_price = get_token_price_from_saber(token_symbol)
            mango_price = get_token_price_from_mango_markets()

            prices[token_symbol] = {
                "Serum": serum_price,
                "Raydium": raydium_price,
                "Orca": orca_price,
                "Saber": saber_price,
                "Mango Markets": mango_price,
            }

            # Store prices in the database
            for dex, price in prices[token_symbol].items():
                Price.objects.create(token=token_symbol, dex=dex, price=price)

        except Exception as e:
            print(f"Error fetching prices for {token_symbol}: {e}")
    return prices

def detect_arbitrage_opportunities(prices):
    opportunities = []
    for token, dex_prices in prices.items():
        sorted_prices = sorted(dex_prices.items(), key=lambda item: item[1])
        if len(sorted_prices) > 1:
            buy_dex, buy_price = sorted_prices[0]
            sell_dex, sell_price = sorted_prices[-1]
            if buy_price < sell_price:
                opportunity = {
                    "token": token,
                    "buy_dex": buy_dex,
                    "buy_price": buy_price,
                    "sell_dex": sell_dex,
                    "sell_price": sell_price,
                    "profit": sell_price - buy_price
                }
                opportunities.append(opportunity)

                # Store opportunities in the database
                Opportunity.objects.create(
                    token=token,
                    buy_dex=buy_dex,
                    buy_price=buy_price,
                    sell_dex=sell_dex,
                    sell_price=sell_price,
                    profit=opportunity['profit']
                )

    return opportunities

class Command(BaseCommand):
    help = 'Fetch prices and detect arbitrage opportunities'

    def handle(self, *args, **kwargs):
        while True:
            prices = fetch_prices()
            opportunities = detect_arbitrage_opportunities(prices)
            for opportunity in opportunities:
                self.stdout.write(self.style.SUCCESS(
                    f"Arbitrage Opportunity: Buy {opportunity['token']} on {opportunity['buy_dex']} for {opportunity['buy_price']} and sell on {opportunity['sell_dex']} for {opportunity['sell_price']} (Profit: {opportunity['profit']})"
                ))
            time.sleep(60)  # Wait a minute before checking again
