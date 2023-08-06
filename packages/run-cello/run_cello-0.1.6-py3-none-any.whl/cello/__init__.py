from Bio import SeqIO
from io import StringIO
from tqdm import tqdm
from functools import partial
import pandas as pd
import requests
import argparse
import re

CELLO_BASE_URL = "http://cello.life.nctu.edu.tw/cgi/"
TYPE_DICT = {
    "gram-": "pro",
    "gram+": "gramp",
    "eukaryote": "eu"
}

def main():
    argument_parser = argparse.ArgumentParser(description='Predict the location of a proteins in a FASTA file.')
    argument_parser.add_argument('-i', '--input', help='The input FASTA file.', required=True)
    argument_parser.add_argument('-o', '--output', help='The output CSV file.', required=True)
    argument_parser.add_argument('-t', '--type', help='Organism type.', required=True, choices=['gram-', 'gram+', 'eukaryote'])
    argument_parser.add_argument('-s', '--chunksize', help='Size of the chunk.', default=60)
    arguments = argument_parser.parse_args()

    with open(arguments.input, 'r') as reader:
        total_records = 0
        records = SeqIO.parse(reader, 'fasta')
        for _ in records:
            total_records += 1

    with open(arguments.input, 'r') as reader:
        records = SeqIO.parse(reader, 'fasta')
        with open(arguments.output, 'w') as writer:
            for r, results in enumerate(map(partial(run_cello, organism_type=arguments.type), iter_chunks(tqdm(records, total=total_records), arguments.chunksize))):
                for result in results:
                    result.to_csv(writer, index=False, header=False if r > 0 else True)

def run_cello(record_chunk, organism_type):

    if type(record_chunk) is not list:
        record_chunk = [record_chunk]

    url = f"{CELLO_BASE_URL}/main.cgi"
    payload = {
        "fasta": '\n'.join([record.format("fasta") for record in record_chunk]),
        "seqtype": "prot",
        "species": TYPE_DICT[organism_type],
        "file": None,
        "Submit": "Submit"
    }
    
    response                = requests.post(url, data=payload)
    result_url              = CELLO_BASE_URL+re.findall('temp/.+\.result_save\.txt', response.text)[0]
    result_df               = pd.read_csv(StringIO(requests.get(result_url).text), sep='\t')
    result_df['protein_id'] = result_df['#SeqName'].map(lambda x: x.split(' ')[0])
    result_df['location']   = result_df['#Most-likely-Location']
    
    yield result_df[['protein_id', 'location']]

def iter_chunks(items, size):
    chunk = []
    for item in items:
        chunk.append(item)
        if len(chunk) == size:
            yield chunk
            chunk = []
    if len(chunk) > 0:
        yield chunk

if __name__ == '__main__':
    main()
