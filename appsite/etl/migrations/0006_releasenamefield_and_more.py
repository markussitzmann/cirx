# Generated by Django 4.0.4 on 2022-09-07 16:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('resolver', '0001_initial'),
        ('etl', '0005_alter_structurefilerecordrelease_table'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReleaseNameField',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_regid', models.BooleanField(default=False)),
                ('name_field', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='name_fields', to='etl.structurefilefield')),
                ('name_type', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='name_fields', to='resolver.nametype')),
                ('release', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='name_fields', to='resolver.release')),
            ],
            options={
                'db_table': 'cir_release_name_field',
            },
        ),
        migrations.DeleteModel(
            name='StructureFileCollectionNameField',
        ),
        migrations.AddConstraint(
            model_name='releasenamefield',
            constraint=models.UniqueConstraint(fields=('release', 'name_field', 'name_type'), name='unique_release_name_field_constraint'),
        ),
    ]
