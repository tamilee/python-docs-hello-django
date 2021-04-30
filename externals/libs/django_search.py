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
#directoryRoot = '/Users/SumeetSandhu/Documents/Climate/python/'
#sys.path = [ directoryRoot , directoryRoot+'.env/' , directoryRoot+'.env/lib/python3.8/' ,
#             directoryRoot+'.env/lib/python3.8/site-packages' ,
#             '/Users/SumeetSandhu/Documents/Patent/Code/Python/CONFIZ/Source' ] + sys.path
import spacy
nlp = spacy.load("en_trf_bertbaseuncased_lg")
vector_size = 768

import requests, io
import os
  
#csvLink = ext_libs_path + '/url_stats.csv' 
csvLink = 'https://mlws5706376320.z20.web.core.windows.net/url_stats.csv' 
r = requests.get(csvLink, allow_redirects=True)
csvfields = ['url' , 'name' , 'snippet' , 'text-length' , 'content-length' , 'hits' , 'markets' ,\
             'queries' , 'tags' , 'top-domain' , 'frags'  ]
#with open(csvLink, newline='', encoding='utf-8') as cf:
with io.StringIO(r.content.decode()) as cf:
    reader = csv.DictReader(cf)
    csvL = [ row for row in reader ]
csvD = { w['url']:w for w in csvL }
urls = [ w['url'] for w in csvL ]

import zlib
#uM = np_load(directoryRoot+'url_UNSnorm_mat.npy')
matrixLink = 'https://storage.googleapis.com/climatedatahub1/url_UNSnorm_mat_zbytes' 
matrixLink = 'https://drive.google.com/file/d/1ZoMp6v8v3_dWd47EirN_ZYch6usRA9jg/view?usp=sharing'
matrixLink = 'https://mlws5706376320.z20.web.core.windows.net/url_UNSnorm_mat_zbytes'
r = requests.get(matrixLink, allow_redirects=True)
r.raise_for_status()
uM = np_load(io.BytesIO(zlib.decompress(r.content)))


queries = [ 'energy data in US' , 'policy Canada' , 'Australian financial and insurance data' ,\
            'climate impact in Africa' , 'regenerative agriculture India' , 'green jobs' , 'Vancouver soil data' ]


def searchURLs(request, query, topN):
    nlp = spacy.load("en_trf_bertbaseuncased_lg")
    queries = [query]
    qN = len(queries)
    qdocs = list(nlp.pipe(queries))
    QM , qV = zeros((1,vector_size)) , zeros((1,vector_size))   #QUERY MATRIX
    for qd in qdocs:
        qV[0,:] = sum(qd.tensor)
        QM = np_append(QM,qV,axis=0)
    QM = QM[1:,:]

    dpM = dot( uM , kron(array(([1,1,1])),QM).T )
    topinds = np_argsort(dpM, axis=0)[-1:-topN-1:-1,:]

    resultDict = {}
    for ii in range(0,qN):
        topiq = topinds[:,ii].tolist()
        resultDict[queries[ii]] = [ dict([ ('rank',str(jj[0]+1)) ] +
                                      [ (key,csvD[urls[jj[1]]][key]) for key in [ 'url','name','snippet','tags'] ] ) for jj in enumerate(topiq) ]
    return resultDict
