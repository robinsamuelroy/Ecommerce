# Generated by Django 4.2.7 on 2023-12-15 13:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0016_order_payment_orderproduct_order_payment_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderproduct',
            name='size',
        ),
    ]
