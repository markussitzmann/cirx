import logging
import os
import sys

sys.setdlopenflags(os.RTLD_GLOBAL|os.RTLD_NOW)

from pycactvs import Molfile, Ens

logging.basicConfig(level=logging.INFO)

origin = Molfile.Open("/home/app/error.2.sdf")
origin_ens = origin.read()

minimol = origin_ens.get("E_MINIMOL")
minimol_ens = Ens(minimol)

smiles_ens = Ens(origin_ens.get("E_SMILES"))

for title, ens in [("MOLFILE", origin_ens), ("MINIMOL", minimol_ens), ("SMILES", smiles_ens)]:

    logging.info("---- \\ {} \\----".format(title, ))

    logging.info("ORIGIN {} {}".format(ens.new("E_HASHISY"), ens.get("E_SMILES")))

    ens_addh = ens.dup()
    ens_addh.hadd()
    ficts_parent = ens_addh.get("E_FICTS_STRUCTURE")
    ficus_parent = ens_addh.get("E_FICUS_STRUCTURE")

    logging.info("HADD   {} {} {}".format(ens_addh.new("E_HASHISY"), ens_addh.get("E_FORMULA"), ens_addh.get("E_SMILES")))
    logging.info("FICTS  {} {} {}".format(ficts_parent.new("E_HASHISY"), ficts_parent.get("E_FORMULA"), ficts_parent.get("E_SMILES")))
    logging.info("FICUS  {} {} {}".format(ficus_parent.new("E_HASHISY"), ficus_parent.get("E_FORMULA"), ficus_parent.get("E_SMILES")))















