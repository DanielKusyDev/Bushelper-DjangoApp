# Generated by Django 2.2 on 2019-04-23 16:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bushelper', '0003_auto_20190420_2230'),
    ]

    operations = [
        migrations.AlterField(
            model_name='busstop',
            name='neighbours',
            field=models.ManyToManyField(to='bushelper.BusStop'),
        ),
    ]