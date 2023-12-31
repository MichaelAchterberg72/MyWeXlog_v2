# Generated by Django 2.2.4 on 2022-04-09 19:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('talenttrack', '0001_initial'),
        ('enterprises', '0001_initial'),
        ('db_flatten', '0001_initial'),
        ('marketplace', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('locations', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='workissuedto',
            name='talent',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='Successful_talent', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='workissuedto',
            name='tlt_decline_reason',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='marketplace.DeclineAssignment'),
        ),
        migrations.AddField(
            model_name='workissuedto',
            name='work',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='marketplace.TalentRequired'),
        ),
        migrations.AddField(
            model_name='workbid',
            name='currency',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='locations.Currency'),
        ),
        migrations.AddField(
            model_name='workbid',
            name='talent',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='workbid',
            name='work',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='marketplace.TalentRequired'),
        ),
        migrations.AddField(
            model_name='vacancyviewed',
            name='talent',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='vacancyviewed',
            name='vacancy',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='marketplace.TalentRequired'),
        ),
        migrations.AddField(
            model_name='vacancyrate',
            name='talent',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='vacancyrate',
            name='vacancy',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='marketplace.TalentRequired'),
        ),
        migrations.AddField(
            model_name='talentrequired',
            name='certification',
            field=models.ManyToManyField(blank=True, to='talenttrack.Result', verbose_name='Certifications Required'),
        ),
        migrations.AddField(
            model_name='talentrequired',
            name='city',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='locations.City', verbose_name='City, Town or Place'),
        ),
        migrations.AddField(
            model_name='talentrequired',
            name='companybranch',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='enterprises.Branch', verbose_name='Company'),
        ),
        migrations.AddField(
            model_name='talentrequired',
            name='currency',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='locations.Currency'),
        ),
        migrations.AddField(
            model_name='talentrequired',
            name='designation',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='talenttrack.Designation'),
        ),
        migrations.AddField(
            model_name='talentrequired',
            name='experience_level',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='marketplace.SkillLevel'),
        ),
        migrations.AddField(
            model_name='talentrequired',
            name='language',
            field=models.ManyToManyField(to='db_flatten.LanguageList'),
        ),
        migrations.AddField(
            model_name='talentrequired',
            name='requested_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='talentrequired',
            name='worklocation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='marketplace.WorkLocation'),
        ),
        migrations.AddField(
            model_name='talentrate',
            name='talent',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='talentrate',
            name='vacancy',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='marketplace.TalentRequired'),
        ),
        migrations.AddField(
            model_name='talentavailabillity',
            name='talent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='skillrequired',
            name='scope',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='marketplace.TalentRequired'),
        ),
        migrations.AddField(
            model_name='skillrequired',
            name='skills',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='db_flatten.SkillTag'),
        ),
        migrations.AddField(
            model_name='deliverables',
            name='scope',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='marketplace.TalentRequired'),
        ),
        migrations.AddField(
            model_name='bidshortlist',
            name='scope',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='marketplace.TalentRequired'),
        ),
        migrations.AddField(
            model_name='bidshortlist',
            name='talent',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='Shortlisted', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='bidinterviewlist',
            name='scope',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='marketplace.TalentRequired'),
        ),
        migrations.AddField(
            model_name='bidinterviewlist',
            name='talent',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='Interviewed', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='bidinterviewlist',
            name='tlt_decline_reason',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='marketplace.DeclineAssignment'),
        ),
        migrations.AlterUniqueTogether(
            name='workissuedto',
            unique_together={('talent', 'work')},
        ),
        migrations.AlterUniqueTogether(
            name='workbid',
            unique_together={('talent', 'work')},
        ),
        migrations.AlterUniqueTogether(
            name='vacancyrate',
            unique_together={('vacancy', 'talent')},
        ),
        migrations.AlterUniqueTogether(
            name='talentrequired',
            unique_together={('companybranch', 'own_ref_no'), ('companybranch', 'title', 'requested_by')},
        ),
        migrations.AlterUniqueTogether(
            name='talentrate',
            unique_together={('vacancy', 'talent')},
        ),
        migrations.AlterUniqueTogether(
            name='deliverables',
            unique_together={('scope', 'deliverable')},
        ),
        migrations.AlterUniqueTogether(
            name='bidshortlist',
            unique_together={('talent', 'scope')},
        ),
        migrations.AlterUniqueTogether(
            name='bidinterviewlist',
            unique_together={('talent', 'scope')},
        ),
    ]
