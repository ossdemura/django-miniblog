# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-30 09:39
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0014_auto_20171128_1541'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Event',
        ),
    ]