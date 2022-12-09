import logging
from collections import defaultdict
from unittest import skip

from django.conf import settings
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import F
from django.db import connection
from django.test import TestCase

from etl.models import StructureFile, StructureFileRecordNameAssociation
from resolver.models import InChI, Structure, StructureInChIAssociation, Name, StructureNameAssociation, \
    Compound, StructureParentStructure

logger = logging.getLogger('cirx')

FIXTURES = ['mini.json']

settings.DEBUG = True


class ResolverModelTests(TestCase):
    fixtures = FIXTURES

    def setUp(self):
        pass

    def tearDown(self):
        pass

        # name_association_objects = StructureNameAssociation.objects.all()
        # for a in name_association_objects:
        #     logger.info("Associations %s" % a)
        #     if a.structure.parents:
        #         logger.info("Parents      %s" % a.structure.parents)
        #     else:
        #         logger.info("SMILES       %s" % a.structure)
        #
        #
        # structures = Structure.objects.count()
        # logger.info("Structure count %s" % structures)
        #
        # inchis = InChI.objects.count()
        # logger.info("InChI count %s" % inchis)
        #
        # inchi_associations = StructureInChIAssociation.objects.count()
        # logger.info("InChI association %s" % inchi_associations)
        #
        # names = Name.objects.count()
        # logger.info("Names %s" % names)
        #
        # compounds = Compound.objects.count()
        # logger.info("Compound %s" % compounds)

        ####
        # for structure in Structure.objects.all():
        #     names = structure.structurenameassociation_set.all()
        #     logger.info("-- Structure: %s" % (structure))
        #     try:
        #         logger.info("     ->: %s" % structure.parents if structure.parents else None)
        #     except:
        #         logger.info("     ->: None")
        #     if len(names):
        #         for name in names:
        #             logger.info("      affinity: %s -> name: %s | %s : %s" % (name.affinity_class, name.name_id, name.name_type_id, name.name.name))
        #     else:
        #         logger.info("     ->: None")

        # name_association_count = StructureNameAssociation.objects.count()
        # logger.info("Count --> %s", name_association_count)
        #
        # name_association_objects = StructureNameAssociation.objects.all()
        # for a in name_association_objects:
        #     logger.info("%s %s %s %s" % (a.name_type_id, a.affinity_class, a.structure, a.name))



    @skip
    def test_structure_name(self):

        logger.info("--------- Structure Name ----------")

        structures = Structure.objects.all()
        for structure in structures:
            logger.info("--------- %s ---------" % structure.id)
            logger.info(structure.structure_file_records.all())
            logger.info(structure.smiles)
            try:
                logger.info(structure.parents)
                logger.info("P FICTS %s FICuS %s uuuuu %s" % (
                    structure.parents.ficts_parent.id if structure.parents.ficts_parent else "-",
                    structure.parents.ficus_parent.id if structure.parents.ficus_parent else "-",
                    structure.parents.uuuuu_parent.id if structure.parents.uuuuu_parent else "-",
                ))
                logger.info("C FICTS %s FICuS %s uuuuu %s" % (
                    structure.parents.ficts_parent.ficts_children.all() if structure.parents.ficts_parent.ficts_children else "-",
                    structure.parents.ficus_parent.ficus_children.all() if structure.parents.ficus_parent.ficts_children else "-",
                    structure.parents.uuuuu_parent.uuuuu_children.all() if structure.parents.uuuuu_parent.uuuuu_children else "-",
                ))
            except Structure.parents.RelatedObjectDoesNotExist:
                logger.info("NO PARENT")

    @skip
    def test_query(self):

        q = Structure.objects\
            .prefetch_related('parents', 'structure_file_records', 'structure_file_records__names') \
            .annotate(
                ficts=F('parents__ficts_parent'),
                ficus=F('parents__ficus_parent'),
            )\
            .annotate(
                tnames=ArrayAgg('structure_file_records__structure_file_record_name_associations')
            )
        logger.info("QUERY %s" % q.query)
        r = q.in_bulk([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 70, 1493])

        logger.info("Q >>> %s" % r[4].ficts)
        logger.info("N >>> %s" % r[4].tnames)

        for qq in r.values():
            logger.info("QQ >>> %s" % qq)
            for n in qq.tnames:
                logger.info("NN >>> %s" % type(n))

    @skip
    def test_name_association(self):

        #flist = StructureFile.objects.all()

        flist = [1,]

        #logger.info("F %s", [f.id for f in flist])

        p = StructureParentStructure.objects\
            .select_related('structure', 'structure__structure_file_source')
        d = defaultdict(list)
        for f in flist:
            r = p.filter(structure__structure_file_source__structure_file=f)
            #l = [(s.ficts_parent_id, s.structure_id) for s in r.all() if s.ficts_parent_id]
            for s in r.all():
                if not s.ficts_parent_id: continue
                d[s.ficts_parent_id].append(s.structure_id)

            #logger.info("F C %s %s P %s", r.count(), len(l), l)

        sid_list = []
        for k in [*d]:
            if k in d[k]:
                logger.info("--> %s : %s" % (k, d[k]))
                sid_list.extend(d[k])

        sids = sorted(list(set(sid_list)))
        logger.info("--> %s", sids)

        q = Structure.objects \
            .prefetch_related('parents', 'structure_file_records', 'structure_file_records__names')\
            .annotate(
                tnames=ArrayAgg('structure_file_records__structure_file_record_name_associations')
            )
        logger.info("QUERY %s" % q.query)

        r = q.in_bulk(sids)
        a_list = []
        for k, s in r.items():
            #logger.info("--- S %s %s" % (s, s.tnames))
            for n in s.tnames:
                if n:
                    #logger.info("--- N %s" % n)
                    ra = StructureFileRecordNameAssociation.objects.get(id=n)
                    #logger.info("    N %s" % ra)

                    a_list.append(StructureNameAssociation(
                        name=ra.name,
                        structure_id=s.id,
                        name_type=ra.name_type,
                        affinity_class="exact",
                        confidence=99
                    ))

        StructureNameAssociation.objects.bulk_create(
            a_list,
            batch_size=100,
            ignore_conflicts=True
        )



    def test_name_association2(self):

        logger.info("COUNT0 %s" % len(connection.queries))

        #flist = StructureFile.objects.all()

        flist = [1,]

        #logger.info("F %s", [f.id for f in flist])

        query = Structure.objects\
            .select_related('parents', 'structure_file_source')\
            .annotate(
                record_names=ArrayAgg('structure_file_records__structure_file_record_name_associations'),
                ficts=F('parents__ficts_parent'),
                ficus=F('parents__ficus_parent'),
                uuuuu=F('parents__uuuuu_parent'),
            )
            #.filter(structure_file_source__structure_file=3)

        structures = query.all()

        structure_association_list = []
        for structure in structures:
            record_names = structure.record_names
            structure_association_list.extend(record_names)

        logger.info(print(len(structure_association_list)))
        file_record_associations = StructureFileRecordNameAssociation.objects\
            .in_bulk(structure_association_list, field_name='id')

        logger.info("COUNTX %s" % len(connection.queries))

        structure_association_list = []
        logger.info("S %s" % len(structures))

        for structure in structures:
            record_names = structure.record_names

            for record_name in record_names:
                if not record_name: continue
                record_name_association = file_record_associations[record_name]
                if structure.ficts:
                    structure_association_list.append(StructureNameAssociation(
                        name_id=record_name_association.name_id,
                        structure_id=structure.ficts,
                        name_type_id=record_name_association.name_type_id,
                        affinity_class="exact",
                        confidence=100
                    ))
                if structure.ficus and not structure.ficus == structure.ficts:
                    structure_association_list.append(StructureNameAssociation(
                        name_id=record_name_association.name_id,
                        structure_id=structure.ficus,
                        name_type_id=record_name_association.name_type_id,
                        affinity_class="narrow",
                        confidence=100
                    ))
                if structure.uuuuu and not structure.uuuuu == structure.ficus and not structure.uuuuu == structure.ficts:
                    structure_association_list.append(StructureNameAssociation(
                        name_id=record_name_association.name_id,
                        structure_id=structure.uuuuu,
                        name_type_id=record_name_association.name_type_id,
                        affinity_class="broad",
                        confidence=100
                    ))

        StructureNameAssociation.objects.bulk_create(
            structure_association_list,
            batch_size=1000,
            ignore_conflicts=True
        )

        logger.info(len(structure_association_list))
        logger.info("COUNT1 %s" % len(connection.queries))

