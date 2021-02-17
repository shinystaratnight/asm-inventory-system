# Generated by Django 3.1.5 on 2021-02-17 02:57

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contract_date', models.DateTimeField(null=True)),
                ('supplier', models.CharField(max_length=200, null=True)),
                ('delivery_destination', models.CharField(max_length=200, null=True)),
                ('payment_deadline', models.DateTimeField(null=True)),
                ('inventory_clearing', models.CharField(max_length=200, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
            ],
        ),
    ]
