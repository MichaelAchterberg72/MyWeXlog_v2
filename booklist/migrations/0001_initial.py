# Generated by Django 2.2.4 on 2022-04-09 19:06

from django.db import migrations, models
import django.db.models.deletion
import tinymce.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250, unique=True, verbose_name='Author name')),
            ],
        ),
        migrations.CreateModel(
            name='BookList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=300, unique=True, verbose_name='Book Title')),
                ('type', models.CharField(choices=[('F', 'Fiction'), ('N', 'Non-fiction')], default='F', max_length=1)),
                ('link', models.URLField(blank=True, null=True, verbose_name='Book URL')),
                ('slug', models.SlugField(blank=True, max_length=60, null=True, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Format',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('format', models.CharField(max_length=60, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Publisher',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('publisher', models.CharField(max_length=150, unique=True)),
                ('link', models.URLField(blank=True, null=True, verbose_name='Publisher URL')),
            ],
        ),
        migrations.CreateModel(
            name='ReadBy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(verbose_name='Date Finished')),
                ('review', tinymce.models.HTMLField(blank=True, null=True)),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='booklist.BookList')),
            ],
        ),
    ]