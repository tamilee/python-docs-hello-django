#! C:\python3.8.3
##
## MODULE main
##
## Sumeet Sandhu
## Copyright (C) 2020- Elementary IP LLC
#############################################

import sys
from sys import exc_info
import re , json, csv, os, string, logging, requests
from bs4 import BeautifulSoup
from timeit import default_timer as timer
from datetime import datetime
from collections import Counter
from itertools import chain
import numpy
from numpy import array, shape, dot, zeros, eye, ceil, sqrt, linalg, diag, kron, sum as np_sum,\
     save as np_save, load as np_load, append as np_append, concatenate as np_concat,\
     amax as np_max, argsort as np_argsort
from sklearn import preprocessing

URL_FIELDS = {'U':0, 'N':1, 'S':2 } #, 'T':3 } text #fields mapped to column blocks of searchMatrix
ALGORITHMS = [  '1UNSu' , '1UNSn', '2Uu', '2Un', '2Nu', '2Nn', '2Su', '2Sn' , '3UNS' ]
STOP_WORDS = [
     '!', '"', '#', '%', '&', "'", "'", '(', ')', '*', ',', '-', '.', ':', ';', '<', '>', '?', '@', '[', '\\', '\\/', ']', '^', '_', '`', '{', '|', '}', '~',\
     'a', 'according', 'all', 'also', 'an', 'and', 'another' , 'any', 'are', 'as', 'at', 'away',\
     'be', 'being', 'by', 'can','could','became','become',\
     'did', 'during', 'following', 'for', 'from', 'further','around',\
     'given', 'has', 'having', 'here', 'hereby', 'herefore', 'herein', 'hereof', 'how','however',\
     'if', 'in', 'into', 'is', 'it', 'its', 'itself',\
     'may', 'might', 'must', 'next', 'of', 'on', 'one', 'or', 'other', 'over', 'ought',\
     'said', 'same', 'should', 'since', 'so', 'such', 'many',\
     'that', 'the', 'then', 'there', 'thereby', 'therefore', 'therein', 'thereof', 'these', 'this', 'those', 'through', 'thus', 'thusly', 'to',\
     'was', 'with', 'what', 'when', 'where', 'whereby', 'wherefore', 'wherein', 'which', 'while', 'why', 'with','would' ]

def similarURL(queryMatrix,searchMatrix,topN):
    ## FUNCTION: find top matches for query in search set
    ## query = Q X vector_size , searchMatrix = num_urls X vector_sizex3 (3 URL_FIELDS)
    ## Returns topinds =  topN x fields array , best matching rows of searchMatrix
    qM , sM , topinds = queryMatrix , searchMatrix , { a:array([]) for a in ALGORITHMS }
    #ALGORITHM 1UNS = concatenated as-is U,N,S fields
    dpM = dot( sM , kron(array(([1,1,1])),qM).T )    #unnormalized
    topinds['1UNSu'] = np_argsort(dpM, axis=0)[-1:-topN-1:-1,:]
    snM = preprocessing.normalize(sM,norm='l2',axis=1)  #normalized
    dpM = dot( snM , kron(array(([1,1,1])),qM).T )
    topinds['1UNSn'] = np_argsort(dpM, axis=0)[-1:-topN-1:-1,:]
    #ALGORITHM 2{UNS} = separate U,N,S fields
    snM = zeros((shape(sM)[0],1))
    for f in list(URL_FIELDS):
        ssM = sM[:,URL_FIELDS[f]*vector_size:(URL_FIELDS[f]+1)*vector_size] #unnormalized
        dpM = dot( ssM , qM.T )
        topinds['2'+f+'u'] = np_argsort(dpM, axis=0)[-1:-topN-1:-1,:]
        ssM = preprocessing.normalize(ssM,norm='l2',axis=1)     #normalized
        dpM = dot( ssM , qM.T )
        topinds['2'+f+'n'] = np_argsort(dpM, axis=0)[-1:-topN-1:-1,:]
        snM = np_append(snM, ssM ,axis=1)
    #ALGORITHM 3{UNS} = concatenation of normalized U,N,S fields
    snM = snM[:,1:]
    dpM = dot( snM , kron(array(([1,1,1])),qM).T )
    topinds['3UNS'] = np_argsort(dpM, axis=0)[-1:-topN-1:-1,:]
    return topinds

if 1==1:    #SETUP
    directoryRoot = '/Users/SumeetSandhu/Documents/Climate/python/'
    sys.path = [ directoryRoot , directoryRoot+'.env/' , directoryRoot+'.env/lib/python3.8/' ,
                 directoryRoot+'.env/lib/python3.8/site-packages' ,
                 '/Users/SumeetSandhu/Documents/Patent/Code/Python/CONFIZ/Source' ] + sys.path
    from main_3p8 import printIDLElimit , url2names
    printIDLElimit(1000)
    logging.basicConfig(format='%(asctime)s : %(message)s',filename=directoryRoot+'search.log', filemode='w', level=logging.INFO)
    logger = logging.getLogger(__name__)
    import spacy
    nlp = spacy.load("en_trf_bertbaseuncased_lg")
    vector_size = 768
