#! /usr/bin/env python3
import sys
import os.path
import urllib.request
from urllib.parse import quote
from habanero import Crossref

# The Crossref Habanero class can be initialized with an email address to
# ensure traffic is put in the polite pool of Crossref servers.
# If you would like to do this, provide an email address in an external
# text file named polite_email.txt.
if os.path.isfile('polite_email.txt'):
    with open('polite_email.txt', 'rt') as email:
        addr = email.read().strip()
    cr = Crossref(mailto=addr)
else:
    cr = Crossref()

# function for conditional join of a list of strings
# if there are no strings in mylist, None is output rather than an empty string
def cj(delim, mylist):
    return delim.join(list(filter(None, mylist)))

addedfields = ['pb', 'ty', 'id', 'fu', 'li', 'issn',
          'ct', 'af', 'issued', 'bc']
headers = {'Accept': 'text/x-bibliography; style=apa'}

def lookup(rawdoi, row={}):
    # The raw DOI is escaped because DOIs are not necessarily URL safe
    doi = quote(rawdoi)
    if doi == '':
        for k in addedfields:
            row[k] = None
    else:
        # get a citation from dx.doi.org and add to dictionary
        doiurl = 'http://dx.doi.org/' + doi
        req = urllib.request.Request(doiurl, headers=headers)
        try:
            resp = urllib.request.urlopen(req)
            citation = resp.read().decode('utf-8').strip()
            row['bc'] = citation
        except Exception as e:
            for k in addedfields:
                row[k] = None
            row['bc'] = 'DOI not found: ' + rawdoi

        # get Crossref data and parse the JSON data into the dictionary
        try:
            data = cr.works(ids=doi)
            msg = data['message']
            row['pb'] = msg['publisher']
            row['ty'] = msg['type']
            row['id'] = 'https://dx.doi.org/' + msg['DOI']
            fu = msg.get('funder')
            if fu != None:
                row['fu'] = '|'.join([cj(': ',
                                         [i['name'], ', '.join(i['award'])])
                                      for i in fu])
            else:
                row['fu'] = None
            li = msg.get('license')
            if li != None:
                row['li'] = '|'.join([i['URL'] for i in li])
            else:
                row['li'] = None
            issn = msg.get('ISSN')
            if issn != None:
                row['issn'] = issn[-1]
            else:
                row['issn'] = None
            ct = msg.get('container-title')
            if ct != None:
                row['ct'] = msg['container-title'][0]
            else:
                row['ct'] = None
            af = set([])
            au = msg.get('author')
            if au != None:
                for a in au:
                    fi = a.get('affiliation')
                    if fi != None:
                        for afil in fi:
                            af.add(afil.get('name'))
                row['af'] = cj('|', af)
            else:
                row['af'] = None
            dt = msg['issued']['date-parts'][0]
            row['issued'] = '-'.join([ str(i).zfill(2) for i in dt ])
        except Exception as e:
            for k in addedfields:
                row[k] = None
            row['bc'] = 'DOI not found: ' + rawdoi
            row['id'] = 'DOI not found: ' + rawdoi
    return row

if __name__ == '__main__':
    row = lookup(sys.argv[1])
    for k in addedfields:
        print('{0}:\t{1}'.format(k, row[k].encode('utf-8').decode('utf-8')))
