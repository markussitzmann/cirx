from django.http import HttpRequest
from django.shortcuts import render

# Create your views here.

def neon(request: HttpRequest, string: str = None):
    return render(request, 'neon.html', {
        'string': string,
        'host': request.scheme + "://" + request.get_host(),
    })