if 1==1:    #LOAD URLS METADATA
    #option 1 - local file
    csvfields = ['url' , 'name' , 'snippet' , 'text-length' , 'content-length' , 'hits' , 'markets' , 'queries' , 'tags' , 'top-domain' , 'frags'  ]
    with open(directoryRoot+'url_stats.csv', newline='', encoding='utf-8') as cf:
        reader = csv.DictReader(cf)
        csv1 = [ row for row in reader ]
    urls = [ w['url'] for w in csvL ]
##    #option 2 - url
##    csvLink = 'https://storage.googleapis.com/climatedatahub1/url_stats.csv' 
##    import requests, io
##    r = requests.get(csvLink, allow_redirects=True)
##    with io.StringIO(r.content.decode()) as cf:
##        reader = csv.DictReader(cf)
##        csv2 = [ row for row in reader ]
##    csv1 == csv2

if 1==2:    #GENERATE BERT VECTORS
    for csvD in csvL[263:]:     #upto 263 saved full text tensors, not their sum
        url , name , snippet , textLength = csvD['url'] , csvD['name'] , csvD['snippet'] , csvD['text-length']
        logger.info('%s',url)
        dirfile, filename = url2names(url,240)
        directory = directoryRoot+'URLS/' + dirfile + '/'
        stream = [ url , name , snippet ]
        suffix = [ '_U.npy' , '_N.npy' , '_S.npy' ]
        docs = list(nlp.pipe(stream))
        for ii in range(0,len(docs)):
            vector = sum(docs[ii].tensor)
            logger.info('%s\tnorm=%0.4f',filename+suffix[ii],linalg.norm(vector,2))
            np_save(directory+filename+suffix[ii],vector)
##        suffix = '_T.npy'
##        if int(textLength)>0:
##            html = open(directory+filename+'.html','r').read()
##            soup = BeautifulSoup(html,"lxml")
##            text = soup.get_text(strip=True,separator='. ')
##            #stream = [ re.sub(r'(\W|_)+',r' \g<0> ',t) for t in textL ]    #tokenize = re.sub(r'(\W|_)+',r' \g<0> ',w) ; reverse = re.sub(r' (\W|_)+ ',lambda m:m.group(0)[1:-1], w)
##            doc = nlp(text)
##            vector = sum(doc.tensor)
##        else:
##            vector = zeros((vector_size,))
##        logger.info('%s\tnorm=%0.4f',filename+suffix,linalg.norm(vector,2))
##        np_save(directory+filename+suffix,vector)

##        #TUTORIAL doc.tensor is per token, sum(doc.tensor) ~ sum(doc.last_hidden_state), state is over wordpieces
##        w = list(nlp.pipe(list of text))[0]
##        print(w)
##        shape(w.tensor)
##        shape(w.doc._.trf_last_hidden_state)
##        w._.trf_word_pieces_
##        (array(list(sum(w.doc._.trf_last_hidden_state)))-list(sum(w.tensor))>1e-6).any()

if 1==2:    #VECTORS TO MATRIX
    urlM , vectorUNS = zeros((1,vector_size*3)) , zeros((1,vector_size*3))
    for csvD in csvL:
        url , name , snippet , textLength = csvD['url'] , csvD['name'] , csvD['snippet'] , csvD['text-length']
        logger.info('%s',url)
        dirfile, filename = url2names(url,240)
        directory = directoryRoot+'URLS/' + dirfile + '/'
        suffix = [ '_U.npy' , '_N.npy' , '_S.npy' ]
        vectorL = []    #vector[0,:] = ...
        for ii in range(0,len(suffix)):
            vectorL += [ np_load(directory+filename+suffix[ii]) ]
        vectorUNS[0,:] = np_concat(vectorL,axis=0)
        urlM = np_append(urlM,vectorUNS,axis=0)
    urlM = urlM[1:,:]
    np_save(directoryRoot+'url_UNS_mat.npy',urlM)   #num_urls X vector_sizex3

if 1==2:    #NORMALIZE MATRIX (per url field)
    uM = np_load(directoryRoot+'url_UNS_mat.npy')
    unM = zeros((shape(uM)[0],1))
    for f in [ 0,1,2 ]:
        nM = uM[:,f*vector_size:(f+1)*vector_size] #unnormalized
        nM = preprocessing.normalize(nM,norm='l2',axis=1)     #normalized
        unM = np_append(unM, nM ,axis=1)
    unM = unM[:,1:]/sqrt(3)
    np_save(directoryRoot+'url_UNSnorm_mat.npy',unM)   #num_urls X vector_sizex3

