#! C:\python3.8.3
##
## MODULE main
##
## Sumeet Sandhu
## Copyright (C) 2020- Elementary IP LLC
#############################################

import sys
import csv , numpy
import numpy
from numpy import array, dot, zeros, kron, load as np_load, argsort as np_argsort, append as np_append
directoryRoot = '/home/tami/DJANGO/climatesite/OUTPUT/'

import spacy
nlp = spacy.load("en_trf_bertbaseuncased_lg")
vector_size = 768

def urls2html(resultD,directoryOut):
    ##FUNCTION: wrap search results in html for display
    query = list(resultD)[0]
    htmldiv = '<div style="font-family:open-sans,sans-serif;font-size:16px;overflow-x:auto;padding-right:10px; padding-left:10px;width:90%;">\n'
    html = '<h3>About</h3>\n'
    html += '<dl><dt>We are building <a href=https://www.climatedatahub.io>ClimateDataHub</a> - a place to easily discover, upload, curate, enrich, create and download climate datasets.</dt>' +\
            '<dd><a href=http://data.protea.earth>Sign up</a> to try our beta or help out.</dd>'+\
            '<dt>Tell us what data you\'d like to see:</dt>'+\
            '<dd>Energy ; Food & Water ; Infrastructure & Transportation ; Risk & Resilience ; Nature Conservation ; Policy ; Health ; Finance & Investment ; Commerce & Manufacturing ; Other.</dd></dl>'
    html += '<h3>AI based semantic search</h3>'+\
            '<dl><dt>You can search for climate data in ~9000 urls by querying with text or url (AI based semantic search):</dt>' +\
            '<dd>e.g. <i>"energy data in US" , "https://en.wikipedia.org/wiki/Climate_of_Dhaka" , "green jobs" ,' +\
            '"regenerative agriculture in India" , "satellite data Amazon rainforest"</i></dd>'+\
            '<dt><form><label for="fname"><b>Enter Query</b></label></dt>'+\
            '<dd><input type="text" id="query" name="query"></form></dd></dl>'
    html += '<h4>Search Results for query = "' + query +  '"</h4>\n'
    tbl = '<table style="font-family:open-sans,sans-serif;font-size:14px;">\n'
    for r in resultD[query]:
        tbl += '<tr style="font-weight:bold;padding-right:20px; padding-left:20px;">' +\
               '<td>'+r['rank']+'</td><td><a href="'+r['url']+u'">'+r['url']+'</a></td></tr>\n'
               #+ '<div class="box"><iframe src='+r['url']+' title='+r['name']+' width="70%" height="500" style="border:none;"></iframe></div></td></tr>\n'
        tbl += '<tr style="padding-right:20px; padding-left:20px;">' +\
               '<td></td><td><small>'+r['snippet'][:500]+'</small></td></tr>\n'
    htmldiv = htmldiv + html + tbl + '</table></div>'
    htmlout = '<!DOCTYPE html>\
    <html lang="en">\n\
    <head>\n\
    <title>Search Results</title>\n\
    <style>\
    input{width: 100%;}\
    .box{display: none; width: 100%;}\
    a:hover + .box, .box:hover{display: block; position: relative; z-index: 100;}\
    </style>\
    </head>\n\
    <body>\n' + htmldiv + '\n</body>\n</html>'
    open( directoryOut + query + '_searchResults.html' ,'w').write(htmlout)

if 1==1:
    import requests, io
    import json
    csvLink = 'https://storage.googleapis.com/climatedatahub1/url_stats.csv' 
    r = requests.get(csvLink, allow_redirects=True)
    csvfields = ['url' , 'name' , 'snippet' , 'text-length' , 'content-length' , 'hits' , 'markets' ,\
                 'queries' , 'tags' , 'top-domain' , 'frags'  ]
    #with open(directoryRoot+'url_stats.csv', newline='', encoding='utf-8') as cf:
    with io.StringIO(r.content.decode()) as cf:
        reader = csv.DictReader(cf)
        csvL = [ row for row in reader ]
    csvD = { w['url']:w for w in csvL }
    urls = [ w['url'] for w in csvL ]

    import zlib
    #uM = np_load(directoryRoot+'url_UNSnorm_mat.npy')
    matrixLink = 'https://storage.googleapis.com/climatedatahub1/url_UNSnorm_mat_zbytes' 
    r = requests.get(matrixLink, allow_redirects=True)
    r.raise_for_status()
    uM = np_load(io.BytesIO(zlib.decompress(r.content)))

if 1==1:
    queries = [ 'energy data in US' , 'policy Canada' , 'Australian financial and insurance data' ,\
                'climate impact in Africa' , 'regenerative agriculture India' , 'green jobs' , 'Vancouver soil data' ]
    queries = queries[0:1]
    qN = len(queries)
    qdocs = list(nlp.pipe(queries))
    QM , qV = zeros((1,vector_size)) , zeros((1,vector_size))   #QUERY MATRIX
    for qd in qdocs:
        qV[0,:] = sum(qd.tensor)
        QM = np_append(QM,qV,axis=0)
    QM = QM[1:,:]

    topN = 5    #NUMBER OF TOP MATCHES
    dpM = dot( uM , kron(array(([1,1,1])),QM).T )
    topinds = np_argsort(dpM, axis=0)[-1:-topN-1:-1,:]
    resultD = {}
    for ii in range(0,qN):
        topiq = topinds[:,ii].tolist()
        resultD[queries[ii]] = [ dict([ ('rank',str(jj[0]+1)) ] +
                                      [ (key,csvD[urls[jj[1]]][key]) for key in [ 'url','name','snippet','tags'] ] ) for jj in enumerate(topiq) ]
    import json
    with open(directoryRoot + 'result.json', 'w') as fp:
        json.dump(resultD, fp)
    urls2html(resultD,directoryRoot)
    
