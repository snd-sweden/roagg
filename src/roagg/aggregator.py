import sys
from typing import List
from roagg.helpers.ror import get_names_from_ror
from roagg.providers.datacite import DataCiteAPI
from roagg.providers.openaire import OpenAireAPI
from roagg.providers.openalex import OpenAlexAPI
from roagg.providers.crossref import CrossRefAPI
import logging
from roagg.models.research_output_item import ResearchOutputItem
import json
import csv
from dataclasses import fields

def aggregate(name: List[str] = [], ror: str = "", output: str = "output.csv") -> None:
    if ror:
        ror_name = get_names_from_ror(ror)
        name.extend(ror_name)
    
    # remove duplicates
    name = list(set(name))

    datacite = DataCiteAPI(name=name, ror=ror)
    url = datacite.api_request_url()
    # debug print of the query string
    logging.info("DataCite url:")
    logging.info(url)

    records = datacite.all()
    research_output_items = []
    logging.info(f"Checking {len(records)} records...")
    for record in records:
        research_output_items.append(datacite.get_record(record))

    openaire = OpenAireAPI(ror=ror, results=research_output_items)
    openaire_id = openaire.get_openaire_id_from_ror()
    logging.info(f"OpenAire ID from ROR {ror} : {openaire_id}")
    openaire.get_records()

    openalex = OpenAlexAPI(ror=ror, results=research_output_items)
    openalex_id = openalex.get_openalex_id_from_ror()
    logging.info(f"OpenAlex ID from ROR {ror} : {openalex_id}")
    openalex.get_records()

    crossreff = CrossRefAPI(ror=ror, results=research_output_items)
    logging.info(f"CrossRef from ROR {ror}")
    crossreff.get_records()

    logging.info(f"Writing: {output}")
    
    write_csv(research_output_items, output)
    logging.info(f"Writing output to csv: {output} - Done")

def write_csv(records: List[ResearchOutputItem], output: str) -> None:
    # Get field names from the dataclass
    dataclass_fields = fields(ResearchOutputItem)
    header = [field.name for field in dataclass_fields]
    
    def format_value(value):
        """Format values for CSV output"""
        if value is None:
            return ""
        elif isinstance(value, bool):
            return 1 if value else 0
        else:
            return value

    with open(output, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        
        writer.writerows([
            [format_value(getattr(record, field.name)) for field in dataclass_fields]
            for record in records
        ])
