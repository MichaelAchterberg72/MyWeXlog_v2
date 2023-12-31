# Generated by Django 2.2 on 2023-04-09 11:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('enterprises', '0001_initial'),
        ('project', '0002_auto_20220409_1906'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Timesheet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_captured', models.DateField(auto_now_add=True)),
                ('date', models.DateField()),
                ('details', models.TextField(blank=True, null=True)),
                ('time_from', models.DateTimeField()),
                ('time_to', models.DateTimeField()),
                ('location', models.CharField(blank=True, max_length=30, null=True)),
                ('out_of_office', models.BooleanField(default=False)),
                ('notification', models.CharField(choices=[('E', 'Email'), ('N', 'Notification')], default='N', max_length=1)),
                ('notification_time', models.CharField(blank=True, max_length=1, null=True)),
                ('notification_duration', models.CharField(choices=[('M', 'minutes'), ('H', 'hours'), ('D', 'days'), ('W', 'weeks')], default='M', max_length=1)),
                ('busy', models.CharField(choices=[('H', "Doesn't repeat"), ('D', 'Daily'), ('W', 'Weekly'), ('M', 'Monthly'), ('A', 'Annualy'), ('L', 'Every weekday (Monday to Friday)'), ('C', 'Custom')], default='B', max_length=1)),
                ('repeat', models.CharField(choices=[('H', "Doesn't repeat"), ('D', 'Daily'), ('W', 'Weekly'), ('M', 'Monthly'), ('A', 'Annualy'), ('L', 'Every weekday (Monday to Friday)'), ('C', 'Custom')], default='H', max_length=1)),
                ('include_for_certificate', models.BooleanField(default=False)),
                ('include_for_invoice', models.BooleanField(default=False)),
                ('client', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='enterprises.Branch', verbose_name='Client')),
                ('project', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='project.ProjectPersonalDetails')),
                ('talent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
