# Generated by Django 4.2.7 on 2023-12-08 06:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_cartoderitems_invoice_no'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='color',
            name='price',
        ),
        migrations.RemoveField(
            model_name='product',
            name='old_price',
        ),
        migrations.RemoveField(
            model_name='productvariant',
            name='old_price',
        ),
    ]
