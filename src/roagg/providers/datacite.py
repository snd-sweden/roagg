from typing import List
import urllib.request
import logging
import json
from roagg.helpers.utils import get_roagg_version
from roagg.models.research_output_item import ResearchOutputItem
from roagg.helpers.utils import match_patterns, string_word_count

class DataCiteAPI:
    def __init__(self, page_size: int = 500, name: List[str] = [], ror: str = ""):
        self.page_size = page_size
        self.name = name
        self.ror = ror

    def get_query_string(self) -> str:
        if not self.name and not self.ror:
            return ""
            
        query_parts = []
        
        if self.name:
            # Separate wildcard and exact matches, handle spaces in wildcard queries appropriately
            wildcard = ' OR '.join(n.replace(" ", "\\ ") for n in self.name if '*' in n)
            exact = ' OR '.join(f'"{n}"' for n in self.name if '*' not in n)
            name_fields = [
                "creators.affiliation.name",
                "contributors.affiliation.name", 
                "publisher.name"
            ]

            if wildcard and exact:
                name_conditions = f'{wildcard} OR {exact}'
            else:
                name_conditions = wildcard or exact
            
            query_parts.extend([f"{field}:({name_conditions})" for field in name_fields])
        
        if self.ror:
            ror_fields = [
                "publisher.publisherIdentifier",
                "creators.affiliation.affiliationIdentifier", 
                "contributors.affiliation.affiliationIdentifier",
                "creators.nameIdentifiers.nameIdentifier",
                "contributors.nameIdentifiers.nameIdentifier",
                "fundingReferences.funderIdentifier"
            ]
            query_parts.extend([f'{field}:"{self.ror}"' for field in ror_fields])
            # nameIdentifiers are formated without https://ror.org/ prefix from some sources, so we need to check both
            query_parts.extend([f'{field}:"{self.ror.split("https://ror.org/")[1]}"' for field in ror_fields])
        
        return " OR ".join(query_parts)

    def api_request_url(self, page_size: int = None) -> str:
        if page_size is None:
            page_size = self.page_size
        params = urllib.parse.urlencode({
            'page[size]': page_size,
            'page[cursor]': '1',
            'affiliation': 'true',
            'publisher': 'true',
            'detail': 'true',
            'disable-facets': 'false',
            'query': self.get_query_string()
        })
        return f"https://api.datacite.org/dois?{params}"

    @staticmethod
    def get_api_result(url: str) -> dict:
        request = urllib.request.Request(url)
        version = get_roagg_version()
        request.add_header('User-Agent', f'ResearchOutputAggregator/{version} (https://github.com/snd-sweden/research-output-aggregator; mailto:team-it@snd.se)')
        try:
            with urllib.request.urlopen(request) as response:
                return json.loads(response.read())
        except (urllib.error.URLError, json.JSONDecodeError, KeyError) as e:
            raise RuntimeError(f"Failed run DataCite query: {e}")
    
    def get_record(self, item: dict) -> ResearchOutputItem:
        attributes = item.get("attributes", {})
        publisher_attr = attributes.get("publisher", {})
        versionCount = 0 if attributes.get("versionCount", {}) is None else int(attributes.get("versionCount", {}))
        versionOfCount = 0 if attributes.get("versionOfCount", {}) is None else int(attributes.get("versionOfCount", {}))

        record = ResearchOutputItem(
            doi=attributes.get("doi"),
            dataCiteClientId=item["relationships"]["client"]["data"]["id"],
            resourceType=attributes.get("types", None).get("resourceTypeGeneral"),
            publisher=publisher_attr.get("name"),
            publicationYear=attributes.get("publicationYear"),
            title=item["attributes"]["titles"][0]["title"],
            inDataCite=True,
            dataCiteCitationCount=attributes.get("citationCount", None),
            dataCiteReferenceCount=attributes.get("referenceCount", None),
            dataCiteViewCount=attributes.get("viewCount", None),
            dataCiteDownloadCount=attributes.get("downloadCount", None),
            titleWordCount=string_word_count(item["attributes"]["titles"][0]["title"])
        )

        if record.resourceType is None or record.resourceType == "":
            record.resourceType = attributes.get("types", {}).get("citeproc")
        if record.resourceType is None or record.resourceType == "":
            record.resourceType = attributes.get("types", {}).get("bibtex")
            

        record.isPublisher = (
            publisher_attr.get("publisherIdentifier") == self.ror or 
            match_patterns(publisher_attr.get("name"), self.name)
        )

        related = [
            r for r in item["attributes"].get("relatedIdentifiers", [])
            if (r.get("relationType") == "IsReferencedBy" or r.get("relationType") == "IsSupplementTo" or r.get("relationType") == "IsSourceOf") and r.get("relatedIdentifierType") == "DOI"
        ]
        if related and len(related) > 0:
            record.referencedByDoi = json.dumps([r.get("relatedIdentifier") for r in related])
        else:
            record.referencedByDoi = None

        record.createdAt = str(attributes.get("created", "") or "")

        record.updatedAt = max([
            str(attributes.get("updated", "") or ""),
            str(attributes.get("created", "") or ""),
            str(attributes.get("registered", "") or "")
        ])

        for relation in attributes.get("relatedIdentifiers", []):
            if relation.get("relationType") == "IsPreviousVersionOf":
                record.isLatestVersion = False
            if relation.get("relationType") == "HasVersion":
                record.isLatestVersion = False

        record.isConceptDoi = (
            versionCount > 0 and
            versionOfCount == 0   
        )

        record.haveCreatorAffiliation = self.check_agent_list_match(attributes.get("creators", []))
        record.haveContributorAffiliation = self.check_agent_list_match(attributes.get("contributors", []))
        return record

    def check_agent_list_match(self, items: list) -> bool:
        partial_ror = self.ror.split("https://ror.org/")[1] if self.ror else ""
        for agent in items:
            # Check if any nameIdentifier matches the ror
            if any(identifier.get("nameIdentifier") == self.ror for identifier in agent.get("nameIdentifiers", [])):
                return True
            # Check if any nameIdentifier matches the partial ror
            if any(identifier.get("nameIdentifier") == partial_ror for identifier in agent.get("nameIdentifiers", [])):
                return True
            # Check if the agent name matches any pattern
            if match_patterns(agent.get("name"), self.name):
                return True
            # Check each affiliation
            for affiliation in agent.get("affiliation", []):
                if (affiliation.get("affiliationIdentifier") == self.ror or 
                        match_patterns(affiliation.get("name"), self.name)):
                    return True
        return False

    def all(self) -> list:
        result = []
        url = self.api_request_url()
        while True:
            response = self.get_api_result(url)
            result.extend(response["data"])
            logging.info(f"Retrieved DataCite {len(result)} of {response['meta']['total']}")
            if response['links'].get('next'):
                url = response['links']['next']
            else:
                break
        return result

    def count(self) -> int:
        if not self.get_query_string():
            return 0
        url = self.api_request_url(page_size=0)
        return self.get_api_result(url)["meta"]["total"]