# Generated by Django 3.2.7 on 2021-10-14 21:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('simple', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='simple',
            old_name='simple_text',
            new_name='text',
        ),
    ]