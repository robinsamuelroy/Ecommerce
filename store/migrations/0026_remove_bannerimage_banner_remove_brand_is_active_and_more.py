# Generated by Django 4.2.7 on 2023-12-19 14:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0025_banner_bannerimage'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bannerimage',
            name='banner',
        ),
        migrations.RemoveField(
            model_name='brand',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='category',
            name='is_active',
        ),
        migrations.AddField(
            model_name='brand',
            name='is_blocked',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='category',
            name='is_blocked',
            field=models.BooleanField(default=False),
        ),
        migrations.DeleteModel(
            name='Banner',
        ),
        migrations.DeleteModel(
            name='BannerImage',
        ),
    ]