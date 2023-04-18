import json
import unicodedata
import re
import hashlib

#TODO: fix the hard coded json path
#TODO: redundent to have the md5 checks as their own specific can be done by just adding them to fields_to_compare list
#TODO: set up a better place for json files to be stored

def normalize_string(s):
    s = s.lower()
    s = ''.join(c for c in unicodedata.normalize('NFKD', s) if not unicodedata.combining(c) and not unicodedata.category(c) == 'Punctuation')
    s = s.replace(':', '')
    s = ' '.join(s.split())
    return s

def compare_subjects(s1, s2):

    s1_normalized = normalize_string(s1)
    s2_normalized = normalize_string(s2)

    s1_subjects = s1_normalized.split(',')
    s2_subjects = s2_normalized.split(',')

    s1_subjects.sort()
    s2_subjects.sort()

    return s1_subjects == s2_subjects


def compare_normalized_field(d1, d2):
    
    d1_normalized = normalize_string(d1)
    d2_normalized = normalize_string(d2)
    
    return d1_normalized == d2_normalized

def log_error(errors, field, doi, curve_url, hyrax_url, message):
    if doi in errors:
        errors[doi]['errors'].append({
            'field': field,
            'curve_url': curve_url,
            'hyrax_url': hyrax_url,
            'message': message
        })
    else:
        errors[doi] = {
            'doi': doi,
            'curve_url': curve_url,
            'hyrax_url': hyrax_url,
            'errors': [{
                'field': field,
                'message': message
            }]
        }

fields_to_compare = ['title', 'creator', 'date', 'language', 'publisher', 'thesis_degree_level', 'subject', 'thesis_degree_disc', 'contributor', 'thesis_degree_name']

# Load the JSON files
with open('/home/manfred/etdscrapy/etdscraper/etdscraper/spiders/curve_output.json') as f:
    file1 = json.load(f)

with open('/home/manfred/etdscrapy/etdscraper/etdscraper/spiders/hyrax_output.json') as f:
    file2 = json.load(f)

file1_dois = {item['identifier'] for item in file1}

errors = {}
# Loop over DOIs in file2 and compare with file1
for item2 in file2:
    if item2['identifier'] in file1_dois:
        # Find the item with the same DOI in file1
        item1 = next(item1 for item1 in file1 if item1['identifier'] == item2['identifier'])
        for field in fields_to_compare:
            if field == "pdf_md5_hash":
                if item1[field] != item2[field]:
                    log_error(errors, field, item1['identifier'], item1['curve_url'], item2['hyrax_url'], f"{field} does not match")
            elif field == "zip_md5_hash":
                if item1[field] != item2[field]:
                    log_error(errors, field, item1['identifier'], item1['curve_url'], item2['hyrax_url'], f"{field} does not match")
            elif field == "abstract":
                if not compare_normalized_field(item1[field], item2[field]):
                    log_error(errors, field, item1['identifier'], item1['curve_url'], item2['hyrax_url'], f"{field} does not match")
            elif field == "thesis_degree_name":
                if not compare_normalized_field(item1[field], item2[field]):
                    log_error(errors, field, item1['identifier'], item1['curve_url'], item2['hyrax_url'], f"{field} does not match")
            else:
                if item1[field] != item2[field]:
                    log_error(errors, field, item1['identifier'], item1['curve_url'], item2['hyrax_url'], f"{field} does not match")

with open('errors.json', 'w') as f:
    json.dump(errors, f, indent=2)