# Generated by Django 4.0.4 on 2022-10-31 23:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resolver', '0005_remove_structurenameassociation_resolver_structurenameassociation_page_count_range_and_more'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='structurenameassociation',
            constraint=models.CheckConstraint(check=models.Q(('confidence__range', (1, 100))), name='structure_name_association_confidence_limits'),
        ),
    ]