if 1==2:    #LOAD URLS MATRIX
    #option 1 - local file
    u1 = np_load(directoryRoot+'url_UNSnorm_mat.npy')
    #option 2 - url of matrix
    matrixLink = 'https://storage.googleapis.com/climatedatahub1/url_UNSnorm_mat.npy' 
    r = requests.get(matrixLink, allow_redirects=True)
    r.raise_for_status()
    u2 = np_load(io.BytesIO(r.content))
    (u1==u2).all()
    #
    import zlib
    bytestream = io.BytesIO()
    np_save(bytestream, u1)
    compressed = zlib.compress(bytestream.getvalue())
    open(directoryRoot+'url_UNSnorm_mat_zbytes', 'wb').write(compressed)
    #option 3 - url of compressed bytes
    matrixLink = 'https://storage.googleapis.com/climatedatahub1/url_UNSnorm_mat_zbytes' 
    r = requests.get(matrixLink, allow_redirects=True)
    r.raise_for_status()
    u2 = np_load(io.BytesIO(zlib.decompress(r.content)))

if 1==2:    #TESTING
    topN = 5    #top matches
    searchUrls = [ 'https://en.climate-data.org/', 'https://climate.ncsu.edu/data_services',
                   'https://climatepolicyinitiative.org/climate-finance/',
                   'http://www.environment.gov.au/fed/catalog/main/home.page',
                   'https://www.probuilder.com/tips-for-building-net-zero-energy-homes',
                   'https://openei.org/wiki/Data',
                   'https://www.usda.gov/oce/climate_change/FoodSecurity.htm',
                   'https://www2.gov.bc.ca/gov/content/environment/air-land-water/land/soil/soil-information-finder',
                   'https://climate.com/careers',
                   'https://www.exec.gov.nl.ca/exec/occ/climate-data/index.html' ]
    searchInds = [ urls.index(w) for w in searchUrls ]
    urlM = np_load(directoryRoot+'url_UNS_mat.npy')
    searchMatrix = zeros((1,vector_size*3))     #SEARCH MATRIX
    for ii in searchInds:
        searchMatrix = np_append(searchMatrix,urlM[ii:ii+1,:],axis=0)
    searchMatrix = searchMatrix[1:,:]
    if 1==2: #Verify top matches
        uM = preprocessing.normalize(urlM,norm='l2',axis=1)
        uuM = dot(uM,uM.T)
        indT = np_argsort(uuM, axis=1)[:,-1:-topN-1:-1]    #top 5 matches for each URL
        for ii in searchInds:
            print(f'QUERY = {urls[ii]}')
            for jj in indT[ii,:]:   print(f'\t\t{urls[jj]}')
    #Queries
    queries = [ 'energy data in US' , 'policy Canada' , 'Australian financial and insurance data' ,
                'climate impact in Africa' , 'regenerative agriculture India' , 'green jobs' ,
                'Vancouver soil data' ] # , 'volunteering in London' , 'geospatial data' , 'Extinction Rebellion' ]
    bestMatches = [ w-1 for w in [ 6 , 3 , 3 , 7 , 7 , 9 , 8 ] ]
    qN = len(queries)
    #for ii in range(0,qN):    print(f'Q : {queries[ii]}\n\tM : {searchUrls[bestMatches[ii]]}')
    qdocs = list(nlp.pipe(queries))
    QM , qV = zeros((1,vector_size)) , zeros((1,vector_size))   #QUERY MATRIX
    for qd in qdocs:
        qV[0,:] = sum(qd.tensor)
        QM = np_append(QM,qV,axis=0)
    QM = QM[1:,:]
    if 1==2: #TEST with known Search Matrix
        topinD = similarURL(QM,searchMatrix,topN)
        amD1 = { alg: round(100*sum((array(bestMatches) == topinD[alg][0,:])*1 )/qN,2) for alg in ALGORITHMS }
        print(f'top1 accuracy = {amD1}')
        #top1 accuracy = {'1UNSu': 28.57, '1UNSn': 42.86, '2Uu': 14.29, '2Un': 71.43, '2Nu': 0.0, '2Nn': 28.57, '2Su': 28.57, '2Sn': 42.86, '3UNS': 71.43}
        amDn = { alg: round(100*sum([ int( bestMatches[ii] in topinD[alg][:,[ii]] ) for ii in range(0,qN) ])/qN,2) for alg in ALGORITHMS }
        print(f'top5 accuracy = {amDn}')
        #top5 accuracy = {'1UNSu': 57.14, '1UNSn': 71.43, '2Uu': 42.86, '2Un': 71.43, '2Nu': 71.43, '2Nn': 71.43, '2Su': 42.86, '2Sn': 100.0, '3UNS': 85.71}
        algo = '3UNS'   #PRINT MATCHES
        for ii in range(0,qN):
            print(f'Q : {queries[ii]}\t match = {bestMatches[ii]}')
            topm = topinD[algo][:,ii]
            for jj in range(0,len(topm)):   print(f'\t{topm[jj]} : \t{searchUrls[topm[jj]]}')
    if 1==1:    #TEST with full search matrix
        topinD = similarURL(QM,urlM,topN)
        algo = '3UNS'   #PRINT MATCHES
        for ii in range(0,qN):
            print(f'Q : {queries[ii]}')
            topm = topinD[algo][:,ii]
            for jj in range(0,len(topm)):   print(f'\t{topm[jj]} : \t{urls[topm[jj]]}')
    

    
