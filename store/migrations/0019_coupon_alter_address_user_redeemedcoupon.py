# Generated by Django 4.2.7 on 2023-12-15 19:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('store', '0018_remove_wishlist_product_remove_wishlist_user_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=10, unique=True)),
                ('description', models.CharField(blank=True, max_length=50)),
                ('discount', models.PositiveIntegerField(help_text='Discount percentage')),
                ('expiration_date', models.DateField()),
                ('minimum_purchase_value', models.PositiveIntegerField(default=1000)),
                ('maximum_purchase_value', models.PositiveIntegerField(default=10000)),
                ('Usage_count', models.PositiveIntegerField(default=1)),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
        migrations.AlterField(
            model_name='address',
            name='user',
            field=models.ForeignKey(default='Robin', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='RedeemedCoupon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('redeemed_date', models.DateTimeField(auto_now_add=True)),
                ('is_redeemed', models.BooleanField(default=False)),
                ('coupon', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.coupon')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]