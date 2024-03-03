# Generated by Django 4.2.8 on 2024-02-10 00:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('resolver', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PubchemStructureNameCIDs',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cid', models.IntegerField()),
                ('name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pubchem_structure_name_cids', to='resolver.name')),
            ],
            options={
                'verbose_name': 'PubchemStructureNameCIDs',
                'verbose_name_plural': 'PubchemStructureNameCIDs',
                'db_table': 'cir_pubchem_structure_name_cid',
            },
        ),
        migrations.AddConstraint(
            model_name='pubchemstructurenamecids',
            constraint=models.UniqueConstraint(fields=('name', 'cid'), name='unique_pubchem_structure_name_cid_constraint'),
        ),
    ]
