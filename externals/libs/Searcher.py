#! C:\python3.8.3

import sys
import csv , numpy
import numpy
from numpy import array, dot, zeros, kron, load as np_load, argsort as np_argsort, append as np_append
import spacy
import requests, io
import os
import zlib

class Searcher:
    def __init__(self):
        self.csvD = None
        self.urls = None
        self.read_csv()
        self.vector_size = 768
        print("Loading nlp...")
        self.nlp = spacy.load("en_trf_bertbaseuncased_lg")
        self.uM = None
        self.read_matrix()

    def read_csv(self):
        print("reading csv...")
        csvLink = 'https://mlws5706376320.z20.web.core.windows.net/url_stats.csv'
        r = requests.get(csvLink, allow_redirects=True)
        csvfields = ['url' , 'name' , 'snippet' , 'text-length' , 'content-length' , 'hits' , 'markets' ,\
                 'queries' , 'tags' , 'top-domain' , 'frags'  ]
        with io.StringIO(r.content.decode()) as cf:
            reader = csv.DictReader(cf)
            csvL = [ row for row in reader ]
            self.csvD = { w['url']:w for w in csvL }
            self.urls = [ w['url'] for w in csvL ]

    def read_matrix(self):
        print("reading matrix...")
        matrixLink = 'https://mlws5706376320.z20.web.core.windows.net/url_UNSnorm_mat_zbytes'
        r = requests.get(matrixLink, allow_redirects=True)
        r.raise_for_status()
        self.uM = np_load(io.BytesIO(zlib.decompress(r.content)))

    def searchURLs(self, request, query, topN):
        queries = [query]
        qN = len(queries)
        qdocs = list(self.nlp.pipe(queries))
        QM , qV = zeros((1,self.vector_size)) , zeros((1,self.vector_size))   #QUERY MATRIX
        for qd in qdocs:
            qV[0,:] = sum(qd.tensor)
            QM = np_append(QM,qV,axis=0)
        QM = QM[1:,:]

        dpM = dot( self.uM , kron(array(([1,1,1])),QM).T )
        topinds = np_argsort(dpM, axis=0)[-1:-topN-1:-1,:]

        resultDict = {}
        for ii in range(0,qN):
            topiq = topinds[:,ii].tolist()
            resultDict[queries[ii]] = [ dict([ ('rank',str(jj[0]+1)) ] +
                                      [ (key,self.csvD[self.urls[jj[1]]][key]) for key in [ 'url','name','snippet','tags'] ] ) for jj in enumerate(topiq) ]
        return resultDict
