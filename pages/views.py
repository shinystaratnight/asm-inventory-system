from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django import template
from django.views.decorators.csrf import ensure_csrf_cookie


def get_base_url(request):
    return '%s://%s' %(request.scheme, request.get_host())


def index(request):
    context = {
        'base_url': get_base_url(request),
    }
    html_template = loader.get_template('login.html')
    return HttpResponse(html_template.render(context, request))


# Create your views here.
def pages(request):

    context = {
        'base_url': get_base_url(request),
    }
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:
        
        load_template = request.path.split('/')[-1]
        html_template = loader.get_template( load_template )
        return HttpResponse(html_template.render(context, request))
        
    except template.TemplateDoesNotExist:

        html_template = loader.get_template( 'error-404.html' )
        return HttpResponse(html_template.render(context, request))

    except:
    
        html_template = loader.get_template( 'error-500.html' )
        return HttpResponse(html_template.render(context, request))