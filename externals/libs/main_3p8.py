#! C:\python3.8.3
##
## MODULE main
##
## Sumeet Sandhu
## Copyright (C) 2020- Elementary IP LLC
#############################################

if 1==1:
    import sys
    from sys import exc_info
    import re , json, csv, os, string, logging, requests
    from bs4 import BeautifulSoup
    from timeit import default_timer as timer
    from datetime import datetime
    from collections import Counter
    from itertools import chain
    user_agent = "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.4; en-US; rv:1.9.2.2) Gecko/20100316 Firefox/3.6.2"
    HTTP_HEADERS = { 'User-Agent' : user_agent }
    TIMEOUT = (7,7)
    directoryRoot = '/Users/SumeetSandhu/Documents/Climate/python/'
    sys.path = [ directoryRoot ] + sys.path
    markets = [ 'en-US', 'en-CA', 'en-GB', 'en-AU', 'en-NZ', 'en-IN', 'en-ID', 'en-MY', 'en-PH', 'en-ZA' ] #sorted loosely
    #logging.basicConfig(format='%(asctime)s : %(funcName)s : %(lineno)d : %(message)s',filename=directoryRoot+'main.log', filemode='w', level=logging.INFO)

def printIDLElimit(chars):
    ## FUNCTION: limit size of IDLE GUI print output to chars, typically 1000
    class LimitedWriter:
        def __init__(self, limit):
                self.limit = limit
                self.old_stdout = sys.stdout
                self.active = True
        def toggle(self, flag):
                self.active = flag
        def write(self, value):
                if len(value) > self.limit and self.active:
                        value = value[:self.limit] + "..."
                self.old_stdout.write(value)
    sys.stdout = LimitedWriter(chars)
    return
printIDLElimit(1000)

def makeDirectory(directory):
    ## FUNCTION: if directory exists, return 1, else create directory and return 0
    error = 0
    try:    os.makedirs(directory)
    except OSError:     error = 1
    return error

def readURL(url):
    ## FUNCTION: reads url, returns header and html text
    header , html = {} , ''
    try:
        req = requests.get(url, headers=HTTP_HEADERS, timeout=TIMEOUT)
        req.raise_for_status()
        if req.status_code==200:
            header = req.headers
            if header.get('Content-Type') and re.search(r'text/html', header['Content-Type']):
                html = req.text
        else:   logger.info('status =%i',req.status_code)
    except :
        logger.error(sys.exc_info())
    return header , html

def html2file(url,html,fileHTML):
    ## FUNCTION: takes html text from url, completes links, saves as file
    textLength , links = 0 , []
    try:
        soup = BeautifulSoup(html,"lxml")
        textLength = len(soup.get_text(strip=True,separator=' ').encode('utf-8'))    #text length in bytes
        links = fixLinks(soup,url)      #correct links in soup
        soupO = soup.prettify(formatter="html")
        open(fileHTML,'w').write(soupO)
    except :
        logger.error(sys.exc_info())
    return textLength , links

def fixLinks(soup,url):
    ## FUNCTION: replace partial links with full links - https://www.w3schools.com/html/html_filepaths.asp
    ##      ADD BUTTON tag
    site = re.search(r'https*\:\/\/(\w|\.|\-|\_)+\/', url).group(0)
    #links = sorted(list(chain.from_iterable([ [ tag[attr] for tag in soup.find_all(lambda tag: tag.has_attr(attr)) ] for attr in [ 'href', 'src' ] ])))
    tmp = soup.find_all(lambda tag: tag.has_attr('href') or tag.has_attr('src'))
    linksC = []
    for tag in tmp:
        for attr in [ 'href' , 'src' ]:
            if tag.has_attr(attr):
                link = tag[attr]
                if not link: linkC = link
                elif link[0]=='#':    linkC = url+'/'+link
                elif re.search(r'^//',link):    linkC = 'https:'+link #likely a 3rd party asset, ignore later
                elif link[0]=='/':  linkC = site+link[1:]
                else:   linkC = link
                tag[attr] , linksC = linkC , linksC + [ linkC ]
    return linksC

def url2names(url,limit):
    ## FUNCTION: maps url to directory and filename (assume url starts with https*)
    ##      limit = 240 in order to allow suffixes and file extensions upto total length 255
    directory = list(map(lambda w:w[8] if re.search(r'^https\:',w) else w[7],[url]))[0]
    file = re.sub(r'\/',r'_',re.sub(r'\.',r' ',re.sub(r'^https*\:\/\/',r'',url)))[:limit] #filename < 255bytes
    return directory, file

