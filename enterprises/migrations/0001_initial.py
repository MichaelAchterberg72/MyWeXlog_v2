# Generated by Django 2.2 on 2022-03-19 09:33

import WeXlog.storage_backends
from django.db import migrations, models
import django.db.models.deletion
import django_countries.fields
import enterprises.models
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('db_flatten', '0001_initial'),
        ('locations', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Branch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Branch or Division Name')),
                ('size', models.CharField(choices=[('A', '1-10'), ('B', '11-50'), ('C', '51-150'), ('D', '151-500'), ('E', '501-1 000'), ('F', '1 001-10 000'), ('G', '10 001+')], default='A', max_length=1, null=True, verbose_name='Branch Size')),
                ('phy_address_line1', models.CharField(blank=True, max_length=150, null=True, verbose_name='Physical address line 1')),
                ('phy_address_line2', models.CharField(blank=True, max_length=150, null=True, verbose_name='Physical address line 2')),
                ('country', django_countries.fields.CountryField(max_length=2, null=True)),
                ('code', models.CharField(max_length=12, null=True, verbose_name='Post Code')),
                ('slug', models.SlugField(blank=True, max_length=60, null=True, unique=True)),
                ('rate_1', models.FloatField(default=0, null=True)),
                ('rate_2', models.FloatField(default=0, null=True)),
                ('rate_3', models.FloatField(default=0, null=True)),
                ('rate_4', models.FloatField(default=0, null=True)),
                ('rate_count', models.IntegerField(default=0, null=True)),
                ('city', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='locations.City')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='BranchType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=70, unique=True)),
            ],
            options={
                'ordering': ['type'],
            },
        ),
        migrations.CreateModel(
            name='Enterprise',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ename', models.CharField(max_length=250, unique=True, verbose_name='Enterprise name')),
                ('slug', models.SlugField(blank=True, max_length=60, null=True, unique=True)),
                ('description', models.TextField(verbose_name='Enterprise description')),
                ('logo', models.ImageField(blank=True, null=True, storage=WeXlog.storage_backends.PrivateMediaStorage(), upload_to=enterprises.models.EnterpriseLogoPic)),
                ('website', models.URLField(blank=True, null=True)),
                ('filter_class', models.CharField(choices=[('P', 'Public'), ('S', 'System')], default='P', max_length=1)),
                ('rate_1', models.FloatField(default=0, null=True)),
                ('rate_2', models.FloatField(default=0, null=True)),
                ('rate_3', models.FloatField(default=0, null=True)),
                ('rate_4', models.FloatField(default=0, null=True)),
                ('rate_count', models.IntegerField(default=0, null=True)),
            ],
            options={
                'ordering': ['ename'],
            },
        ),
        migrations.CreateModel(
            name='Industry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('industry', models.CharField(max_length=60, unique=True)),
            ],
            options={
                'ordering': ['industry'],
            },
        ),
        migrations.CreateModel(
            name='PhoneNumber',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', phonenumber_field.modelfields.PhoneNumberField(max_length=128, region=None)),
                ('existing', models.BooleanField(verbose_name='Number in use')),
                ('branch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='enterprises.Branch')),
                ('type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='Number_type', to='db_flatten.PhoneNumberType')),
            ],
        ),
        migrations.AddField(
            model_name='branch',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='enterprises.Enterprise'),
        ),
        migrations.AddField(
            model_name='branch',
            name='industry',
            field=models.ManyToManyField(to='enterprises.Industry'),
        ),
        migrations.AddField(
            model_name='branch',
            name='region',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='locations.Region'),
        ),
        migrations.AddField(
            model_name='branch',
            name='suburb',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='locations.Suburb'),
        ),
        migrations.AddField(
            model_name='branch',
            name='type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='enterprises.BranchType'),
        ),
        migrations.AlterUniqueTogether(
            name='branch',
            unique_together={('company', 'name', 'city')},
        ),
    ]
