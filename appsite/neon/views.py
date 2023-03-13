import json
from collections import namedtuple
from typing import NamedTuple

from django.db.models import Q
from pycactvs import Prop, Ens

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

# Create your views here.
from structure.ncicadd.identifier import Identifier
from etl.registration import StructureRegistry
from resolver.models import Compound, StructureNameAssociation

ParentData = namedtuple('ParentData', 'structure identifier children_count is_parent')


def _create_image(ens: Ens, svg_paramaters = None):

    default_svg_paramaters = {
        'width': 250,
        'height': 250,
        'bgcolor': 'white',
        'atomcolor': 'element',
        # 'symbolfontsize': 32,
        'bonds': 10,
        'framecolor': 'transparent'
    }
    if svg_paramaters:
        default_svg_paramaters.update(svg_paramaters)

    prop: Prop = Prop.Ref('E_SVG_IMAGE')
    prop.datatype = 'xmlstring'
    prop.setparameter(default_svg_paramaters)

    return ens.get(prop)


def neon(request: HttpRequest, string: str = None):
    return render(request, 'neon.html', {
        'string': string,
        'host': request.scheme + "://" + request.get_host(),
    })

def compounds(request, cid: int = None):

    compound: Compound = Compound.structures.by_compound_ids([cid, ]).first()

    parents = {}
    for parent_type in StructureRegistry.NCICADD_TYPES:
        parents[parent_type.public_string] = ParentData(
            structure=getattr(compound.structure.parents, parent_type.attr),
            identifier=Identifier(hashcode=p.hashisy_key.padded, identifier_type=parent_type.public_string)
                            if (p := getattr(compound.structure.parents, parent_type.attr)) else None,
            children_count=getattr(compound, parent_type.key + '_children_count'),
            is_parent=compound.structure.hashisy_key == p.hashisy_key
                            if (p := getattr(compound.structure.parents, parent_type.attr)) else False
        )

    name_associations = StructureNameAssociation.names.by_compounds_and_affinity_classes(
        compounds=[compound, ],
    ).order_by('affinity_class', 'name__name').all()

    identifier_keys = ['FICTS', 'FICuS', 'uuuuu']

    return render(request, 'compound.html', {
        'string': int,
        'host': request.scheme + "://" + request.get_host(),
        'compound': compound,
        'parents': {key: parents[key] for key in identifier_keys},
        'names': name_associations,
    })

def images(request: HttpRequest, cid: int = None, string: str = None):

    if cid or string:
        if cid:
            compound: Compound = Compound.objects.annotated().filter(id=cid).first()
            #ens = compound.structure.to_ens
            image = _create_image(compound.structure.to_ens)
            return HttpResponse(image, content_type='image/svg+xml')
        else:
            ens = Ens(string)
            image = _create_image(ens)
            return HttpResponse(image, content_type='image/svg+xml')
    else:
        prop: Prop = Prop.Ref('E_SVG_IMAGE')
        params = {param: prop.getparameter(param) for param in prop.parameters}
        return HttpResponse(json.dumps(params), content_type='application/json')


def sandbox(request: HttpRequest):
    return render(request, 'sandbox.html')

