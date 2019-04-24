# Generated by Django 2.2 on 2019-04-23 20:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bushelper', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Departure',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hour', models.TimeField()),
            ],
        ),
        migrations.AlterModelOptions(
            name='course',
            options={'ordering': ['pk']},
        ),
        migrations.RemoveField(
            model_name='busstop',
            name='neighbours',
        ),
        migrations.AddField(
            model_name='carrier',
            name='number',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='busstop',
            name='direction',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='busstop_direction_fk', to='bushelper.Direction'),
        ),
        migrations.AlterField(
            model_name='carrierstop',
            name='bus_stop',
            field=models.ManyToManyField(related_name='carrierstop_busstop_fk', through='bushelper.CarrierStopOrder', to='bushelper.BusStop'),
        ),
        migrations.AlterField(
            model_name='carrierstop',
            name='carrier',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='carrierstop_carrier_fk', to='bushelper.Carrier'),
        ),
        migrations.AlterField(
            model_name='carrierstop',
            name='direction',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='carrierstop_direction_fk', to='bushelper.Direction'),
        ),
        migrations.AlterField(
            model_name='carrierstop',
            name='line',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='carrierstop_line_fk', to='bushelper.Line'),
        ),
        migrations.AlterField(
            model_name='carrierstoporder',
            name='bus_stop',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='carrierstoporder_busstop_fk', to='bushelper.BusStop'),
        ),
        migrations.AlterField(
            model_name='carrierstoporder',
            name='carrier_stop',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='carrierstoporder_carrierstop_fk', to='bushelper.CarrierStop'),
        ),
        migrations.AlterField(
            model_name='course',
            name='bus_stop',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='course_stop_fk', to='bushelper.BusStop'),
        ),
        migrations.AlterField(
            model_name='course',
            name='carrier',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='course_carrier_fk', to='bushelper.Carrier'),
        ),
        migrations.AlterField(
            model_name='course',
            name='departure',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='course_departure_fk', to='bushelper.Departure'),
        ),
        migrations.AlterField(
            model_name='course',
            name='direction',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='course_direction_fk', to='bushelper.Direction'),
        ),
        migrations.AlterField(
            model_name='course',
            name='line',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='course_line_fk', to='bushelper.Line'),
        ),
    ]
