# Generated by Django 4.0.4 on 2022-07-24 21:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('etl', '0001_initial'),
        ('resolver', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='structurefilerecord',
            name='structure',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='structure_file_records', to='resolver.structure'),
        ),
        migrations.AddField(
            model_name='structurefilerecord',
            name='structure_file',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='etl.structurefile'),
        ),
        migrations.AddField(
            model_name='structurefilefield',
            name='structure_files',
            field=models.ManyToManyField(related_name='fields', to='etl.structurefile'),
        ),
        migrations.AddField(
            model_name='structurefilecollectionnamefield',
            name='collection',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='collection_name_field', to='etl.structurefilecollection'),
        ),
        migrations.AddField(
            model_name='structurefilecollectionnamefield',
            name='field',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='collection_name_field', to='etl.structurefilefield'),
        ),
        migrations.AddField(
            model_name='structurefilecollectionnamefield',
            name='name_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='collection_name_field', to='resolver.nametype'),
        ),
        migrations.AddField(
            model_name='structurefilecollection',
            name='release',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='collections', to='resolver.release'),
        ),
        migrations.AddField(
            model_name='structurefile',
            name='collection',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='files', to='etl.structurefilecollection'),
        ),
        migrations.AddConstraint(
            model_name='structurefilerecord',
            constraint=models.UniqueConstraint(fields=('structure_file', 'number'), name='unique_structure_file__record_constraint'),
        ),
        migrations.AddConstraint(
            model_name='structurefilecollectionnamefield',
            constraint=models.UniqueConstraint(fields=('collection_id', 'field', 'name_type'), name='unique_structure_file_collection_name_field_constraint'),
        ),
        migrations.AddConstraint(
            model_name='structurefilecollection',
            constraint=models.UniqueConstraint(fields=('release', 'file_location_pattern_string'), name='unique_file_collection_constraint'),
        ),
        migrations.AddConstraint(
            model_name='structurefile',
            constraint=models.UniqueConstraint(fields=('collection', 'file'), name='unique_structure_file_constraint'),
        ),
    ]
