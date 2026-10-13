from typing import List
import urllib.request
import logging
import json
from roagg.models.research_output_item import ResearchOutputItem
from roagg.helpers.utils import string_word_count, remove_resolver_prefix_from_doi, capitalize_first


def _has_creator_affiliation(record, ror):
    ror_id = ror.rstrip("/").rsplit("/", 1)[-1]
    for contributor_type in ("author", "editor"):
        for contributor in record.get(contributor_type, []):
            for affiliation in contributor.get("affiliation", []):
                for identifier in affiliation.get("id", []):
                    identifier_value = identifier.get("id", "")
                    if (
                        identifier.get("id-type") == "ROR"
                        and identifier_value.rstrip("/").rsplit("/", 1)[-1] == ror_id
                    ):
                        return True
    return False


def _publication_year(record):
    for date_field in ("published-online", "published-print", "published", "issued", "deposited"):
        date_parts = record.get(date_field, {}).get("date-parts", [])
        if date_parts and date_parts[0] and date_parts[0][0] is not None:
            return date_parts[0][0]
    return None


class CrossRefAPI:
    crossref_base_url = "https://api.crossref.org/v1/"

    def __init__(self, page_size: int = 200, ror: str = "", results: List[ResearchOutputItem] = []):
        self.page_size = page_size
        self.ror = ror
        self.results = results

            
    def get_records(self) -> List[ResearchOutputItem]:
        if not self.ror:
            return []
        crossref_results = []

        params = {
            'rows': self.page_size,
            'cursor': '*',
            'filter': f'ror-id:{self.ror}' 
        }
        retrieve_count = 0

        while True:
            query_string = urllib.parse.urlencode(params)
            url = f"{self.crossref_base_url}works?{query_string}"
            with urllib.request.urlopen(url) as response:
                json_response = json.loads(response.read())
                if 'message' in json_response:
                    crossref_results.extend(json_response['message']['items'])
                retrieve_count = len(crossref_results)
                logging.info(f"Retrieved CrossRef {retrieve_count} of {json_response['message']['total-results']}")

                if 'next-cursor' in json_response['message'] and json_response['message']['next-cursor'] and len(json_response['message']['items']) > 0:
                    params['cursor'] = json_response['message']['next-cursor']
                else:
                    break

        # Create a dictionary for O(1) lookups
        doi_to_item = {item.doi.lower(): item for item in self.results if item.doi}
        
        for r in crossref_results:

            haveCreatorAffiliation = _has_creator_affiliation(r, self.ror)
            publication_year = _publication_year(r)

            doi = remove_resolver_prefix_from_doi(r.get('DOI', None))
            if doi is None:
                continue

            recordMatch = False

            item = doi_to_item.get(doi.lower())
            if item:
                recordMatch = True
                item.crossRefReferenceCount = r.get('reference-count', None)
                item.crossRefIsReferencedByCount = r.get('is-referenced-by-count', None)
                item.inCrossRef = True
                item.crossRefResourceType = r.get('type', None)
                item.haveCreatorAffiliation = haveCreatorAffiliation
                if publication_year is not None:
                    item.publicationYear = publication_year
            if not recordMatch:
                item = ResearchOutputItem(
                    doi=doi,
                    isPublisher=None,
                    resourceType=r.get('type', None),
                    title=r.get('title', None)[0],
                    publisher=r.get('publisher', None),
                    publicationYear=publication_year,
                    createdAt=r.get('created', None)['date-time'] if r.get('created', None) else None,
                    haveContributorAffiliation=None,
                    haveCreatorAffiliation=haveCreatorAffiliation,
                    isLatestVersion=None,   
                    isConceptDoi=None,
                    inCrossRef=True,
                    openAlexResourceType=r.get('type', None),
                    crossRefIsReferencedByCount=r.get('is-referenced-by-count', None),
                    crossRefReferenceCount=r.get('reference-count', None),
                    titleWordCount=string_word_count(r.get('title', None)[0])
                )
                item.resourceType = capitalize_first(item.resourceType) if item.resourceType else None
                self.results.append(item)
                doi_to_item[item.doi.lower()] = item  # Add to lookup dictionary

        return crossref_results