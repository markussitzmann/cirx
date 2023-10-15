# Generated by Django 4.2.3 on 2023-10-15 16:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('resolver', '0001_initial'),
        ('etl', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='StructureCalcInChIStatus',
            fields=[
                ('structure_file', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='calcinchi_status', serialize=False, to='etl.structurefile')),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
                ('progress', models.FloatField(default=0.0)),
            ],
            options={
                'db_table': 'cir_structure_file_calcinchi_status',
            },
        ),
        migrations.CreateModel(
            name='StructureFileLinkNameStatus',
            fields=[
                ('structure_file', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='linkname_status', serialize=False, to='etl.structurefile')),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
                ('progress', models.FloatField(default=0.0)),
            ],
            options={
                'db_table': 'cir_structure_file_structure_linkname_status',
            },
        ),
        migrations.CreateModel(
            name='StructureFileNormalizationStatus',
            fields=[
                ('structure_file', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='normalization_status', serialize=False, to='etl.structurefile')),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
                ('progress', models.FloatField(default=0.0)),
            ],
            options={
                'db_table': 'cir_structure_file_normalization_status',
            },
        ),
        migrations.CreateModel(
            name='StructureFileSource',
            fields=[
                ('structure', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, primary_key=True, related_name='structure_file_source', serialize=False, to='resolver.structure')),
                ('structure_file', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='structure_file_source', to='etl.structurefile')),
            ],
            options={
                'db_table': 'cir_structure_file_source',
            },
        ),
        migrations.AddField(
            model_name='structurefilerecordrelease',
            name='release',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='structure_file_records', to='resolver.release'),
        ),
        migrations.AddField(
            model_name='structurefilerecordrelease',
            name='structure_file_record',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='structure_file_record_releases', to='etl.structurefilerecord'),
        ),
        migrations.AddField(
            model_name='structurefilerecordnameassociation',
            name='name',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='resolver.name'),
        ),
        migrations.AddField(
            model_name='structurefilerecordnameassociation',
            name='name_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='resolver.nametype'),
        ),
        migrations.AddField(
            model_name='structurefilerecordnameassociation',
            name='structure_file_record',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='structure_file_record_name_associations', to='etl.structurefilerecord'),
        ),
        migrations.AddField(
            model_name='structurefilerecord',
            name='names',
            field=models.ManyToManyField(through='etl.StructureFileRecordNameAssociation', to='resolver.name'),
        ),
        migrations.AddField(
            model_name='structurefilerecord',
            name='releases',
            field=models.ManyToManyField(through='etl.StructureFileRecordRelease', to='resolver.release'),
        ),
        migrations.AddField(
            model_name='structurefilerecord',
            name='structure',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='structure_file_records', to='resolver.structure'),
        ),
        migrations.AddField(
            model_name='structurefilerecord',
            name='structure_file',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='structure_file_records', to='etl.structurefile'),
        ),
        migrations.AddField(
            model_name='structurefilefield',
            name='structure_files',
            field=models.ManyToManyField(related_name='fields', to='etl.structurefile'),
        ),
        migrations.AddConstraint(
            model_name='structurefilecollectionpreprocessor',
            constraint=models.UniqueConstraint(fields=('name', 'params'), name='unique_file_collection_preprocessor_constraint'),
        ),
        migrations.AddField(
            model_name='structurefilecollection',
            name='preprocessors',
            field=models.ManyToManyField(related_name='collections', to='etl.structurefilecollectionpreprocessor'),
        ),
        migrations.AddField(
            model_name='structurefilecollection',
            name='release',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='collections', to='resolver.release'),
        ),
        migrations.AddField(
            model_name='structurefile',
            name='collection',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='files', to='etl.structurefilecollection'),
        ),
        migrations.AddField(
            model_name='releasenamefield',
            name='name_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='name_fields', to='resolver.nametype'),
        ),
        migrations.AddField(
            model_name='releasenamefield',
            name='release',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='name_fields', to='resolver.release'),
        ),
        migrations.AddField(
            model_name='releasenamefield',
            name='structure_file_field',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='name_fields', to='etl.structurefilefield'),
        ),
        migrations.AddConstraint(
            model_name='structurefilerecordrelease',
            constraint=models.UniqueConstraint(fields=('structure_file_record', 'release'), name='unique_structure_file_record_release_constraint'),
        ),
        migrations.AddConstraint(
            model_name='structurefilerecordnameassociation',
            constraint=models.UniqueConstraint(fields=('name', 'structure_file_record', 'name_type'), name='structure_file_record_names'),
        ),
        migrations.AddConstraint(
            model_name='structurefilerecord',
            constraint=models.UniqueConstraint(fields=('structure_file', 'number'), name='unique_structure_file_record_constraint'),
        ),
        migrations.AddConstraint(
            model_name='structurefilecollection',
            constraint=models.UniqueConstraint(fields=('release', 'file_location_pattern_string'), name='unique_file_collection_constraint'),
        ),
        migrations.AddConstraint(
            model_name='structurefile',
            constraint=models.UniqueConstraint(fields=('collection', 'file'), name='unique_structure_file_constraint'),
        ),
        migrations.AddConstraint(
            model_name='releasenamefield',
            constraint=models.UniqueConstraint(fields=('release', 'structure_file_field', 'name_type'), name='unique_release_name_field_constraint'),
        ),
    ]
