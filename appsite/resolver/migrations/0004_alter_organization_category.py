# Generated by Django 4.2.8 on 2024-03-31 14:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resolver', '0003_delete_pubchemstructurenamecids'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='category',
            field=models.CharField(choices=[('regulatory', 'Regulatory'), ('government', 'Government'), ('academia', 'Academia'), ('company', 'Company'), ('vendor', 'Vendor'), ('research', 'Research'), ('publishing', 'Publishing'), ('provider', 'Provider'), ('public', 'Public'), ('society', 'Society'), ('charity', 'Charity'), ('non-profit', 'Non-Profit'), ('other', 'Other'), ('none', 'None'), ('generic', 'Generic')], default='none', max_length=16),
        ),
    ]