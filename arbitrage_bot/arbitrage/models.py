# arbitrage/models.py

from django.db import models

class Price(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    token = models.CharField(max_length=10)
    dex = models.CharField(max_length=50)
    price = models.FloatField()

    def __str__(self):
        return f"{self.token} - {self.dex} - {self.price}"

class Opportunity(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    token = models.CharField(max_length=10)
    buy_dex = models.CharField(max_length=50)
    buy_price = models.FloatField()
    sell_dex = models.CharField(max_length=50)
    sell_price = models.FloatField()
    profit = models.FloatField()

    def __str__(self):
        return f"{self.token} - {self.buy_dex} -> {self.sell_dex} - {self.profit}"
