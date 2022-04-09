# Generated by Django 2.2 on 2021-06-27 09:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('db_flatten', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('locations', '0001_initial'),
        ('marketplace', '0001_initial'),
        ('referrals', '0004_auto_20210627_0913'),
        ('talenttrack', '0001_initial'),
        ('Profile', '0001_initial'),
        ('enterprises', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='willingtorelocate',
            name='talent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='profileimages',
            name='talent',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='profile',
            name='currency',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='locations.Currency'),
        ),
        migrations.AddField(
            model_name='profile',
            name='exp_lvl',
            field=models.ForeignKey(default=1, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='profile_tenure', to='marketplace.SkillLevel'),
        ),
        migrations.AddField(
            model_name='profile',
            name='referral_code',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='referrals.Referral'),
        ),
        migrations.AddField(
            model_name='profile',
            name='talent',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='postaladdress',
            name='city',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='locations.City'),
        ),
        migrations.AddField(
            model_name='postaladdress',
            name='region',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='locations.Region'),
        ),
        migrations.AddField(
            model_name='postaladdress',
            name='suburb',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='locations.Suburb'),
        ),
        migrations.AddField(
            model_name='postaladdress',
            name='talent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='physicaladdress',
            name='city',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='locations.City'),
        ),
        migrations.AddField(
            model_name='physicaladdress',
            name='region',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='locations.Region'),
        ),
        migrations.AddField(
            model_name='physicaladdress',
            name='suburb',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='locations.Suburb'),
        ),
        migrations.AddField(
            model_name='physicaladdress',
            name='talent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='phonenumber',
            name='talent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='phonenumber',
            name='type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='db_flatten.PhoneNumberType'),
        ),
        migrations.AddField(
            model_name='passportdetail',
            name='talent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='onlineregistrations',
            name='sitename',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='Site_Name', to='Profile.SiteName'),
        ),
        migrations.AddField(
            model_name='onlineregistrations',
            name='talent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='languagetrack',
            name='language',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='db_flatten.LanguageList'),
        ),
        migrations.AddField(
            model_name='languagetrack',
            name='talent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='identificationdetail',
            name='id_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='Profile.IdType', verbose_name='Identification_type'),
        ),
        migrations.AddField(
            model_name='identificationdetail',
            name='talent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='fileupload',
            name='talent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='email',
            name='company',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='enterprises.Enterprise'),
        ),
        migrations.AddField(
            model_name='email',
            name='talent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Customuser_email', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='briefcareerhistory',
            name='companybranch',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='enterprises.Branch', verbose_name='Home_Base'),
        ),
        migrations.AddField(
            model_name='briefcareerhistory',
            name='designation',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='talenttrack.Designation'),
        ),
        migrations.AddField(
            model_name='briefcareerhistory',
            name='talent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='briefcareerhistory',
            name='work_configeration',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='marketplace.WorkLocation'),
        ),
        migrations.AlterUniqueTogether(
            name='willingtorelocate',
            unique_together={('talent', 'country')},
        ),
        migrations.AlterUniqueTogether(
            name='passportdetail',
            unique_together={('talent', 'passport_number')},
        ),
        migrations.AlterUniqueTogether(
            name='onlineregistrations',
            unique_together={('profileurl', 'sitename')},
        ),
        migrations.AlterUniqueTogether(
            name='languagetrack',
            unique_together={('talent', 'language')},
        ),
        migrations.AlterUniqueTogether(
            name='identificationdetail',
            unique_together={('talent', 'identification')},
        ),
        migrations.AlterUniqueTogether(
            name='email',
            unique_together={('talent', 'email')},
        ),
    ]
