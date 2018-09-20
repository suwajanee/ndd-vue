# Generated by Django 2.1 on 2018-09-06 08:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0003_auto_20180827_1125'),
    ]

    operations = [
        migrations.AddField(
            model_name='principal',
            name='cancel',
            field=models.CharField(choices=[('1', 'Cancel'), ('0', '-')], default=0, max_length=1),
        ),
        migrations.AddField(
            model_name='shipper',
            name='cancel',
            field=models.CharField(choices=[('1', 'Cancel'), ('0', '-')], default=0, max_length=1),
        ),
    ]