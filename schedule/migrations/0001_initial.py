# Generated by Django 2.2 on 2023-04-09 11:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import tinymce.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('enterprises', '0001_initial'),
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('db_flatten', '0001_initial'),
        ('project', '0003_auto_20230409_1120'),
    ]

    operations = [
        migrations.CreateModel(
            name='Calendar',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='name')),
                ('slug', models.SlugField(max_length=200, unique=True, verbose_name='slug')),
                ('talent', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'calendar',
                'verbose_name_plural': 'calendars',
            },
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start', models.DateTimeField(db_index=True, verbose_name='start')),
                ('end', models.DateTimeField(db_index=True, help_text='The end time must be later than the start time.', verbose_name='end')),
                ('title', models.CharField(max_length=255, verbose_name='title')),
                ('description', models.TextField(blank=True, verbose_name='description')),
                ('created_on', models.DateTimeField(auto_now_add=True, verbose_name='created on')),
                ('updated_on', models.DateTimeField(auto_now=True, verbose_name='updated on')),
                ('end_recurring_period', models.DateTimeField(blank=True, db_index=True, help_text='This date is ignored for one time only events.', null=True, verbose_name='end recurring period')),
                ('color_event', models.CharField(blank=True, max_length=10, null=True, verbose_name='Color event')),
                ('calendar', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='schedule.Calendar', verbose_name='calendar')),
                ('companybranch', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='enterprises.Branch', verbose_name='Branch Working for on Project')),
                ('creator', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='creator', to=settings.AUTH_USER_MODEL, verbose_name='creator')),
                ('project_data', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='project.ProjectPersonalDetails', verbose_name='Personal Project Details')),
            ],
            options={
                'verbose_name': 'event',
                'verbose_name_plural': 'events',
            },
        ),
        migrations.CreateModel(
            name='NotePad',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True, verbose_name='created on')),
                ('updated_on', models.DateTimeField(auto_now=True, verbose_name='updated on')),
                ('heading', models.CharField(max_length=240, null=True)),
                ('note_pad', tinymce.models.HTMLField(blank=True, null=True)),
                ('date_due', models.DateTimeField(blank=True, null=True, verbose_name='due on')),
                ('complete', models.BooleanField(default=False)),
                ('date_complete', models.DateTimeField(blank=True, null=True, verbose_name='completed on')),
                ('slug', models.SlugField(blank=True, max_length=15, null=True, unique=True)),
                ('companybranch', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='enterprises.Branch', verbose_name='Branch Working for on Project')),
                ('event_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='schedule.Event')),
            ],
        ),
        migrations.CreateModel(
            name='Rule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, verbose_name='name')),
                ('description', models.TextField(verbose_name='description')),
                ('frequency', models.CharField(choices=[('YEARLY', 'Yearly'), ('MONTHLY', 'Monthly'), ('WEEKLY', 'Weekly'), ('DAILY', 'Daily'), ('HOURLY', 'Hourly'), ('MINUTELY', 'Minutely'), ('SECONDLY', 'Secondly')], max_length=10, verbose_name='frequency')),
                ('params', models.TextField(blank=True, verbose_name='params')),
                ('talent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'rule',
                'verbose_name_plural': 'rules',
            },
        ),
        migrations.CreateModel(
            name='Occurrence',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=255, verbose_name='title')),
                ('description', models.TextField(blank=True, verbose_name='description')),
                ('start', models.DateTimeField(db_index=True, verbose_name='start')),
                ('end', models.DateTimeField(db_index=True, verbose_name='end')),
                ('cancelled', models.BooleanField(default=False, verbose_name='cancelled')),
                ('original_start', models.DateTimeField(verbose_name='original start')),
                ('original_end', models.DateTimeField(verbose_name='original end')),
                ('created_on', models.DateTimeField(auto_now_add=True, verbose_name='created on')),
                ('updated_on', models.DateTimeField(auto_now=True, verbose_name='updated on')),
                ('companybranch', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='enterprises.Branch', verbose_name='Branch Working for on Project')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='schedule.Event', verbose_name='event')),
                ('project_data', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='project.ProjectPersonalDetails', verbose_name='Personal Project Details')),
                ('skills', models.ManyToManyField(related_name='occurance_experience', to='db_flatten.SkillTag')),
                ('task', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='project.ProjectPersonalDetailsTask', verbose_name='Tasks')),
            ],
            options={
                'verbose_name': 'occurrence',
                'verbose_name_plural': 'occurrences',
                'index_together': {('start', 'end')},
            },
        ),
        migrations.CreateModel(
            name='NotePadRelatedTask',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notepad_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='schedule.NotePad')),
                ('related_notepad_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='related_notepad', to='schedule.NotePad')),
                ('talent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='NotePadRelatedProject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notepad_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='schedule.NotePad')),
                ('project_data', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='project.ProjectPersonalDetails', verbose_name='Personal Project Details')),
                ('talent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='NotePadRelatedOccurrence',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notepad_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='schedule.NotePad')),
                ('related_occurrence_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='schedule.Occurrence')),
                ('talent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='NotePadRelatedEvent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notepad_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='schedule.NotePad')),
                ('related_event_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='schedule.Event')),
                ('talent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='notepad',
            name='occurrence_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='schedule.Occurrence'),
        ),
        migrations.AddField(
            model_name='notepad',
            name='project_data',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='project.ProjectPersonalDetails', verbose_name='Personal Project Details'),
        ),
        migrations.AddField(
            model_name='notepad',
            name='talent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='notepad',
            name='task',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='project.ProjectPersonalDetailsTask', verbose_name='Tasks'),
        ),
        migrations.AddField(
            model_name='event',
            name='rule',
            field=models.ForeignKey(blank=True, help_text="Select '----' for a one time only event.", null=True, on_delete=django.db.models.deletion.SET_NULL, to='schedule.Rule', verbose_name='rule'),
        ),
        migrations.AddField(
            model_name='event',
            name='skills',
            field=models.ManyToManyField(blank=True, related_name='event_experience', to='db_flatten.SkillTag'),
        ),
        migrations.AddField(
            model_name='event',
            name='task',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='project.ProjectPersonalDetailsTask', verbose_name='Tasks'),
        ),
        migrations.CreateModel(
            name='EventRelation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.IntegerField(db_index=True)),
                ('distinction', models.CharField(max_length=20, verbose_name='distinction')),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='schedule.Event', verbose_name='event')),
            ],
            options={
                'verbose_name': 'event relation',
                'verbose_name_plural': 'event relations',
                'index_together': {('content_type', 'object_id')},
            },
        ),
        migrations.AlterIndexTogether(
            name='event',
            index_together={('start', 'end')},
        ),
        migrations.CreateModel(
            name='CalendarRelation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.IntegerField(db_index=True)),
                ('distinction', models.CharField(blank=True, max_length=20, null=True, verbose_name='distinction')),
                ('inheritable', models.BooleanField(default=True, verbose_name='inheritable')),
                ('calendar', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='schedule.Calendar', verbose_name='calendar')),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
            ],
            options={
                'verbose_name': 'calendar relation',
                'verbose_name_plural': 'calendar relations',
                'index_together': {('content_type', 'object_id')},
            },
        ),
    ]