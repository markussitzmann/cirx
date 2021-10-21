from pycactvs import Ens

names = ['ethanol', 'benzene', 'warfarin', 'guanine', 'tylenol']

smiles = [Ens(n).get('E_SMILES') for n in names]

print("smiles")



