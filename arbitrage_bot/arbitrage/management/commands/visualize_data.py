# arbitrage/management/commands/visualize_data.py

import pandas as pd
import matplotlib.pyplot as plt
from django.core.management.base import BaseCommand
from arbitrage.models import Price, Opportunity

class Command(BaseCommand):
    help = 'Visualize price data and arbitrage opportunities'

    def handle(self, *args, **kwargs):
        # Fetch price data
        price_data = pd.DataFrame(list(Price.objects.all().values()))

        # Fetch arbitrage opportunities
        opportunity_data = pd.DataFrame(list(Opportunity.objects.all().values()))

        # Convert timestamp to datetime
        price_data['timestamp'] = pd.to_datetime(price_data['timestamp'])
        opportunity_data['timestamp'] = pd.to_datetime(opportunity_data['timestamp'])

        # Plot price data
        for token in price_data['token'].unique():
            plt.figure(figsize=(12, 6))
            for dex in price_data['dex'].unique():
                dex_data = price_data[(price_data['token'] == token) & (price_data['dex'] == dex)]
                plt.plot(dex_data['timestamp'], dex_data['price'], label=dex)
            plt.title(f'Prices for {token}')
            plt.xlabel('Time')
            plt.ylabel('Price')
            plt.legend()
            plt.show()

        # Plot arbitrage opportunities
        plt.figure(figsize=(12, 6))
        for token in opportunity_data['token'].unique():
            token_data = opportunity_data[opportunity_data['token'] == token]
            plt.scatter(token_data['timestamp'], token_data['profit'], label=token)
        plt.title('Arbitrage Opportunities')
        plt.xlabel('Time')
        plt.ylabel('Profit')
        plt.legend()
        plt.show()
