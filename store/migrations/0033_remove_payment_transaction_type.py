# Generated by Django 4.2.7 on 2023-12-29 15:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0032_payment_transaction_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='payment',
            name='transaction_type',
        ),
    ]
