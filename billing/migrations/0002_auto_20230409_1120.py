# Generated by Django 2.2 on 2023-04-09 11:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('billing', '0001_initial'),
        ('project', '0003_auto_20230409_1120'),
        ('talenttrack', '0002_auto_20220409_1906'),
    ]

    operations = [
        migrations.AddField(
            model_name='timesheet',
            name='task',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='project.ProjectPersonalDetailsTask', verbose_name='Tasks'),
        ),
        migrations.AddField(
            model_name='timesheet',
            name='work_experience',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='talenttrack.WorkExperience'),
        ),
    ]
