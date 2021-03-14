# Generated by Django 3.1.5 on 2021-02-17 07:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentShippingAddress',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_name', models.CharField(max_length=200, null=True)),
                ('address', models.CharField(max_length=200, null=True)),
                ('tel', models.CharField(max_length=200, null=True)),
                ('fax', models.CharField(max_length=200, null=True)),
                ('expected_arrival_date', models.DateTimeField(null=True)),
                ('desired_arrival_date', models.DateTimeField(blank=True, null=True)),
                ('shipping_company', models.CharField(blank=True, max_length=200, null=True)),
                ('remark', models.CharField(blank=True, max_length=200, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProductShippingAddress',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_name', models.CharField(max_length=200, null=True)),
                ('address', models.CharField(max_length=200, null=True)),
                ('tel', models.CharField(max_length=200, null=True)),
                ('fax', models.CharField(max_length=200, null=True)),
                ('expected_arrival_date', models.DateTimeField(null=True)),
                ('desired_arrival_date', models.DateTimeField(blank=True, null=True)),
                ('shipping_company', models.CharField(blank=True, max_length=200, null=True)),
                ('remark', models.CharField(blank=True, max_length=200, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Sale',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_id', models.CharField(max_length=200, null=True)),
                ('contract_date', models.DateTimeField(null=True)),
                ('in_charge', models.CharField(max_length=200, null=True)),
                ('membership_number', models.CharField(max_length=200, null=True)),
                ('shipping_method', models.CharField(choices=[('Shipping', 'Shipping'), ('Picking up', 'Picking up'), ('ID change', 'ID change'), ('*blank', '*blank')], max_length=200, null=True)),
                ('shipping_method_date', models.DateTimeField(null=True)),
                ('remarks', models.CharField(max_length=200, null=True)),
                ('payment_method', models.CharField(choices=[('Transfer', 'Transfer'), ('Check', 'Check'), ('Bill', 'Bill'), ('Cash', 'Cash')], max_length=200, null=True)),
                ('payment_deadline', models.DateTimeField(null=True)),
                ('subtotal', models.FloatField(blank=True, null=True)),
                ('consumption_tax', models.FloatField(blank=True, null=True)),
                ('insurance_fee', models.FloatField(blank=True, null=True)),
                ('total_amount', models.FloatField(blank=True, null=True)),
                ('update_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('product_shipping_address', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='contracts.productshippingaddress')),
            ],
        ),
    ]