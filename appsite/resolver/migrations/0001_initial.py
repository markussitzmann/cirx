# Generated by Django 4.0.4 on 2022-09-19 14:36

import custom.fields
from django.db import migrations, models
import django.db.models.deletion
import multiselectfield.db.fields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('etl', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Compound',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('added', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('blocked', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'db_table': 'cir_compound',
            },
        ),
        migrations.CreateModel(
            name='ContextTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag', models.CharField(max_length=128, unique=True)),
                ('description', models.TextField(blank=True, max_length=1500, null=True)),
            ],
            options={
                'verbose_name': 'Context Teg',
                'verbose_name_plural': 'Context Tags',
                'db_table': 'cir_dataset_context_tag',
            },
        ),
        migrations.CreateModel(
            name='Dataset',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=768)),
                ('href', models.URLField(blank=True, max_length=4096, null=True)),
                ('description', models.TextField(blank=True, max_length=4096, null=True)),
                ('added', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'cir_dataset',
                'ordering': ['-added'],
            },
        ),
        migrations.CreateModel(
            name='EndPoint',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('uri', models.CharField(max_length=32768)),
                ('category', models.CharField(choices=[('schema', 'Schema'), ('uritemplate', 'URI Template (RFC6570)'), ('documentation', 'Documentation (HTML, PDF)')], default='uritemplate', max_length=16)),
                ('request_methods', multiselectfield.db.fields.MultiSelectField(choices=[('GET', 'GET'), ('HEAD', 'HEAD'), ('POST', 'POST'), ('PUT', 'PUT'), ('DELETE', 'DELETE'), ('CONNECT', 'CONNECT'), ('OPTIONS', 'OPTIONS'), ('TRACE', 'TRACE'), ('PATCH', 'PATCH')], default=['GET'], max_length=16)),
                ('description', models.TextField(blank=True, max_length=32768, null=True)),
                ('added', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'cir_endpoint',
            },
        ),
        migrations.CreateModel(
            name='EntryPoint',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('category', models.CharField(choices=[('self', 'Self'), ('site', 'Site'), ('api', 'API'), ('resolver', 'Resolver')], default='site', max_length=16)),
                ('href', models.URLField(max_length=4096)),
                ('entrypoint_href', models.URLField(blank=True, max_length=4096, null=True)),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('description', models.TextField(blank=True, max_length=32768, null=True)),
                ('added', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'cir_entrypoint',
            },
        ),
        migrations.CreateModel(
            name='InChI',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('version', models.IntegerField(default=1)),
                ('block1', models.CharField(max_length=14)),
                ('block2', models.CharField(max_length=10)),
                ('block3', models.CharField(max_length=1)),
                ('key', models.CharField(max_length=27)),
                ('string', models.CharField(blank=True, max_length=32768, null=True)),
                ('added', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'InChI',
                'verbose_name_plural': 'InChIs',
                'db_table': 'cir_inchi',
            },
        ),
        migrations.CreateModel(
            name='InChIType',
            fields=[
                ('id', models.CharField(editable=False, max_length=32, primary_key=True, serialize=False)),
                ('software_version', models.CharField(blank=True, default=None, max_length=16, null=True)),
                ('description', models.TextField(blank=True, max_length=32768, null=True)),
                ('is_standard', models.BooleanField(default=False)),
                ('newpsoff', models.BooleanField(default=False)),
                ('donotaddh', models.BooleanField(default=False)),
                ('snon', models.BooleanField(default=False)),
                ('srel', models.BooleanField(default=False)),
                ('srac', models.BooleanField(default=False)),
                ('sucf', models.BooleanField(default=False)),
                ('suu', models.BooleanField(default=False)),
                ('sluud', models.BooleanField(default=False)),
                ('recmet', models.BooleanField(default=False)),
                ('fixedh', models.BooleanField(default=False)),
                ('ket', models.BooleanField(default=False)),
                ('t15', models.BooleanField(default=False)),
                ('pt_22_00', models.BooleanField(default=False)),
                ('pt_16_00', models.BooleanField(default=False)),
                ('pt_06_00', models.BooleanField(default=False)),
                ('pt_39_00', models.BooleanField(default=False)),
                ('pt_13_00', models.BooleanField(default=False)),
                ('pt_18_00', models.BooleanField(default=False)),
                ('added', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'cir_inchi_type',
            },
        ),
        migrations.CreateModel(
            name='MediaType',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=1024, unique=True)),
                ('description', models.TextField(blank=True, max_length=32768, null=True)),
                ('added', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'cir_media_type',
            },
        ),
        migrations.CreateModel(
            name='Name',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.TextField(max_length=1500, unique=True)),
            ],
            options={
                'db_table': 'cir_structure_name',
            },
        ),
        migrations.CreateModel(
            name='NameType',
            fields=[
                ('id', models.CharField(editable=False, max_length=64, primary_key=True, serialize=False)),
                ('public_string', models.TextField(blank=True, max_length=64, null=True)),
                ('description', models.TextField(blank=True, max_length=768, null=True)),
            ],
            options={
                'db_table': 'cir_name_type',
            },
        ),
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=32768)),
                ('abbreviation', models.CharField(blank=True, max_length=32, null=True)),
                ('category', models.CharField(choices=[('regulatory', 'Regulatory'), ('government', 'Government'), ('academia', 'Academia'), ('company', 'Company'), ('vendor', 'Vendor'), ('research', 'Research'), ('publishing', 'Publishing'), ('provider', 'Provider'), ('public', 'Public'), ('society', 'Society'), ('charity', 'Charity'), ('other', 'Other'), ('none', 'None'), ('generic', 'Generic')], default='none', max_length=16)),
                ('href', models.URLField(blank=True, max_length=4096, null=True)),
                ('added', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'cir_organization',
            },
        ),
        migrations.CreateModel(
            name='Publisher',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('category', models.CharField(choices=[('entity', 'Entity'), ('service', 'Service'), ('network', 'Network'), ('division', 'Division'), ('group', 'Group'), ('person', 'Person'), ('other', 'Other'), ('none', 'None'), ('generic', 'Generic')], default='none', max_length=16)),
                ('name', models.CharField(max_length=1024)),
                ('description', models.TextField(blank=True, max_length=32768, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('address', models.CharField(blank=True, max_length=8192, null=True)),
                ('href', models.URLField(blank=True, max_length=4096, null=True)),
                ('orcid', models.URLField(blank=True, max_length=4096, null=True)),
                ('added', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'cir_publisher',
            },
        ),
        migrations.CreateModel(
            name='Record',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version', models.IntegerField(default=1)),
                ('added', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'cir_record',
            },
        ),
        migrations.CreateModel(
            name='Release',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=768)),
                ('description', models.TextField(blank=True, max_length=2048, null=True)),
                ('href', models.URLField(blank=True, max_length=4096, null=True)),
                ('classification', models.CharField(blank=True, choices=[('public', 'Public'), ('private', 'Private'), ('internal', 'Internal'), ('legacy', 'Legacy')], db_column='class', max_length=32)),
                ('status', models.CharField(blank=True, choices=[('active', 'Show'), ('inactive', 'Hide')], max_length=32)),
                ('version', models.CharField(default='0', max_length=255)),
                ('released', models.DateField(blank=True, null=True, verbose_name='Date Released')),
                ('downloaded', models.DateField(blank=True, null=True, verbose_name='Date Downloaded')),
                ('added', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'cir_dataset_release',
                'ordering': ['-added'],
            },
        ),
        migrations.CreateModel(
            name='Structure',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('hashisy_key', custom.fields.CactvsHashField(unique=True)),
                ('hashisy', models.CharField(blank=True, max_length=16, null=True)),
                ('minimol', custom.fields.CactvsMinimolField()),
                ('added', models.DateTimeField(auto_now_add=True)),
                ('blocked', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Structure',
                'verbose_name_plural': 'Structures',
                'db_table': 'cir_structure',
            },
        ),
        migrations.CreateModel(
            name='StructureInChIAssociation',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('software_version', models.CharField(default='1', max_length=16)),
                ('save_opt', models.CharField(default=None, max_length=2)),
                ('added', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'cir_structure_inchi_associations',
            },
        ),
        migrations.CreateModel(
            name='StructureNameAssociation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'db_table': 'cir_structure_names',
            },
        ),
        migrations.CreateModel(
            name='URIPattern',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('uri', models.CharField(max_length=32768)),
                ('category', models.CharField(choices=[('schema', 'Schema'), ('uritemplate', 'URI Template (RFC6570)'), ('documentation', 'Documentation (HTML, PDF)')], default='uritemplate', max_length=16)),
                ('name', models.CharField(max_length=768)),
                ('description', models.TextField(blank=True, max_length=32768, null=True)),
                ('added', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'cir_dataset_uri_pattern',
                'ordering': ['-added'],
            },
        ),
        migrations.AddConstraint(
            model_name='uripattern',
            constraint=models.UniqueConstraint(fields=('uri', 'category'), name='unique_uripattern_constraint'),
        ),
        migrations.AddField(
            model_name='structurenameassociation',
            name='name',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='resolver.name'),
        ),
        migrations.AddField(
            model_name='structurenameassociation',
            name='name_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='resolver.nametype'),
        ),
        migrations.AddField(
            model_name='structurenameassociation',
            name='structure',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='resolver.structure'),
        ),
        migrations.AddField(
            model_name='structureinchiassociation',
            name='inchi',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='structures', to='resolver.inchi'),
        ),
        migrations.AddField(
            model_name='structureinchiassociation',
            name='inchitype',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='associations', to='resolver.inchitype'),
        ),
        migrations.AddField(
            model_name='structureinchiassociation',
            name='structure',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inchis', to='resolver.structure'),
        ),
        migrations.AddField(
            model_name='structure',
            name='entrypoints',
            field=models.ManyToManyField(blank=True, related_name='structures', to='resolver.entrypoint'),
        ),
        migrations.AddField(
            model_name='structure',
            name='ficts_parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='ficts_children', to='resolver.structure'),
        ),
        migrations.AddField(
            model_name='structure',
            name='ficus_parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='ficus_children', to='resolver.structure'),
        ),
        migrations.AddField(
            model_name='structure',
            name='names',
            field=models.ManyToManyField(related_name='structures', through='resolver.StructureNameAssociation', to='resolver.name'),
        ),
        migrations.AddField(
            model_name='structure',
            name='uuuuu_parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='uuuuu_children', to='resolver.structure'),
        ),
        migrations.AddField(
            model_name='release',
            name='dataset',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='releases', to='resolver.dataset'),
        ),
        migrations.AddField(
            model_name='release',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='children', to='resolver.release'),
        ),
        migrations.AddField(
            model_name='release',
            name='publisher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='releases', to='resolver.publisher'),
        ),
        migrations.AddField(
            model_name='release',
            name='record_uri_pattern',
            field=models.ManyToManyField(to='resolver.uripattern'),
        ),
        migrations.AddField(
            model_name='record',
            name='dataset',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='resolver.dataset'),
        ),
        migrations.AddField(
            model_name='record',
            name='regid',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='resolver.name'),
        ),
        migrations.AddField(
            model_name='record',
            name='release',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='resolver.release'),
        ),
        migrations.AddField(
            model_name='record',
            name='structure_file_record',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='records', to='etl.structurefilerecord'),
        ),
        migrations.AddField(
            model_name='publisher',
            name='organizations',
            field=models.ManyToManyField(blank=True, related_name='publishers', to='resolver.organization'),
        ),
        migrations.AddField(
            model_name='publisher',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='children', to='resolver.publisher'),
        ),
        migrations.AddField(
            model_name='organization',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='children', to='resolver.organization'),
        ),
        migrations.AddField(
            model_name='nametype',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='children', to='resolver.nametype'),
        ),
        migrations.AddConstraint(
            model_name='inchitype',
            constraint=models.UniqueConstraint(fields=('software_version', 'is_standard', 'newpsoff', 'donotaddh', 'snon', 'srel', 'srac', 'sucf', 'suu', 'sluud', 'recmet', 'fixedh', 'ket', 't15', 'pt_22_00', 'pt_16_00', 'pt_06_00', 'pt_39_00', 'pt_13_00', 'pt_18_00'), name='inchi_type_constraint'),
        ),
        migrations.AddField(
            model_name='inchi',
            name='entrypoints',
            field=models.ManyToManyField(blank=True, related_name='inchis', to='resolver.entrypoint'),
        ),
        migrations.AddField(
            model_name='entrypoint',
            name='parent',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='children', to='resolver.entrypoint'),
        ),
        migrations.AddField(
            model_name='entrypoint',
            name='publisher',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='entrypoints', to='resolver.publisher'),
        ),
        migrations.AddField(
            model_name='endpoint',
            name='accept_header_media_types',
            field=models.ManyToManyField(related_name='accepting_endpoints', to='resolver.mediatype'),
        ),
        migrations.AddField(
            model_name='endpoint',
            name='content_media_types',
            field=models.ManyToManyField(related_name='delivering_endpoints', to='resolver.mediatype'),
        ),
        migrations.AddField(
            model_name='endpoint',
            name='entrypoint',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='endpoints', to='resolver.entrypoint'),
        ),
        migrations.AddField(
            model_name='endpoint',
            name='request_schema_endpoint',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='schema_requesting_endpoints', to='resolver.endpoint'),
        ),
        migrations.AddField(
            model_name='endpoint',
            name='response_schema_endpoint',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='schema_responding_endpoints', to='resolver.endpoint'),
        ),
        migrations.AddField(
            model_name='dataset',
            name='context_tags',
            field=models.ManyToManyField(to='resolver.contexttag'),
        ),
        migrations.AddField(
            model_name='dataset',
            name='publisher',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='resolver.publisher'),
        ),
        migrations.AddField(
            model_name='compound',
            name='structure',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='resolver.structure'),
        ),
        migrations.AddConstraint(
            model_name='structurenameassociation',
            constraint=models.UniqueConstraint(fields=('name', 'structure', 'name_type'), name='unique_structure_names'),
        ),
        migrations.AddConstraint(
            model_name='structureinchiassociation',
            constraint=models.UniqueConstraint(fields=('structure', 'inchi', 'inchitype', 'save_opt'), name='unique_structure_inchi_association'),
        ),
        migrations.AddConstraint(
            model_name='release',
            constraint=models.UniqueConstraint(fields=('dataset', 'publisher', 'name', 'version', 'downloaded', 'released'), name='unique_dataset_release_constraint'),
        ),
        migrations.AddConstraint(
            model_name='record',
            constraint=models.UniqueConstraint(fields=('regid', 'version', 'release'), name='unique_record'),
        ),
        migrations.AddConstraint(
            model_name='publisher',
            constraint=models.UniqueConstraint(fields=('name', 'category'), name='unique_publisher_constraint'),
        ),
        migrations.AddConstraint(
            model_name='organization',
            constraint=models.UniqueConstraint(fields=('name', 'category'), name='unique_organization_constraint'),
        ),
        migrations.AddConstraint(
            model_name='inchi',
            constraint=models.UniqueConstraint(fields=('block1', 'block2', 'block3', 'version'), name='unique_inchi_constraint'),
        ),
        migrations.AddConstraint(
            model_name='entrypoint',
            constraint=models.UniqueConstraint(fields=('category', 'href'), name='unique_entrypoint_constraint'),
        ),
        migrations.AddConstraint(
            model_name='endpoint',
            constraint=models.UniqueConstraint(fields=('category', 'uri'), name='unique_endpoint_constraint'),
        ),
        migrations.AddConstraint(
            model_name='dataset',
            constraint=models.UniqueConstraint(fields=('name', 'publisher'), name='unique_dataset_constraint'),
        ),
    ]
