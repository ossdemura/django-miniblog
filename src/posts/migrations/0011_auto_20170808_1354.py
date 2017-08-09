# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-08-08 11:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0010_auto_20170808_1034'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='type',
            field=models.CharField(choices=[('T', 'Topic'), ('P', 'Personal')], default='T', max_length=1),
        ),
    ]