# Generated by Django 2.2.4 on 2022-04-09 19:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FeedBack',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_captured', models.DateTimeField(auto_now_add=True)),
                ('type', models.CharField(choices=[('X', 'Select'), ('B', 'Bug'), ('T', 'Comment'), ('S', 'Suggestion'), ('F', 'Request Feature'), ('C', 'Complaint'), ('M', 'Compliance'), ('M', 'I Got A Job')], default='X', max_length=1)),
                ('details', models.TextField()),
                ('optional_1', models.TextField(blank=True, null=True, verbose_name='What do you like about MyWeXlog')),
                ('optional_2', models.TextField(blank=True, null=True, verbose_name="What don't you like about MyWeXlog")),
                ('responded', models.BooleanField(default=False)),
                ('slug', models.SlugField(blank=True, null=True, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='FeedBackActions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_reviewed', models.DateTimeField(auto_now_add=True)),
                ('actions', models.TextField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Notices',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notice_date', models.DateTimeField()),
                ('subject', models.CharField(max_length=200, null=True)),
                ('notice', models.TextField(null=True)),
                ('slug', models.SlugField(blank=True, max_length=10, null=True, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='NoticeRead',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_read', models.DateTimeField(auto_now_add=True)),
                ('notice_read', models.BooleanField(default=False, null=True)),
                ('notice', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='feedback.Notices')),
            ],
        ),
    ]
