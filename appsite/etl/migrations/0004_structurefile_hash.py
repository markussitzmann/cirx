# Generated by Django 4.2.3 on 2023-11-04 23:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('etl', '0003_alter_structurefiletag_process'),
    ]

    operations = [
        migrations.AddField(
            model_name='structurefile',
            name='hash',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
    ]
