# Generated by Django 2.2 on 2023-05-13 13:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('booklist', '0002_auto_20220409_1906'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booklist',
            name='publisher',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='booklist.Publisher'),
        ),
        migrations.AlterField(
            model_name='booklist',
            name='type',
            field=models.CharField(choices=[('F', 'Fiction'), ('N', 'Non_fiction')], default='F', max_length=1),
        ),
    ]
