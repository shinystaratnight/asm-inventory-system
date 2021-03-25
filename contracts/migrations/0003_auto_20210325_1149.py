# Generated by Django 3.1.5 on 2021-03-25 11:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('masterdata', '0006_auto_20210325_1149'),
        ('contracts', '0002_auto_20210217_1534'),
    ]

    operations = [
        migrations.CreateModel(
            name='Sender',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('address', models.CharField(max_length=255)),
                ('tel', models.CharField(blank=True, max_length=30, null=True)),
                ('fax', models.CharField(blank=True, max_length=30, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='TraderSalesContract',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contract_id', models.CharField(max_length=200)),
                ('person_in_charge', models.CharField(max_length=200)),
                ('remarks', models.TextField(blank=True, null=True)),
                ('shipping_method', models.CharField(choices=[('D', 'Delivery'), ('R', 'Receipt'), ('C', 'ID Change'), ('B', '* Blank')], max_length=1)),
                ('shipping_date', models.DateTimeField()),
                ('payment_method', models.CharField(choices=[('TR', 'Transfer'), ('CH', 'Check'), ('BL', 'Bill'), ('CA', 'Cash')], max_length=2)),
                ('payment_due_date', models.DateTimeField()),
                ('insurance_fee', models.PositiveIntegerField(blank=True, null=True)),
                ('update_at', models.DateTimeField()),
                ('created_at', models.DateTimeField()),
                ('customer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='trader_sales_contracts', to='masterdata.customer')),
            ],
        ),
        migrations.CreateModel(
            name='TraderSalesProduct',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('type', models.CharField(choices=[('M', 'Main body'), ('F', 'Frame'), ('C', 'Cell'), ('N', 'Nail sheet')], max_length=1)),
                ('quantity', models.PositiveIntegerField()),
                ('price', models.PositiveIntegerField()),
                ('contract', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='contracts.tradersalescontract')),
            ],
        ),
        migrations.DeleteModel(
            name='DocumentShippingAddress',
        ),
        migrations.RemoveField(
            model_name='sale',
            name='product_shipping_address',
        ),
        migrations.CreateModel(
            name='DocumentSender',
            fields=[
                ('sender_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='contracts.sender')),
                ('expected_arrival_date', models.DateTimeField()),
                ('contract', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='contracts.tradersalescontract')),
            ],
            bases=('contracts.sender',),
        ),
        migrations.CreateModel(
            name='ProductSender',
            fields=[
                ('sender_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='contracts.sender')),
                ('expected_arrival_date', models.DateTimeField()),
                ('contract', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='contracts.tradersalescontract')),
            ],
            bases=('contracts.sender',),
        ),
        migrations.DeleteModel(
            name='ProductShippingAddress',
        ),
        migrations.DeleteModel(
            name='Sale',
        ),
    ]