def url2country(url,countryDomainD):
    ## FUNCTION: parses url into top level domain, country, and url fragments
    country = ''
    frags = re.sub(r' +',r' ', re.sub(r'(\W|_|^https*|html$|pdf$)',r' ', url).strip()).split(' ')
    if re.search(r'https*\:\/\/(\w|\.|\-|\_)+\/', url):
        top = re.search(r'https*\:\/\/(\w|\.|\-|\_)+\/', url).group(0)
        if re.search(r'\.(\w|\-|\_)+\/* *$',top):
            dom = re.sub(r'\/* *$',r'',re.search(r'(?<=\.)(\w|\-|\_)+\/* *$',top).group(0))
            if dom in list(countryDomainD): country = countryDomainD[dom]
            else:   country = dom
            frags = filter(lambda w: w!=dom, frags)
    return country , frags

def removeTextOverlap(textL):
    ## FUNCTION: remove overlapping strings in list - back to front
    sub = []
    #text = sorted(textL, key=lambda w:len(w))
    for ii in range(-1,-len(textL)-1,-1):
        w = textL[ii]
        for jj in range(ii-1,-len(textL)-1,-1):
            v = textL[jj]
            if ii != jj:
                if re.search(re.escape(w),v,re.I): sub += [ ii+len(textL) ]
                elif re.search(re.escape(v),w,re.I): sub += [ jj+len(textL) ]
    textO = [ textL[ii] for ii in range(0,len(textL)) if ii not in sub ]
    return textO   


if 1==1:
    tmp = []    #country domains from https://www.worldstandards.eu/other/tlds/
    with open(directoryRoot+'countryDomains.csv', newline='', encoding='utf-8') as cf:
        reader = csv.DictReader(cf)
        for row in reader:  tmp += [ row ]
    countryDomainD = {  re.search(r'(?<=^\.)[a-zA-Z]+(?= *)',w['Country code top-level domain (TLD)']).group(0) : w['Country / territory']
            for w in tmp if w.get('Country code top-level domain (TLD)') and w.get('Country / territory') and re.search(r'(?<=^\.)[a-zA-Z]+(?= *)',w['Country code top-level domain (TLD)'])  }
    queryD = {
        'data': [ 'climate data marketplace' , 'climate data' , 'climate database' , 'climate repository' ] ,
        'science' : [ 'climate measurement' , 'climate change measurement' , 'climate science data' , 'climate change data' , 'earth science data' ] ,
        'location' : [ 'geospatial climate data' , 'satellite data' , 'weather data' , 'local climate data' ] ,
        'nature' : [ 'environmental data' , 'ecological data' , 'ecosystem data' , 'nature data' ,  'climate conservation data' , 'nature conservation data' , 'climate species data' , 'climate deforestation data' ] ,
        'impact' : [ 'climate impact data' , 'climate pollution data' , 'climate water data' , 'climate soil data' , 'climate air data' , 'climate health data' ] ,
        'company' : [ 'climate corporate data' , 'sustainability data' , 'circular economy data' , 'sustainable supply chain data' , 'climate recycling data' , 'zero carbon data' , 'net zero data' , 'zero waste data' , 'climate manufacturing data' ] ,
        'economy' : [ 'climate economic data' , 'climate finance data' , 'climate commerce data' , 'climate investment data' , 'climate exchange data' , 'climate trade data' , 'climate credit data' , 'climate venture data' , 'climate funders data' ] ,
        'risk' : [ 'climate risk data' , 'climate resilience data' , 'climate insurance data' ] ,
        'energy' : [ 'climate energy data' , 'clean energy data' , 'renewable energy data' , 'climate solar data' , 'climate wind data'  ] ,
        'food' : [ 'climate agriculture data' , 'climate food data' , 'climate regeneration data' , 'regenerative agriculture data', 'permaculture data' , 'climate garden data' , 'climate home garden data' ] ,
        'infrastructure' : [ 'climate infrastructure data' , 'climate transportation data' , 'climate building data' , 'climate vehicle data' , 'net zero construction data' ] ,
        'ict' : [ 'climate sensor data' , 'climate blockchain data' , 'climate artificial intelligence data' , 'climate machine learning data' ] ,
        'entity' : [  'climate organizations data' , 'climate events data' , 'climate movements data' , 'climate services data' , 'climate jobs data' , 'climate careers data' , 'climate providers data' , 'climate consultants data' , 'climate leaders data' , 'climate volunteers data' , 'climate activists data' ] ,
        'government' : [  'climate government data' , 'climate policy data' , 'climate city data' , 'climate education data' , 'climate communication data' ]
        }   #14 topics, total 85 queries
    queries = sorted(list(chain.from_iterable(queryD.values())))

