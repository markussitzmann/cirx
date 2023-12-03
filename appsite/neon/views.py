import json
from collections import namedtuple, defaultdict

from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from pycactvs import Prop, Ens

from core.common import NCICADD_TYPES
from resolver.models import Compound, StructureNameAssociation, StructureInChIAssociation, Record, \
    StructureParentStructure, Structure
from structure.forms import ResolverInput
# Create your views here.
from structure.ncicadd.identifier import Identifier

ParentData = namedtuple('ParentData', 'structure identifier children_count is_parent')

def _prepare_parent_data_for_structure(structure: Structure, ncicadd_key_types=None):
    if ncicadd_key_types is None:
        ncicadd_key_types = ['FICTS', 'FICuS', 'uuuuu']
    parents = {}
    for parent_type in NCICADD_TYPES:
        parents[parent_type.public_string] = ParentData(
            structure=getattr(structure.parents, parent_type.attr),
            identifier=Identifier(hashcode=p.hash.padded, identifier_type=parent_type.public_string)
            if (p := getattr(structure.parents, parent_type.attr)) else None,
            #children_count=getattr(compound, parent_type.key + '_children_count'),
            children_count=0,
            is_parent=structure.hash == p.hash
            if (p := getattr(structure.parents, parent_type.attr)) else False
        )

    return {key: parents[key] for key in ncicadd_key_types}



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

def records(request, rid: int = None):
    record: Record = Record.with_related_objects.by_record_ids([rid, ]).first()

    return render(request, 'record.html', {
        'id': int,
        'host': request.scheme + "://" + request.get_host(),
        'record': record,
        'source': record.structure_file_record.source.decode("UTF-8"),
        'parents': _prepare_parent_data_for_structure(record.structure_file_record.structure)

    })


def compounds(request, cid: int = None):
    compound: Compound = Compound.with_related_objects.by_compound_ids([cid, ]).first()
    
    name_association_affinity_dict = defaultdict(list)
    _ = {
        n.affinity_class: name_association_affinity_dict[n.affinity_class.title].append(n)
        for n in StructureNameAssociation.with_related_objects
            .by_compound(compounds=[compound, ], )
            .order_by('name__name').all()
    }

    inchi_associations = {
        a.inchi_type.title: a
        for a in StructureInChIAssociation.with_related_objects.by_compound(compounds=[compound, ]).all()
    }

    name_affinities = ['exact', 'narrow', 'broad', 'generic']
    #identifier_keys = ['FICTS', 'FICuS', 'uuuuu']
    inchi_types = ['standard', 'original', 'xtauto', 'xtautox']

    return render(request, 'compound.html', {
        'id': int,
        'host': request.scheme + "://" + request.get_host(),
        'compound': compound,
        #'parents': {key: parents[key] for key in identifier_keys},
        'parents': _prepare_parent_data_for_structure(compound.structure),
        'names': {key: name_association_affinity_dict[key] for key in name_affinities},
        'inchis': {t: inchi_associations[t] for t in inchi_types if t in inchi_associations},
        'formula': compound.structure.to_ens.get('E_FORMULA'),
        'weight': compound.structure.to_ens.get('E_WEIGHT')
    })


def compound_images(request: HttpRequest, cid: int = None, string: str = None):
    if cid or string:
        if cid:
            return HttpResponseRedirect("/chemical/structure/NCICADD:CID=" + str(cid) + "/image")
        else:
            ens = Ens(string)
            image = _create_image(ens)
            return HttpResponse(image, content_type='image/svg+xml')
    else:
        prop: Prop = Prop.Ref('E_SVG_IMAGE')
        params = {param: prop.getparameter(param) for param in prop.parameters}
        return HttpResponse(json.dumps(params), content_type='application/json')

def record_images(request: HttpRequest, rid: int = None, string: str = None):
    if rid or string:
        if rid:
            return HttpResponseRedirect("/chemical/structure/NCICADD:RID=" + str(rid) + "/image")
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
