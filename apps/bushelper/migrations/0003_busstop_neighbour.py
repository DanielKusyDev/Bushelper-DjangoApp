# Generated by Django 2.1.4 on 2019-03-30 20:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bushelper', '0002_remove_carrier_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='busstop',
            name='neighbour',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='bushelper.BusStop'),
        ),
    ]