if 1==2:        #Open search results from azure_2p7.py
    resultsLr = json.loads(open(directoryRoot+'searchResults__2020-06-08-08-25-54.json','r').read())
    resultsL = [ eval(w) for w in sorted(set([ str(v) for v in resultsLr ])) ]  #unique results
    urlL = [ w['url'] for w in resultsL if re.search(r'^https*\:',w['url']) ]
    urls = sorted(set(urlL))

if 1==2:        #For each URL = markets + queries (total hits), tags (queries), name + snippet (combined from hits)
    resultD = { w:[] for w in urls }
    for w in resultsL:
        resultD[w['url']] += [ { key:w[key] for key in [ 'market' , 'query' , 'name' , 'snippet' ] } ]
    urlStatD = { w:{} for w in urls }
    tmpD = dict(list(chain.from_iterable([ [ (v,w[0]) for v in w[1] ] for w in queryD.items() ])))  #queries to tags
    for k in list(resultD):
        markets = sorted(set([ w['market'] for w in resultD[k] ]))
        queries = sorted(set([ w['query'] for w in resultD[k] ]))
        tags = sorted(set([ tmpD[q] for q in queries ]))
        sents = sorted(set([ w['name'] for w in resultD[k] ]))
        name = '. '.join(removeTextOverlap(sents))
        sents = list(chain.from_iterable([ filter(lambda u:u!='',v.split('.')) for v in set([ w['snippet'] for w in resultD[k] ]) ]))
        snippet = '. '.join(removeTextOverlap(sents)) + '.'
        urlStatD[k] = { 'hits':len(resultD[k]) , 'markets':markets , 'queries':queries , 'tags':tags , 'name':name , 'snippet':snippet }

##if 1==1:        #Topics per URL
##    tmpD = dict(list(chain.from_iterable([ [ (v,w[0]) for v in w[1] ] for w in queryD.items() ])))
##    urlTopicD = { u:{'topics':[]} for u in urls }
##    for w in resultsL:
##        urlTopicD[w['url']]['topics']+= [ tmpD[w['query']] ]
##    urlTopicD = { u:{'topics':sorted(set(urlTopicD[u]['topics']))} for u in list(urlTopicD) }
##    ##URLs per topic
##    topicD = { w:[] for w in list(queryD) }
##    for w in resultsL:  topicD[tmpD[w['query']]] += [ w['url'] ]
##    topicD = { key:sorted(set(topicD[key])) for key in list(topicD) }

if 1==2:        #Scrape URLs
    indices = [ (0,1800) , (1800,3600) , (3600,5400) , (5400,7200) ,(7200,8944) ]
    span = indices[4]
    #span = [8933,8943]
    logging.basicConfig(format='%(asctime)s : %(message)s',filename=directoryRoot+'main_'+str(span[0])+'-'+str(span[1])+'.log', filemode='w', level=logging.INFO)
    logger = logging.getLogger(__name__)
    t0=timer()
    for url in urls[span[0]:span[1]]: 
        urlD = { 'url':url , 'file':'' , 'content-length':0 , 'text-length':0 , 'links':{} }
        directory, filename = url2names(url,240)
        directory = directoryRoot+'URLS/' + directory + '/'
        error = makeDirectory(directory)
        fileHTML = directory + filename + '.html'
        urlD['file'] = fileHTML
        logger.info('URL %s',url)
        t1=timer()
        header , html = readURL(url)
        urlD['header'] = { k.lower():header[k] for k in list(header) }
        logger.info('URL TIME = %.3f',timer()-t1)
        urlD['text-length'], urlD['links'] = html2file(url,html,fileHTML)
        open(directory+filename+'_meta.json','w').write(json.dumps(urlD))
    print(f'span = {span} in time = {timer()-t0:.2f} seconds')

