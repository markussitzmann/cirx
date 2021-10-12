from django.shortcuts import render
from django.http import HttpResponse

from pycactvs import Ens


def resolver(request, smiles):
    e = Ens(smiles)
    context = {'hashisy': e.get("E_HASHISY")}
    #return render(request, "simple.html", context)
    return HttpResponse(e.get("E_HASHISY"))