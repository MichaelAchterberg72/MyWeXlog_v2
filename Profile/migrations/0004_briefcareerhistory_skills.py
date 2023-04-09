# Generated by Django 2.2.4 on 2022-04-09 19:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('db_flatten', '0001_initial'),
        ('Profile', '0003_remove_briefcareerhistory_skills'),
    ]

    operations = [
        migrations.AddField(
            model_name='briefcareerhistory',
            name='skills',
            field=models.ManyToManyField(related_name='skills_utilised', to='db_flatten.SkillTag'),
        ),
    ]