# Generated by Django 3.1.5 on 2021-03-27 11:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contracts', '0003_auto_20210325_1149'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documentsender',
            name='expected_arrival_date',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='productsender',
            name='expected_arrival_date',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='tradersalescontract',
            name='created_at',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='tradersalescontract',
            name='payment_due_date',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='tradersalescontract',
            name='shipping_date',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='tradersalescontract',
            name='update_at',
            field=models.DateField(),
        ),
    ]