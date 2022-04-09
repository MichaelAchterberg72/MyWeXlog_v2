# Generated by Django 2.2 on 2021-06-29 17:56

from django.db import migrations
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
        ('Profile', '0002_auto_20210627_0913'),
    ]

    operations = [
        migrations.AlterField(
            model_name='briefcareerhistory',
            name='description',
            field=tinymce.models.HTMLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='background',
            field=tinymce.models.HTMLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='motivation',
            field=tinymce.models.HTMLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='public_profile_intro',
            field=tinymce.models.HTMLField(blank=True, max_length=460, null=True),
        ),
    ]
