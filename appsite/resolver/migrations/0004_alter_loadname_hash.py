# Generated by Django 4.2.3 on 2023-11-26 20:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resolver', '0003_alter_loadname_hash'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loadname',
            name='hash',
            field=models.UUIDField(unique=True),
        ),
    ]
