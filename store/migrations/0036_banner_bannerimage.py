# Generated by Django 4.2.7 on 2024-01-03 15:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0035_order_address'),
    ]

    operations = [
        migrations.CreateModel(
            name='Banner',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('banner_name', models.CharField(blank=True, max_length=50)),
                ('is_active', models.BooleanField(default=True)),
                ('set', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='BannerImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('images', models.ImageField(blank=True, upload_to='banneer_images/')),
                ('banner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='store.banner')),
            ],
        ),
    ]
