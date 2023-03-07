import json

from pycactvs import Prop, Ens

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

# Create your views here.
from resolver.models import Compound


def neon(request: HttpRequest, string: str = None):
    return render(request, 'neon.html', {
        'string': string,
        'host': request.scheme + "://" + request.get_host(),
    })

def compounds(request, cid: int = None):
    return render(request, 'compound.html', {
        'string': int,
        'host': request.scheme + "://" + request.get_host(),
        'compound': Compound.objects.annotated().order_by('id').filter(id=cid, annotated_inchi_is_standard=True).first()
    })

def images(request: HttpRequest, cid: int = None, string: str = None):

    svg_paramaters = {
        'width': 264,
        'height': 264,
        'bgcolor': 'white',
        'atomcolor': 'element',
        # 'symbolfontsize': 32,
        'bonds': 10,
        'framecolor': 'transparent'
    }

    prop: Prop = Prop.Ref('E_SVG_IMAGE')
    prop.datatype = 'xmlstring'
    prop.setparameter(svg_paramaters)

    if cid or string:
        if cid:
            compound: Compound = Compound.objects.annotated().filter(id=cid).first()
            ens = compound.structure.to_ens
            image = ens.get(prop)
            return HttpResponse(image, content_type='image/svg+xml')
        else:
            image = Ens.Get(string, prop)
            return HttpResponse(image, content_type='image/svg+xml')
    else:
        params = {param: prop.getparameter(param) for param in prop.parameters}
        return HttpResponse(json.dumps(params), content_type='application/json')


def sandbox(request: HttpRequest):
    return render(request, 'sandbox.html')

