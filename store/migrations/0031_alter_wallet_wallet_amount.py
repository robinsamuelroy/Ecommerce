# Generated by Django 4.2.7 on 2023-12-28 13:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0030_alter_wallet_wallet_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wallet',
            name='wallet_amount',
            field=models.FloatField(default=100),
        ),
    ]
