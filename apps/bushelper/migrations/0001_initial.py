# Generated by Django 2.2 on 2019-04-20 20:18

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
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('departure', models.TimeField()),
                ('course_type', models.CharField(max_length=7)),
                ('bus_stop', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='course_bus_stop', to='bushelper.BusStop')),
                ('carrier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='course_carrier', to='bushelper.Carrier')),
                ('direction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='course_direction', to='bushelper.Direction')),
                ('line', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='course_line', to='bushelper.Line')),
            ],
        ),
        migrations.CreateModel(
            name='CarrierStopOrder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField()),
                ('bus_stop', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bushelper.BusStop')),
                ('carrier_stop', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bushelper.CarrierStop')),
            ],
        ),
        migrations.AddField(
            model_name='carrierstop',
            name='bus_stop',
            field=models.ManyToManyField(through='bushelper.CarrierStopOrder', to='bushelper.BusStop'),
        ),
        migrations.AddField(
            model_name='carrierstop',
            name='carrier',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bushelper.Carrier'),
        ),
        migrations.AddField(
            model_name='carrierstop',
            name='direction',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bushelper.Direction'),
        ),
        migrations.AddField(
            model_name='carrierstop',
            name='line',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='bushelper.Line'),
        ),
        migrations.AddField(
            model_name='busstop',
            name='direction',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bushelper.Direction'),
        ),
        migrations.AddField(
            model_name='busstop',
            name='neighbours',
            field=models.ManyToManyField(related_name='_busstop_neighbours_+', to='bushelper.BusStop'),
        ),
    ]
