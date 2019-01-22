import csv
import json

def clean_row(row):
    for f in row:
        if row[f]=="":
            row[f] = None
    return row


with open('countries.csv') as csv_input:
    with open('countries.json', 'w') as output:
        reader = csv.DictReader(csv_input)
        json.dump({'countries': [clean_row(r) for r in reader]}, output, indent=4)
        
