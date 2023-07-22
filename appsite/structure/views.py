import io
import logging

from django.conf import settings
from django.http import *
from django.shortcuts import render, redirect

from structure.dispatcher import Dispatcher, DispatcherData, DispatcherResponse
from structure.forms import *

logger = logging.getLogger('cirx')


def identifier(request, string, representation, operator=None, format='plain'):
    return resolve_to_response(request, string, representation, operator=operator, output_format=format)


def structure(request, string=None):

    host_string = request.scheme + "://" + request.get_host()
    base_url = request.path_info

    query = request.GET.copy()
    if 'string' in query and 'representation' in query:
        return identifier(
            request,
            query['string'],
            query['representation'],
            operator=query.get('operator', None),
            format=query.get('protocol', 'plain')
        )
    if request.method == 'POST':
        form = ResolverInput(request.POST)
        if form.is_valid():
            redirectedURL = '%s/%s/%s' % (
                base_url,
                form.cleaned_data['identifier'],
                form.cleaned_data['representation']
            )
            return HttpResponseRedirect(redirectedURL)
    else:
        return redirect('cir', permanent=True)
    #    if string:
    #        form = ResolverInput({'identifier': string, 'representation': 'stdinchikey'})
    #    else:
    #        form = ResolverInput()
    #return render(request, 'resolver.html', {
    #    'form': form,
    #    'base_url': base_url,
    #    'host': host_string,
    #})


def resolve_to_response(request, string: str, representation_type: str, operator=None, output_format="plain"):
    parameters = request.GET.copy()
    if 'operator' in parameters:
        operator = parameters['operator']
    if operator:
        string = "%s:%s" % (operator, string)

    dispatcher: Dispatcher = Dispatcher(
        request=request,
        representation_type=representation_type,
        output_format=output_format
    )
    dispatcher_data: DispatcherData = dispatcher.parse(string)

    if request.is_secure():
        host_string = 'https://' + request.get_host()
    else:
        host_string = 'http://' + request.get_host()
    if 'QUERY_STRING' in request.META:
        url_parameter_string = request.META['QUERY_STRING']
    else:
        url_parameter_string = None

    if representation_type == 'twirl' or representation_type == 'chemdoodle':
        if not parameters.has_key('width'):
            parameters['width'] = 1000
        if not parameters.has_key('height'):
            parameters['height'] = 700
        if parameters.has_key('div_id') or parameters.has_key('dom_id'):
            if parameters.has_key('div_id') and not parameters.has_key('dom_id'):
                parameters['dom_id'] = parameters['div_id']
            content_type = 'text/javascript'
        else:
            content_type = 'text/html'
        return render(
            request, '3d.template', {
                'library': representation_type,
                'string': string,
                'dispatcher_response': dispatcher.response_list,
                'parameters': parameters,
                'url_parameter_string': url_parameter_string,
                'base_url': settings.STRUCTURE_BASE_URL,
                'host': host_string
            }, content_type=content_type)

    if representation_type == "image":
        output_format = "image"

    if not dispatcher_data:
        if output_format == "xml":
            return render(request, 'structure.xml', {
                'dispatcher_response': [],
                'string': dispatcher_data.identifier,
                'representation': representation_type,
                # 'base_url': settings.STRUCTURE_BASE_URL,
                'base_url': request.get_full_path_info(),
                'host': host_string
            }, content_type="text/xml")
        else:
            raise Http404

    dispatcher_response: DispatcherResponse = dispatcher_data.response

    content, content_type = dispatcher_response, dispatcher_response.content_type
    if output_format == "plain":
        try:
            http_response = HttpResponse(content_type=content_type)
            http_response.write(io.BytesIO(content.simple).getvalue())
        except:
            content_str = '\n'.join(set([str(item) for r in sorted(content.simple) for item in r.content]))
            http_response = HttpResponse(content_str, content_type=content_type)
        http_response["Access-Control-Allow-Origin"] = "*"
        http_response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        http_response["Access-Control-Max-Age"] = "1000"
        http_response["Access-Control-Allow-Headers"] = "X-Requested-With, Content-Type"
        return http_response
    elif output_format == "image":
        http_response = HttpResponse(content.simple[0].content, content_type=content_type)
        return http_response
    elif output_format == "xml":
        return render(request, "structure.xml", {
            'response': dispatcher_response.full,
            'string': dispatcher_data.identifier,
            'representation': representation_type,
            'base_url': request.get_full_path_info(),
            'host': host_string
        }, content_type="text/xml")

