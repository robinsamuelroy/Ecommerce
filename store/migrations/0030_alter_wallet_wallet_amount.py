# Generated by Django 4.2.7 on 2023-12-28 11:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0029_coupon_redeemedcoupon'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wallet',
            name='wallet_amount',
            field=models.DecimalField(decimal_places=2, default=100.0, max_digits=10),
        ),
    ]
