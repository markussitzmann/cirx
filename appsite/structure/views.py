import io
import logging
from pycactvs import Ens, Dataset

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
    host_string = request.scheme + "://" + request.get_host()
    logger.info("ENS {} COUNT {}".format(Ens.List(), Dataset.List()))
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

    if 'QUERY_STRING' in request.META:
        url_parameter_string = request.META['QUERY_STRING']
    else:
        url_parameter_string = None

    dispatcher_response: DispatcherResponse = dispatcher_data.response
    content, content_type = dispatcher_response, dispatcher_response.content_type

    if representation_type == 'twirl' or representation_type == 'chemdoodle':
        if not 'width' in parameters:
            parameters['width'] = 1000
        if not 'height' in parameters:
            parameters['height'] = 700
        if 'div_id' in parameters or 'dom_id' in parameters:
            if 'div_id' in parameters and not 'dom_id' in parameters:
                parameters['dom_id'] = parameters['div_id']
            content_type = 'text/javascript'
        else:
            content_type = 'text/html'
        context = {
            'library': representation_type,
            'string': string,
            'response': content.simple[0].content,
            'parameters': parameters,
            'url_parameter_string': url_parameter_string,
            'base_url': request.get_full_path_info(),
            'host': host_string
        }

        return render(request, 'twirl.html', context=context, content_type=content_type)

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

    if output_format == "plain":
        try:
            http_response = HttpResponse(content_type=content_type)
            http_response.write(io.BytesIO(content.simple).getvalue())
        except:
            #content_str = '\n'.join(set([str(item) for r in sorted(content.simple) for item in r.content]))
            #content_str = '\n'.join(sorted(set([str(item) for r in content.simple for item in r.content])))
            content_str = '\n'.join([str(item) for r in sorted(content.simple) for item in r.content])
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

def twirl_cache(request, string, dom_id):
    parameters = request.GET.copy()
    parameters.__setitem__('dom_id', dom_id)
    request.GET = parameters
    response = identifier(request, string, 'twirl')
    return response

