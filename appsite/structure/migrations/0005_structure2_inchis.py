# Generated by Django 4.0 on 2022-01-14 11:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('structure', '0004_structureinchis'),
    ]

    operations = [
        migrations.AddField(
            model_name='structure2',
            name='inchis',
            field=models.ManyToManyField(related_name='structures', through='structure.StructureInChIs', to='structure.InChI'),
        ),
    ]
