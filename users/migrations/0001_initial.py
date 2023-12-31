# Generated by Django 2.2.4 on 2022-04-09 19:06

from django.conf import settings
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import users.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('alias', models.CharField(max_length=30, null=True)),
                ('display_text', models.CharField(max_length=250, null=True)),
                ('public_profile_name', models.CharField(max_length=100, null=True, unique=True)),
                ('permit_viewing_of_profile_as_reference', models.BooleanField(blank=True, default=False)),
                ('subscription', models.IntegerField(choices=[(0, 'Free'), (1, 'Passive'), (2, 'Active'), (3, 'MyWeXlog Management')], default=2)),
                ('permission', models.IntegerField(choices=[(0, 'Company Representative'), (1, 'Individual')], default=1)),
                ('role', models.IntegerField(choices=[(0, 'Talent'), (1, 'Beta-Tester'), (2, 'Industry Insider')], default=0)),
                ('registered_date', models.DateTimeField(auto_now_add=True)),
                ('paid', models.BooleanField(blank=True, default=True)),
                ('free_month', models.BooleanField(blank=True, default=True)),
                ('paid_date', models.DateTimeField(blank=True, null=True)),
                ('paid_type', models.IntegerField(choices=[(0, 'Free'), (1, 'Monthly'), (2, 'Six-Monthly'), (3, 'Twelve-Monthly')], default=1)),
                ('invite_code', models.CharField(blank=True, max_length=42, null=True)),
                ('alphanum', models.SlugField(max_length=7, null=True, unique=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', users.models.CustomUserManager()),
            ],
        ),
        migrations.CreateModel(
            name='ExpandedView',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('intro_walkthrough', models.BooleanField(default=False, verbose_name="Don't view intro again")),
                ('trial_expired', models.BooleanField(default=False, verbose_name="Don't view trial again")),
                ('applicants_list', models.BooleanField(default=True)),
                ('applicants_fl_list', models.BooleanField(default=True)),
                ('talent_suited_list', models.BooleanField(default=True)),
                ('talent_fl_suited_list', models.BooleanField(default=True)),
                ('shortlist_list', models.BooleanField(default=True)),
                ('pending_interviews_list', models.BooleanField(default=True)),
                ('pending_fl_interviews_list', models.BooleanField(default=True)),
                ('suitable_applicants_list', models.BooleanField(default=True)),
                ('suitable_fl_applicants_list', models.BooleanField(default=True)),
                ('unsuitable_applicants_list', models.BooleanField(default=True)),
                ('unsuitable_fl_applicants_list', models.BooleanField(default=True)),
                ('rejected_applicants_list', models.BooleanField(default=True)),
                ('rejected_fl_applicants_list', models.BooleanField(default=True)),
                ('vacancies_suited_list', models.BooleanField(default=True)),
                ('vacancies_fl_suited_list', models.BooleanField(default=True)),
                ('talent', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CustomUserSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('right_to_say_no', models.BooleanField(default=False, verbose_name='The right to say no to the sale of personal information')),
                ('unsubscribe', models.BooleanField(default=False, verbose_name='Unsubscribe from all newsletters')),
                ('receive_newsletter', models.BooleanField(default=True, verbose_name='Receive the newsletter')),
                ('validation_requests', models.BooleanField(default=True, verbose_name='Receive validation requests')),
                ('takeout', models.BooleanField(default=False, verbose_name='Export data to a csv file')),
                ('dnt', models.BooleanField(default=False, verbose_name='Do Not Track')),
                ('right_to_be_forgotten', models.BooleanField(default=False, verbose_name='Right to be forgotten / Permanently delete my account')),
                ('payment_notifications', models.BooleanField(default=True, verbose_name='Receive subscription payment notifications')),
                ('subscription_notifications', models.BooleanField(default=True, verbose_name='Receive subscription status notifications')),
                ('privacy', models.BooleanField(default=True, verbose_name='Accept Privacy Policy')),
                ('useragree', models.BooleanField(default=True, verbose_name='Accept User Agreement')),
                ('theme', models.IntegerField(choices=[(0, 'Light Theme'), (1, 'Dark Theme')], default=0)),
                ('talent', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
