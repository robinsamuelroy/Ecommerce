# Generated by Django 4.2.7 on 2023-12-29 15:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0031_alter_wallet_wallet_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='transaction_type',
            field=models.CharField(default='Debit', max_length=10),
        ),
    ]