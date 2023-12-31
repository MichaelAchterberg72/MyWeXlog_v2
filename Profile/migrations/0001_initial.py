# Generated by Django 2.2.4 on 2022-04-09 19:06

import Profile.models
import WeXlog.storage_backends
import django.core.validators
from django.db import migrations, models
import django_countries.fields
import phonenumber_field.modelfields
import tinymce.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BriefCareerHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', tinymce.models.HTMLField(blank=True, null=True)),
                ('reason_for_leaving', models.TextField(blank=True, null=True, verbose_name='Reason for leaving')),
                ('current', models.BooleanField(default=False)),
                ('date_captured', models.DateField(auto_now_add=True)),
                ('date_from', models.DateField()),
                ('date_to', models.DateField(blank=True, null=True)),
                ('slug', models.SlugField(blank=True, max_length=15, null=True, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Email',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('active', models.BooleanField(default=False)),
                ('slug', models.SlugField(blank=True, max_length=9, null=True, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='FileUpload',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=150)),
                ('file', models.FileField(storage=WeXlog.storage_backends.PrivateMediaStorage(), upload_to=Profile.models.ExtFilename, validators=[django.core.validators.FileExtensionValidator(['pdf'])])),
                ('thumbnail', models.ImageField(blank=True, null=True, storage=WeXlog.storage_backends.PrivateMediaStorage(), upload_to=Profile.models.ExtThumbnail)),
            ],
        ),
        migrations.CreateModel(
            name='IdentificationDetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identification', models.CharField(max_length=20, null=True, unique=True, verbose_name='Identification number')),
            ],
        ),
        migrations.CreateModel(
            name='IdType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='LanguageTrack',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.CharField(choices=[('B', 'Basic'), ('G', 'Good'), ('F', 'Fluent'), ('H', 'Home Language')], default='B', max_length=1)),
                ('slug', models.SlugField(blank=True, max_length=15, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='OnlineRegistrations',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profileurl', models.URLField()),
            ],
        ),
        migrations.CreateModel(
            name='PassportDetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('passport_number', models.CharField(blank=True, max_length=20, null=True, unique=True)),
                ('issue', django_countries.fields.CountryField(max_length=2, null=True, verbose_name='Country issued in')),
                ('expiry_date', models.DateField(null=True)),
                ('slug', models.SlugField(blank=True, max_length=20, null=True, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='PhoneNumber',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', phonenumber_field.modelfields.PhoneNumberField(max_length=128, region=None)),
                ('current', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='PhysicalAddress',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('line1', models.CharField(blank=True, max_length=250, null=True, verbose_name='Address Line 1')),
                ('line2', models.CharField(blank=True, max_length=250, null=True, verbose_name='Address Line 2')),
                ('line3', models.CharField(blank=True, max_length=100, null=True, verbose_name='Address Line 3')),
                ('country', django_countries.fields.CountryField(max_length=2, null=True)),
                ('code', models.CharField(max_length=12, null=True, verbose_name='Postal Code')),
            ],
        ),
        migrations.CreateModel(
            name='PostalAddress',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('line1', models.CharField(blank=True, max_length=100, null=True, verbose_name='Address Line 1')),
                ('line2', models.CharField(blank=True, max_length=100, null=True, verbose_name='Address Line 2')),
                ('line3', models.CharField(blank=True, max_length=100, null=True, verbose_name='Address Line 3')),
                ('country', django_countries.fields.CountryField(max_length=2)),
                ('code', models.CharField(max_length=12, null=True, verbose_name='Postal Code')),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('f_name', models.CharField(max_length=30, null=True)),
                ('l_name', models.CharField(max_length=30, null=True)),
                ('alias', models.CharField(max_length=30, null=True, unique=True)),
                ('public_profile_intro', tinymce.models.HTMLField(blank=True, max_length=460, null=True)),
                ('birth_date', models.DateField(null=True, verbose_name='Date of Birth')),
                ('background', tinymce.models.HTMLField(blank=True, null=True)),
                ('mentor', models.CharField(choices=[('Y', 'Yes'), ('N', 'No')], default='N', max_length=1, verbose_name='Do you wish to be a mentor?')),
                ('std_rate', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('rate_unit', models.CharField(choices=[('H', 'per Hour'), ('D', 'per Day'), ('M', 'per Month'), ('L', 'Lump Sum')], default='H', max_length=1)),
                ('motivation', tinymce.models.HTMLField(blank=True, null=True)),
                ('rate_1', models.FloatField(default=0, null=True)),
                ('rate_2', models.FloatField(default=0, null=True)),
                ('rate_3', models.FloatField(default=0, null=True)),
                ('rate_count', models.IntegerField(default=0, null=True)),
                ('confirm_check', models.BooleanField(default=False, null=True)),
                ('accepted_terms', models.BooleanField(default=False)),
                ('age_accept', models.BooleanField(default=False, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProfileImages',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profile_pic', models.ImageField(blank=True, null=True, storage=WeXlog.storage_backends.PrivateMediaStorage(), upload_to=Profile.models.ProfilePic)),
                ('profile_background', models.ImageField(blank=True, null=True, storage=WeXlog.storage_backends.PrivateMediaStorage(), upload_to=Profile.models.BackgroundPic)),
            ],
        ),
        migrations.CreateModel(
            name='SiteName',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('site', models.CharField(max_length=40, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='WillingToRelocate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country', django_countries.fields.CountryField(max_length=2)),
                ('documents', models.BooleanField(default=False)),
                ('slug', models.SlugField(blank=True, max_length=9, null=True, unique=True)),
            ],
        ),
    ]
