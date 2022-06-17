import logging
from collections import namedtuple

from pycactvs import Ens, Prop
from time import sleep

from celery import group
from celery.result import AsyncResult
from django.test import TestCase, SimpleTestCase
from etl.tasks import *

logger = logging.getLogger('cirx')

InChIType = namedtuple('InChIType', 'name property key version software options')


class EtlTests(TestCase):



    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_sandbox(self):
        logger.info("----- start ----")

        INCHI_TYPES = [
            InChIType(
                'standard',
                'E_STDINCHI',
                'E_STDINCHIKEY',
                Prop.Ref('E_STDINCHI').softwareversion,
                Prop.Ref('E_STDINCHI').software,
                []
            ),
            InChIType(
                'default',
                'E_INCHI',
                'E_INCHIKEY',
                Prop.Ref('E_INCHI').softwareversion,
                Prop.Ref('E_INCHIKEY').software,
                ["DONOTADDH RECMET NOWARNINGS FIXEDH"]
            ),
            InChIType(
                'x-tauto',
                'E_INCHI',
                'E_INCHIKEY',
                Prop.Ref('E_INCHI').softwareversion,
                Prop.Ref('E_INCHIKEY').software,
                ["DONOTADDH RECMET NOWARNINGS KET 15T"]
            ),
            InChIType(
                'x-tauto-x',
                'E_TAUTO_INCHI',
                'E_TAUTO_INCHIKEY',
                Prop.Ref('E_TAUTO_INCHI').softwareversion,
                Prop.Ref('E_TAUTO_INCHI').software,
                "DONOTADDH RECMET NOWARNINGS KET 15T PT_22_00 PT_16_00 PT_06_00 PT_39_00 PT_13_00 PT_18_00"
            ),
        ]

        #smiles1 = "CC(=O)CC(C)=O"
        #smiles2 = "CC(O)=CC(C)=O"

        smiles_list = [
            "OC1=NC(=N)Nc2[nH]cnc12",
            "N=C1NC(=O)C2N=CNC2=N1",
            "N=C1NC(=O)c2[nH]cnc2N1",
            "N1C(N)=NC=2N=CNC2C1=O",
            "N=C1NC(=O)C2N=CN=C2N1",
            "OC1=C2N=CN=C2NC(=N)N1",
            "N=C1NC(=O)c2nc[nH]c2N1",
            "NC1=NC(=O)c2[nH]cnc2N1",
            "Nc1nc(O)c2nc[nH]c2n1",
            "NC1=NC(=O)C2NC=NC2=N1",
            "NC1=Nc2[nH]cnc2C(=O)N1",
            "NC1=NC(=O)C2N=CNC2=N1",
            "NC1=NC(=O)c2nc[nH]c2N1",
            "NC1=NC2=NC=NC2C(=N1)O",
            "N=C1NC(=O)C2NC=NC2=N1",
            "NC1=NC2=NC=NC2C(=O)N1",
            "Nc1nc(O)c2[nH]cnc2n1",
            "NC1=NC(=O)C2N=CN=C2N1",
            "OC1=NC(=N)NC2=NC=NC12",
            "Nc1[nH]c(O)c2ncnc2n1",
            "OC1=NC(=N)N=C2N=CNC12",
            "OC1=NC(=N)Nc2nc[nH]c12",
            "Nc1[nH]c2ncnc2c(O)n1",
            "OC1=NC(=N)N=C2NC=NC12",
            "OC1=C2NC=NC2=NC(=N)N1",
            "OC1=C2N=CNC2=NC(=N)N1"
        ]

        for t in INCHI_TYPES:
            p = Prop.Ref(t.property)
            p.setparam("options", t.options)
            for smiles in smiles_list:
                e = Ens(smiles)
                #logger.info("%s : %s" % (t.property, p.getparam("options")))
                logger.info("%s : %s : %s :%s" % (e.get(t.key), t.property, e.get(t.property), t.name))








