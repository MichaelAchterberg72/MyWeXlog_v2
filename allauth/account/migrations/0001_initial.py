<<<<<<< HEAD
# Generated by Django 2.2 on 2021-06-27 09:13
=======
# Generated by Django 2.2 on 2022-03-19 09:33
>>>>>>> origin/2022-01_MA_1.0.6

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EmailAddress',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='e-mail address')),
                ('verified', models.BooleanField(default=False, verbose_name='verified')),
                ('primary', models.BooleanField(default=False, verbose_name='primary')),
            ],
            options={
                'verbose_name': 'email address',
                'verbose_name_plural': 'email addresses',
            },
        ),
        migrations.CreateModel(
            name='EmailConfirmation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created')),
                ('sent', models.DateTimeField(null=True, verbose_name='sent')),
                ('key', models.CharField(max_length=64, unique=True, verbose_name='key')),
                ('email_address', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='account.EmailAddress', verbose_name='e-mail address')),
            ],
            options={
                'verbose_name': 'email confirmation',
                'verbose_name_plural': 'email confirmations',
            },
        ),
    ]
