# Generated by Django 2.0.2 on 2018-07-31 05:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20180730_1910'),
    ]

    operations = [
        migrations.AlterField(
            model_name='banner',
            name='index',
            field=models.IntegerField(default=1, verbose_name='顺序'),
        ),
    ]