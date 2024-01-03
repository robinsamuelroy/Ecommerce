# Generated by Django 4.2.7 on 2023-12-17 21:41

from django.db import migrations, models
import store.models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0020_alter_product_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(blank=True, default='product.jpg', null=True, upload_to=store.models.user_directory_path),
        ),
    ]
