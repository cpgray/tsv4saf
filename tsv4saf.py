#! /usr/bin/env python3
import sys
import csv
import time
import doilookup

# Check for the input file
if len(sys.argv) < 3:
    print()
    print('Usage: ./tsv4saf.py [wos_tsv_file]')
    print('Or:    python3 tsv4saf.py [wos_tsv_file] [output_tsv_file]')
    print()
    sys.exit(1)
else:
    infile = sys.argv[1]
    outfile = sys.argv[2]

# read in the file converting rows into dictionaries 
rows = []
with open(infile, 'rt', encoding='utf-8-sig') as intsv:
    rdr = csv.DictReader(intsv, restkey='extra_columns', delimiter='\t')
    for r in rdr:
        rows.append(r)

newrows = []
for row in rows:
    time.sleep(0.1)
    rowaug = doilookup.lookup(row['DI'])
    newrow = row.copy()
    newrow.update(rowaug)
    newrows.append(newrow)

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

with open(outfile, 'wt', encoding='utf-8', newline='') as outf:
    w = csv.DictWriter(outf, fieldnames=newfieldnames,
                       delimiter='\t')
    w.writeheader()
    for row in newrows:
        w.writerow({mapping[k]: row[k] for k in fields})
