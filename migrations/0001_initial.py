# Generated by Django 2.1.4 on 2019-01-03 15:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BusStop',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mpk_street', models.CharField(default='', max_length=255)),
                ('fremiks_alias', models.CharField(blank=True, max_length=255, null=True)),
                ('latitude', models.FloatField()),
                ('longtitude', models.FloatField()),
            ],
            options={
                'ordering': ['mpk_street'],
            },
        ),
        migrations.CreateModel(
            name='Carrier',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('number', models.IntegerField(blank=True, null=True)),
                ('website', models.CharField(blank=True, max_length=127, null=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='CarrierStop',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='CarrierStopOrder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField()),
                ('bus_stop', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='carrierstoporder_busstop_fk', to='apps.bushelper.BusStop')),
                ('carrier_stop', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='carrierstoporder_carrierstop_fk', to='apps.bushelper.CarrierStop')),
            ],
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course_type', models.CharField(max_length=7)),
                ('bus_stop', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='course_stop_fk', to='apps.bushelper.BusStop')),
                ('carrier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='course_carrier_fk', to='apps.bushelper.Carrier')),
            ],
            options={
                'ordering': ['pk'],
            },
        ),
        migrations.CreateModel(
            name='Departure',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hour', models.TimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Direction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('direction', models.CharField(max_length=3)),
            ],
        ),
        migrations.CreateModel(
            name='Line',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=8)),
                ('url', models.URLField()),
            ],
        ),
        migrations.AddField(
            model_name='course',
            name='departure',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='course_departure_fk', to='apps.bushelper.Departure'),
        ),
        migrations.AddField(
            model_name='course',
            name='direction',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='course_direction_fk', to='apps.bushelper.Direction'),
        ),
        migrations.AddField(
            model_name='course',
            name='line',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='course_line_fk', to='apps.bushelper.Line'),
        ),
        migrations.AddField(
            model_name='carrierstop',
            name='bus_stop',
            field=models.ManyToManyField(related_name='carrierstop_busstop_fk', through='apps.bushelper.CarrierStopOrder', to='apps.bushelper.BusStop'),
        ),
        migrations.AddField(
            model_name='carrierstop',
            name='carrier',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='carrierstop_carrier_fk', to='apps.bushelper.Carrier'),
        ),
        migrations.AddField(
            model_name='carrierstop',
            name='direction',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='carrierstop_direction_fk', to='apps.bushelper.Direction'),
        ),
        migrations.AddField(
            model_name='carrierstop',
            name='line',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='carrierstop_line_fk', to='apps.bushelper.Line'),
        ),
        migrations.AddField(
            model_name='busstop',
            name='direction',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='busstop_direction_fk', to='apps.bushelper.Direction'),
        ),
    ]
