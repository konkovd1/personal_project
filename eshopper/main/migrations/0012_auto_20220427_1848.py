# Generated by Django 3.2.13 on 2022-04-27 15:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0011_productattribute_size'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ProductAttribute',
        ),
        migrations.DeleteModel(
            name='Size',
        ),
    ]
