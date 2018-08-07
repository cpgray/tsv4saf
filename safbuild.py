#! /usr/bin/env python3
import sys
import csv
import urllib.request
from habanero import Crossref
import json
import datetime
import time

cr = Crossref(mailto='cpgray@uwaterloo.ca,wkroy@uwaterloo.ca')

# Check for the input file
if len(sys.argv) < 2:
    print()
    print('Usage: ./safbuild.py _wos_tsv_file_')
    print('Or:    python3 safbuild.py _wos_tsv_file_')
    print()
    sys.exit(1)
else:
    infile = sys.argv[1]

# function for conditional join
# if there are no strings in mylist, None is output rather than ''
def cj(delim, mylist):
    return delim.join(list(filter(None, mylist)))

# read in the file converting rows into dictionaries 
rows = []
with open(infile, 'rt', encoding='utf-8-sig') as intsv:
    rdr = csv.DictReader(intsv, delimiter='\t')
    for r in rdr:
        rows.append(r)

addedfields = ['pb', 'ty', 'id', 'fu', 'li', 'issn',
          'ct', 'af', 'issued', 'bc']
headers = {'Accept': 'text/x-bibliography; style=apa'}
for row in rows:
    time.sleep(0.1)
    rawdoi = row['DI']
    if rawdoi == '':
        for k in addedfields:
            row[k] = None
    else:
            
        # get a citation from dx.doi.org and add to dictionary
        doiurl = 'http://dx.doi.org/' + rawdoi
        req = urllib.request.Request(doiurl, headers=headers) 
        resp = urllib.request.urlopen(req)
        citation = resp.read().decode('utf-8').strip()
        row['bc'] = citation

        # get Crossref data and parse the JSON data into the dictionary
        data = cr.works(ids=rawdoi)
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
        for au in msg['author']:
            for afil in au['affiliation']:
                af.add(afil.get('name'))
        row['af'] = cj('|', af).replace('\r', ' ')
        pp = msg.get('published-print')
        issued = msg.get('issued')
        if pp != None:
            dt = pp
        else:
            dt = issued
        if len(dt['date-parts'][0]) != 3:
            row['issued'] = dt['date-parts'][0][0]
        else:
            row['issued'] = datetime.date(*dt['date-parts'][0])

fields = ['AF', 'TI', 'DE', 'ID', 'AB', 'pb', 'ty', 'id', 'fu', 'li', 'issn',
          'ct', 'af', 'issued', 'bc']
mapping = {'AF': 'dc.contributor.author',
           'TI': 'dc.title[en]',
           'DE': 'dc.subject[en]',
           'ID': 'dc.subject2',
           'AB': 'dc.description.abstract[en]',
           'pb': 'dc.publisher[en]',
           'ty': 'dc.type[en]',
           'id': 'dc.identifier.uri',
           'fu': 'dc.description.sponsorship[en]',
           'li': 'dc.rights.uri',
           'issn': 'ISSN',
           'ct': 'Journal_Name',
           'af': 'uws.contributor.affiliation2[en]',
           'issued': 'dc.date.issued',
           'bc': 'dcterms.bibliographicCitation[en]',
}
newfieldnames = [ mapping[k] for k in fields ]

with open('output.tsv', 'wt', encoding='utf-8') as outf:
    w = csv.DictWriter(outf, fieldnames=newfieldnames,
                       delimiter='\t', lineterminator='\n')
    w.writeheader()
    for row in rows:
        w.writerow({mapping[k]: row[k] for k in fields})
