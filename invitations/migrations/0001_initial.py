# Generated by Django 2.2.4 on 2022-04-09 19:06

from django.db import migrations, models
import django.db.models.deletion
import tinymce.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('enterprises', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Invitation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=45, verbose_name='First Name')),
                ('surname', models.CharField(max_length=45, verbose_name='Surname')),
                ('relationship', models.CharField(choices=[('LR', 'Lecturer'), ('CM', 'Class Mate'), ('WC', 'Colleague'), ('WS', 'Superior'), ('WL', 'Collaborator'), ('WT', 'Client'), ('PC', 'Colleague'), ('AF', 'Acqaintance / Friend')], max_length=2, null=True)),
                ('message', tinymce.models.HTMLField(blank=True, null=True)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('date_invited', models.DateTimeField(auto_now_add=True)),
                ('accpeted', models.BooleanField(default=False, null=True)),
                ('date_accepted', models.DateTimeField(auto_now=True)),
                ('assigned', models.BooleanField(default=False, verbose_name='Assigned since registration')),
                ('companybranch', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='enterprises.Branch', verbose_name='Who did they work for at the time')),
            ],
        ),
    ]
