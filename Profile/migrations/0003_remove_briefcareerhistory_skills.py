# Generated by Django 2.2.4 on 2022-04-09 19:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Profile', '0002_auto_20220409_1906'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='briefcareerhistory',
            name='skills',
        ),
    ]
