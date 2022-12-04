# Generated by Django 4.0.4 on 2022-11-27 23:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resolver', '0008_alter_structurenameassociation_name_type'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='structurenameassociation',
            name='unique_structure_names',
        ),
        migrations.RemoveConstraint(
            model_name='structurenameassociation',
            name='unique_structure_name_affinity',
        ),
        migrations.AddConstraint(
            model_name='structurenameassociation',
            constraint=models.UniqueConstraint(fields=('name', 'structure', 'name_type', 'affinity_class'), name='unique_structure_name_affinity'),
        ),
    ]
