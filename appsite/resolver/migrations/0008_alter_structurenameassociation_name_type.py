# Generated by Django 4.0.4 on 2022-10-31 23:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('resolver', '0007_alter_structurenameassociation_table'),
    ]

    operations = [
        migrations.AlterField(
            model_name='structurenameassociation',
            name='name_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='resolver.nametype'),
        ),
    ]