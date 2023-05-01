import logging
import os
import sys

# Pycactvs needs that
sys.setdlopenflags(os.RTLD_GLOBAL|os.RTLD_NOW)

from pycactvs import Ens, Dataset, Molfile, Prop

names = ['ethanol', 'benzene', 'warfarin', 'guanine', 'tylenol', 'restasis', 'acetic anhydride', 'glucose']

Prop.Create('E_SYNONYM')
Prop.Create('E_ID')
Prop.Create('E_NSC_NUMBER')
#Prop.Create('E_ZINC_ID')


def id():
    num = 0
    while True:
        yield "TEST-" + str(num)
        num += 1

def nsc_id():
    num = 0
    while True:
        yield "NSC-" + str(num)
        num += 1

def zinc_id():
    num = 0
    while True:
        yield "ZINC-" + str(num)
        num += 1


def prep_ens(id, nsc_id, zinc_id, name):
    ens = Ens(name)
    ens.set('E_ID', id)
    ens.set('E_NSC_NUMBER', nsc_id)
    ens.set('E_ZINC_ID', zinc_id)
    ens.set('E_NAME', name)
    ens.set('E_SYNONYM', name[::-1] + "\n" + name.capitalize())
    #ens.set('E_MDL_NAME', id)


    #ens.set('E_ID', regid)
    return ens


r = id()
z = zinc_id()
n = nsc_id()
dataset = Dataset([prep_ens(next(r), next(n), next(z), name) for name in names])
dataset.get('E_INCHI')

molfile = Molfile.Open("/home/app/test.sdf", mode="w", writelist=['E_ID', 'E_NAME', 'E_SYNONYM', 'E_ZINC_ID', 'E_NSC_NUMBER'])
molfile.write(dataset)
molfile.close()



#string = str(Molfile.String(dataset).decode('utf-8'))

#print(string)



