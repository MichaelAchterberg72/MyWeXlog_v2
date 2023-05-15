# Generated by Django 2.2 on 2023-04-09 11:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('room_name', models.CharField(max_length=200, null=True)),
                ('slug', models.SlugField(blank=True, null=True, unique=True)),
                ('description', models.TextField(blank=True, help_text='Add a description for the group!', null=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('room_name', models.CharField(max_length=200, null=True)),
                ('content', models.TextField()),
                ('reply_pk', models.CharField(blank=True, max_length=20, null=True)),
                ('initial_members_count', models.CharField(max_length=20, null=True)),
                ('message_deleted', models.BooleanField(default=False)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='author_messages', to=settings.AUTH_USER_MODEL)),
                ('message_read', models.ManyToManyField(blank=True, related_name='message_read_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='MessageRead',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message_read', models.BooleanField(default=False, null=True)),
                ('read_date', models.DateTimeField(auto_now=True)),
                ('chat_group', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='intmessages.ChatGroup')),
                ('message', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='intmessages.Message')),
                ('talent', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ChatRoomMembers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('room_name', models.CharField(max_length=200, null=True)),
                ('mute_notifications', models.BooleanField(default=False)),
                ('date_joined', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('chat_group', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='intmessages.ChatGroup')),
                ('talent', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]