# Generated by Django 3.1.5 on 2021-03-19 03:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('masterdata', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customer',
            old_name='telephone',
            new_name='tel',
        ),
        migrations.RenameField(
            model_name='hall',
            old_name='telephone',
            new_name='tel',
        ),
        migrations.RenameField(
            model_name='shippingaddress',
            old_name='telephone',
            new_name='tel',
        ),
    ]
