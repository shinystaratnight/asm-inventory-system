# Generated by Django 3.1.5 on 2021-03-28 04:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('masterdata', '0006_auto_20210325_1149'),
        ('contracts', '0004_auto_20210327_1112'),
    ]

    operations = [
        migrations.CreateModel(
            name='PurchaseSender',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('P', 'Product'), ('D', 'Document')], max_length=1)),
                ('desired_arrival_date', models.DateField()),
                ('shipping_company', models.CharField(max_length=100)),
                ('remarks', models.TextField(blank=True, null=True)),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='masterdata.receiver')),
            ],
        ),
        migrations.CreateModel(
            name='SaleSender',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('P', 'Product'), ('D', 'Document')], max_length=1)),
                ('expected_arrival_date', models.DateField()),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='masterdata.receiver')),
            ],
        ),
        migrations.RemoveField(
            model_name='productsender',
            name='contract',
        ),
        migrations.RemoveField(
            model_name='productsender',
            name='sender_ptr',
        ),
        migrations.DeleteModel(
            name='DocumentSender',
        ),
        migrations.DeleteModel(
            name='ProductSender',
        ),
        migrations.DeleteModel(
            name='Sender',
        ),
    ]