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
directoryRoot = '/Users/SumeetSandhu/Documents/Climate/python/'
sys.path = [ directoryRoot , directoryRoot+'.env/' , directoryRoot+'.env/lib/python3.8/' ,
             directoryRoot+'.env/lib/python3.8/site-packages' ,
             '/Users/SumeetSandhu/Documents/Patent/Code/Python/CONFIZ/Source' ] + sys.path
import spacy
nlp = spacy.load("en_trf_bertbaseuncased_lg")
vector_size = 768

import requests, io
csvLink = 'https://storage.googleapis.com/climatedatahub1/url_stats.csv' 
r = requests.get(csvLink, allow_redirects=True)
csvfields = ['url' , 'name' , 'snippet' , 'text-length' , 'content-length' , 'hits' , 'markets' ,\
             'queries' , 'tags' , 'top-domain' , 'frags'  ]
#with open(directoryRoot+'url_stats.csv', newline='', encoding='utf-8') as cf:
with io.StringIO(r.content.decode()) as cf:
    reader = csv.DictReader(cf)
    csvL = [ row for row in reader ]
urls = [ w['url'] for w in csvL ]

import zlib
#uM = np_load(directoryRoot+'url_UNSnorm_mat.npy')
matrixLink = 'https://storage.googleapis.com/climatedatahub1/url_UNSnorm_mat_zbytes' 
r = requests.get(matrixLink, allow_redirects=True)
r.raise_for_status()
uM = np_load(io.BytesIO(zlib.decompress(r.content)))


queries = [ 'energy data in US' , 'policy Canada' , 'Australian financial and insurance data' ,\
            'climate impact in Africa' , 'regenerative agriculture India' , 'green jobs' , 'Vancouver soil data' ]
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

for ii in range(0,qN):
    print(f'Q : {queries[ii]}')
    topm = topinds[:,ii]
    for jj in range(0,len(topm)):   print(f'\t{topm[jj]} : \t{urls[topm[jj]]}')
