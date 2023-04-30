import logging
import os
import sys

# Pycactvs needs that
sys.setdlopenflags(os.RTLD_GLOBAL|os.RTLD_NOW)

from pycactvs import Ens, Dataset, Molfile, Prop

names = ['ethanol', 'benzene', 'warfarin', 'guanine', 'tylenol']

Prop.Create('E_SYNONYM')


def id():
    num = 0
    while True:
        yield "TEST-" + str(num)
        num += 1


def prep_ens(id, name):
    ens = Ens(name)
    ens.set('E_MDL_NAME', id)
    ens.set('E_SYNONYM', name[::-1])
    ens.set('E_NAME', name + "\n" + name.capitalize())
    #ens.set('E_ID', regid)
    return ens


r = id()
dataset = Dataset([prep_ens(next(r), n) for n in names])
dataset.get('E_INCHI')

molfile = Molfile.Open("/home/app/test.sdf", mode="w", writelist=['E_MDL_NAME', 'E_NAME', 'E_SYNONYM'])
molfile.write(dataset)
molfile.close()



#string = str(Molfile.String(dataset).decode('utf-8'))

#print(string)



