# Generated by Django 3.2.13 on 2022-04-27 09:34

from django.db import migrations, models
import eshopper.main.models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_auto_20220427_1213'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='email',
            field=models.EmailField(max_length=254, unique=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='transaction_id',
            field=models.CharField(default=eshopper.main.models.default_random_transaction_id, max_length=100, null=True, unique=True),
        ),
    ]
