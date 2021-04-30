from django.shortcuts import render

from django.http import HttpResponse
from django.template import loader, RequestContext
#from django_search import searchURLs
from Searcher import Searcher
import subprocess


def index(request):
    #context = {'result_list' : ['result 1', 'result 2', 'result 3'] , 'query' : 'climate related websites'}
    context = {}

    template = loader.get_template('mvp1/index.html')
    requestContext = RequestContext(request, context)
    return  HttpResponse(template.template.render(requestContext))

def search(request):
    #query = request.POST['query']
    query = request.POST.get('query')

    if (query):
        searcher = Searcher()
        resultDict = searcher.searchURLs(request, query, 50)
    else:
        resultDict = {' ':[]}
        query = ' '
    
    context = {'result_list' : resultDict.get(query) , 'query' : query }
    template = loader.get_template("mvp1/results.html") 
    requestContext = RequestContext(request, context)
    return HttpResponse(template.template.render(requestContext))
    #return render(request, 'mvp1/results.html', context)

def spacy_init(request):
    out_html = "<html><body><h1>spaCy download en_trf_bertbaseuncased_lg output:</h1><p>"
    output = subprocess.check_output("python -m spacy download en_trf_bertbaseuncased_lg", stderr=subprocess.STDOUT, shell=True)
    out_html += output.decode("UTF-8")
    out_html += "</p></body></html>"
    return HttpResponse(out_html)  
