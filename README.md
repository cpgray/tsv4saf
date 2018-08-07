# Get and process CrossRef data via API

Get metadata from the CrossRef API and use it to populate records in DSpace.

## Input

The script starts from a tab delimited file downloaded from Web of Science. It assumes the following fields are present in the file:
* AF - Author
* TI - Title
* DE - Author Keywords
* ID - Keywords Plus
* AB - Abstract
* DI - DOI -- used for the CrossRef lookup

## CrossRef

The DOI from the Web of Science file is used to get an APA style citation from dx.doi.org. Then the JSON record from the CrossRef API is fetched as JSON. The Python Habenero module is used to access the API.

Metadata is extracted from the JSON data for the following metadata fields:
* dc.publisher
* dc.type
* dc.identifier.uri
* dc.description.sponsorship
* dc.rights.uri
* dc.date.issued
* dcterms.bibliographicCitation
* uws.contributor.affiliation (uws is a local metadata namespace)

The output tab delimited data also includes, from the CrossRef data, the fields ISSN and Journal Name to help in determining copyright and embargo status of items.
