# Generated by Django 2.2 on 2019-04-23 16:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20190422_1833'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='avatar',
            field=models.ImageField(blank=True, default='default_avatar.png', null=True, upload_to='', verbose_name='avatar'),
        ),
    ]
