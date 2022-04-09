# Generated by Django 2.2.4 on 2022-04-09 19:06

from django.db import migrations, models
import django.db.models.deletion
import django_countries.fields
import tinymce.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('enterprises', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250, verbose_name='Project name')),
                ('country', django_countries.fields.CountryField(max_length=2)),
                ('slug', models.SlugField(blank=True, null=True, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProjectPersonalDetails',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', tinymce.models.HTMLField(blank=True, null=True, verbose_name='Personal responsibilities description')),
                ('company', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='enterprises.Enterprise', verbose_name='Owner')),
                ('companybranch', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='enterprises.Branch', verbose_name='Branch Working for on the Project')),
                ('project', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='project.ProjectData')),
            ],
        ),
    ]