if 1==2:        # URL content stats
    logging.basicConfig(format='%(asctime)s : %(message)s',filename=directoryRoot+'main_stats.log', filemode='w', level=logging.INFO)
    logger = logging.getLogger(__name__)
    csvL = []
    csvfields = ['url' , 'name' , 'snippet' , 'text-length' , 'content-length' , 'hits' , 'markets' , 'queries' , 'tags' , 'top-domain' , 'frags'  ]
    for url in urls:
        directory, filename = url2names(url,240)
        directory = directoryRoot+'URLS/' + directory + '/'
        metaD = json.loads(open(directory+filename+'_meta.json','r').read())
        csvD = { 'url':url }
        for k in [ 'text-length' , 'content-length' ]: csvD[k] = metaD[k]
        if metaD['header'].get('content-length'):    csvD['content-length'] = int(metaD['header']['content-length'])
        for f in [ 'name' , 'snippet' , 'hits' ]:    csvD[f] = urlStatD[url][f]
        for f in [ 'markets' , 'queries' , 'tags' ]:    csvD[f] = ' , '.join(urlStatD[url][f])
        csvD['top-domain'] , frags = url2country(url,countryDomainD)
        csvD['frags'] = ' , '.join([ f.lower() for f in frags ])
        csvL += [ csvD ]
    with open(directoryRoot+'url_stats.csv', 'w', newline='') as cf:
        writer = csv.DictWriter(cf, fieldnames=csvfields)
        writer.writeheader()
        writer.writerows(csvL)


if 1==1:    #LOAD URLS METADATA
    def cleandom(dom,repD):
        cdom = dom
        if repD.get(dom): cdom = repD[dom]
        return cdom
    csvfields = ['url' , 'name' , 'snippet' , 'text-length' , 'content-length' , 'hits' , 'markets' , 'queries' , 'tags' , 'top-domain' , 'frags'  ]
    csvL = []
    with open(directoryRoot+'url_stats.csv', newline='', encoding='utf-8') as cf:
        reader = csv.DictReader(cf)
        csvL = [ row for row in reader ]

    repd = [ 'aws', 'blog', 'build', 'careers', 'center', 'city', 'com', 'community', 'company',
             'consulting', 'digital', 'earth', 'edu', 'education', 'fund', 'global', 'google', 'gov',
             'green', 'info', 'int', 'kpmg', 'mil', 'museum', 'net', 'news', 'one', 'org', 'pioneer',
             'science', 'scot', 'systems', 'tech', 'tokyo', 'toyota', 'training', 'wales', 'world' ]
    repD = { dom:'United States of America (USA)' for dom in
             [ 'gov' , 'edu' , 'mil' , 'google' , 'aws' , 'careers' , 'com' , 'org' ] }
    vizL = [ { 'country': cleandom(w['top-domain'],repD), 'datasize':w['text-length']+w['content-length'] , 'tags':len(w['tags'].split()) } for w in csvL ]
    vizfields = ['country','datasize','tagn','tagt','sites']
    countries = sorted(set([ w['country'] for w in vizL ]))
    vcL = []
    from math import log as m_log, sqrt
    compf = sqrt
    #compf = lambda w:w
    for c in countries:
        vc = [ w for w in vizL if w['country']==c ]
        vcL += [ { 'country':c , 'sites':len(vc) , 'datasize':compf(sum([int(w['datasize']) for w in vc])) ,
                   'tagn':sum([w['tags'] for w in vc]) , 'tagt':len(set([w['tags'] for w in vc])) } ]
    with open(directoryRoot+'url_aggviz.csv', 'w', newline='') as cf:
        writer = csv.DictWriter(cf, fieldnames=vizfields)
        writer.writeheader()
        writer.writerows(vcL)

if 1==2:
    colocfields = [ 'country' , 'latitude' , 'longitude' , 'name' ]   #https://developers.google.com/public-data/docs/canonical/countries_csv
    with open(directoryRoot+'countries_latitude_longitude.csv', newline='', encoding='utf-8') as cf:
        reader = csv.DictReader(cf)
        colocL = [ row for row in reader ]
    colocD = { w['country'].lower():w for w in colocL }


if 1==2:
    searchset = []
    for w in csvL:
        for k in [ 'tags' , 'queries' ]: #, 'top-domain' , 'frags' ]:
            searchset += re.split(r' ,* *',w[k])
    searchset = sorted(set(searchset))
    open(directoryRoot+'searchset.txt','w').write('\n'.join(searchset))