#
# # print " 1 jeff /www/django/chemical/structure/views.py"
#
# if not settings.TEST:
#     if settings.JAVA:
#         from jpype import JPackage, attachThreadToJVM, isThreadAttachedToJVM
#
#         if not isThreadAttachedToJVM():
#             attachThreadToJVM()
#         opsin_package = JPackage("uk").ac.cam.ch.wwmm.opsin
#         Opsin = opsin_package.NameToStructure.getInstance()
#         OpsinConfig = opsin_package.NameToStructureConfig()
#
#
# def twirl_cache(request, string, dom_id):
#     parameters = request.GET.copy()
#     parameters.__setitem__('dom_id', dom_id)
#     request.GET = parameters
#     response = identifier(request, string, 'twirl')
#     return response
#
#
# def chemdoodle_cache(request, string, dom_id):
#     parameters = request.GET.copy()
#     parameters.__setitem__('dom_id', dom_id)
#     request.GET = parameters
#     response = identifier(request, string, 'chemdoodle')
#     return response
#
#


#
#
# def opsin_resolver(request, name):
#     #	print " 3 jeff /www/django/chemical/structure/views.py"
#     try:
#         opsin_result = Opsin.parseChemicalName(name, OpsinConfig)
#     except:
#         raise Http404
#     smiles = opsin_result.getSmiles()
#     if not smiles:
#         raise Http404
#     return HttpResponse(smiles, mimetype='text/plain')
#
#


#
# #	print " 4.10 jeff /www/django/chemical/structure/views.py"
#
# # def editor(request):
# # form = ChemicalResolverInput()
# # form.editor_button = 'editor-button'
# # form.structure_input_field = 'id_identifier'
# # return render_to_response('editor_test.template', {
# # 'form': form,
# # 'base_url': settings.STRUCTURE_BASE_URL,
# # 'host': host_string,
# # })
#
#
# def structure_documentation(request, dummy=None, string=None):
#     return render_to_response('structure_documentation.template')
#
#
# #######
#

#
# def structureImage(ensemble, height=240, width=280, fontsize=10, linewidth=1, MIN_WIDTH=240, MAX_WIDTH=280):
#     # pdb.set_trace()
#     if str(width) == "auto":
#         # try:
#         smiles_length = len(ensemble['smiles'])
#         ring_atoms_cmd = 'ens atoms %s ringatom count' % ensemble.cs_handle
#         ring_atom_count = int(ensemble.cs_client_object.cmd(ring_atoms_cmd))
#         width = (smiles_length * 15) - (15 * ring_atom_count)
#     # except:
#     #	width = MAX_WIDTH
#     if width <= MIN_WIDTH: width = MIN_WIDTH
#     if width >= MAX_WIDTH: width = MAX_WIDTH
#
#     hashisy = ensemble['hashisy']
#     filename = os.path.join("tmp", "structure_%s_%s_%s_%s_%s_%s_%s.gif" % (
#         hashisy, height, width, fontsize, linewidth, MIN_WIDTH, MAX_WIDTH))
#
#     image = ensemble.get_image(
#         www_media_path=settings.MEDIA_ROOT,
#         filename=filename,
#         parameters={'height': height, 'width': width, 'symbolfontsize': fontsize, 'linewidth': linewidth}
#     )
#
#     # fname = os.path.join("tmp", "structure_%s_%s_%s_%s_%s_%s_%s.gif" % (hashisy,height,width,fontsize,linewidth,MIN_WIDTH,MAX_WIDTH))
#     # imageFileName = os.path.join(settings.MEDIA_ROOT, fname)
#     # f = open(imageFileName, 'w')
#     # imageFile = File(f)
#     # imageFile.write(image.image)
#     # imageFile.close()
#     # imageFile.url = os.path.join(settings.MEDIA_URL, image.filename[1:])
#     image.url = os.path.join(settings.MEDIA_URL, filename)
#     image.height = height
#     image.width = width
#     image.fontsize = fontsize
#     image.linewidth = linewidth
#
#     return image
