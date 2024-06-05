# Generated by Django 5.0.6 on 2024-06-05 17:57

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Opportunity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('token', models.CharField(max_length=10)),
                ('buy_dex', models.CharField(max_length=50)),
                ('buy_price', models.FloatField()),
                ('sell_dex', models.CharField(max_length=50)),
                ('sell_price', models.FloatField()),
                ('profit', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='Price',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('token', models.CharField(max_length=10)),
                ('dex', models.CharField(max_length=50)),
                ('price', models.FloatField()),
            ],
        ),
    ]
