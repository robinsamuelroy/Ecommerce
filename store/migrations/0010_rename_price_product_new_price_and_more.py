# Generated by Django 4.2.7 on 2023-12-12 07:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0009_remove_productvariant_old_price_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='price',
            new_name='new_price',
        ),
        migrations.RenameField(
            model_name='productvariant',
            old_name='price',
            new_name='new_price',
        ),
        migrations.AddField(
            model_name='product',
            name='old_price',
            field=models.DecimalField(decimal_places=2, default=2.99, max_digits=10),
        ),
        migrations.AddField(
            model_name='productvariant',
            name='old_price',
            field=models.DecimalField(decimal_places=2, default=2.99, max_digits=10),
        ),
    ]