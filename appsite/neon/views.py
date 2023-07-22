import json
from collections import namedtuple, defaultdict

from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from pycactvs import Prop, Ens
from pycactvs import Dataset as CsDataset

from etl.registration import StructureRegistry
from structure.forms import ResolverInput
from resolver.models import Compound, StructureNameAssociation, StructureInChIAssociation, Dataset
# Create your views here.
from structure.ncicadd.identifier import Identifier

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
    for item in default_svg_paramaters.items():
        prop.setparameter({item[0]: item[1]})

    prop.datatype = 'xmlstring'

    return ens.get(prop)


def neon(request: HttpRequest, string: str = None):
    return render(request, 'neon.html', {
        'form': ResolverInput(),
        'string': string,
        'host': request.scheme + "://" + request.get_host(),
    })


def cir(request: HttpRequest):
    return render(request, 'cir.html', {
        'form': ResolverInput(),
        'host': request.scheme + "://" + request.get_host(),
    })


def compounds(request, cid: int = None):

    compound: Compound = Compound.with_related_objects.by_compound_ids([cid, ]).first()
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

    name_association_affinity_dict = defaultdict(list)
    name_associations = {
        n.affinity_class: name_association_affinity_dict[n.affinity_class.title].append(n)
        for n in StructureNameAssociation.with_related_objects
            .by_compound(compounds=[compound, ], )
            .order_by('name__name').all()
    }

    inchi_associations = {
        a.inchi_type.title: a
        for a in StructureInChIAssociation.with_related_objects
            .by_compound(compounds=[compound, ]).all()
    }

    name_affinities = ['exact', 'narrow', 'broad', 'generic']
    identifier_keys = ['FICTS', 'FICuS', 'uuuuu']
    inchi_types = ['standard', 'original', 'xtauto', 'xtautox']

    return render(request, 'compound.html', {
        'string': int,
        'host': request.scheme + "://" + request.get_host(),
        'compound': compound,
        'parents': {key: parents[key] for key in identifier_keys},
        'names': {key: name_association_affinity_dict[key] for key in name_affinities},
        'inchis': {t: inchi_associations[t] for t in inchi_types},
        'formula': compound.structure.to_ens.get('E_FORMULA'),
        'weight': compound.structure.to_ens.get('E_WEIGHT')
    })


def images(request: HttpRequest, cid: int = None, string: str = None):

    if cid or string:
        if cid:
            #compound: Compound = Compound.objects.filter(id=cid).first()
            #ens = compound.structure.to_ens
            #image = _create_image(compound.structure.to_ens)
            #return HttpResponse(image, content_type='image/svg+xml')
            return HttpResponseRedirect("/chemical/structure/NCICADD:CID=" + str(cid) + "/image")
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

def cover(request: HttpRequest):
    return render(request, 'cover.html')
