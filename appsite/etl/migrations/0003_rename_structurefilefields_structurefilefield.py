# Generated by Django 4.0.2 on 2022-03-09 21:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('etl', '0002_remove_structurefilerecord_hashisy_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='StructureFileFields',
            new_name='StructureFileField',
        ),
    ]
