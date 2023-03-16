# Generated by Django 4.0.4 on 2023-03-14 22:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AccessClient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('string', models.CharField(max_length=255, unique=True)),
            ],
            options={
                'db_table': 'cir_access_client',
            },
        ),
        migrations.CreateModel(
            name='AccessHost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('string', models.CharField(max_length=255, unique=True)),
                ('blocked', models.IntegerField()),
                ('lock_timestamp', models.DateTimeField(db_column='lock_time')),
                ('current_sleep_period', models.IntegerField()),
                ('force_sleep_period', models.IntegerField()),
                ('force_block', models.IntegerField()),
            ],
            options={
                'db_table': 'cir_access_host',
            },
        ),
        migrations.CreateModel(
            name='AccessOrganization',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('string', models.CharField(max_length=255, unique=True)),
            ],
            options={
                'db_table': 'cir_access_organization',
            },
        ),
        migrations.CreateModel(
            name='StructureFormula',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('formula', models.CharField(max_length=50, unique=True)),
            ],
            options={
                'db_table': 'cir_structure_formula',
            },
        ),
        migrations.CreateModel(
            name='UsageMonth',
            fields=[
                ('month_year', models.CharField(max_length=2, primary_key=True, serialize=False)),
                ('month', models.IntegerField()),
                ('year', models.IntegerField()),
                ('requests', models.IntegerField()),
                ('ip_counts', models.IntegerField()),
                ('average', models.DecimalField(decimal_places=2, max_digits=5)),
            ],
            options={
                'db_table': 'cir_usage_month',
            },
        ),
        migrations.CreateModel(
            name='UsageMonthDay',
            fields=[
                ('month_day', models.CharField(max_length=2, primary_key=True, serialize=False)),
                ('month', models.IntegerField()),
                ('day', models.IntegerField()),
                ('requests', models.IntegerField()),
                ('ip_counts', models.IntegerField()),
            ],
            options={
                'db_table': 'cir_usage_month_day',
            },
        ),
        migrations.CreateModel(
            name='UsageSeconds',
            fields=[
                ('requests', models.IntegerField(primary_key=True, serialize=False)),
            ],
            options={
                'db_table': 'cir_usage_seconds',
            },
        ),
        migrations.CreateModel(
            name='ResponseType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(max_length=128)),
                ('method', models.CharField(blank=True, max_length=255, null=True)),
                ('parameter', models.CharField(blank=True, max_length=1024, null=True)),
                ('base_mime_type', models.CharField(max_length=255)),
                ('parent_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='structure.responsetype')),
            ],
            options={
                'verbose_name': 'Response Type',
                'verbose_name_plural': 'Response Types',
                'db_table': 'cir_response_type',
            },
        ),
        migrations.CreateModel(
            name='Response',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fromString', models.TextField()),
                ('response', models.TextField(db_column='string')),
                ('responseFile', models.FileField(max_length=255, upload_to='tmp')),
                ('type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='structure.responsetype')),
            ],
            options={
                'db_table': 'cir_response',
            },
        ),
        migrations.CreateModel(
            name='AccessHostOrganization',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('host', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='structure.accesshost')),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='structure.accessorganization')),
            ],
            options={
                'db_table': 'cir_access_host_organization',
                'unique_together': {('host', 'organization')},
            },
        ),
        migrations.AddField(
            model_name='accesshost',
            name='organization',
            field=models.ManyToManyField(through='structure.AccessHostOrganization', to='structure.accessorganization'),
        ),
        migrations.CreateModel(
            name='Access',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now=True, db_column='dateTime')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='structure.accessclient')),
                ('host', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='structure.accesshost')),
            ],
            options={
                'db_table': 'cir_access',
            },
        ),
    ]
