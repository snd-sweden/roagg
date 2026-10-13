from dataclasses import dataclass

@dataclass
class ResearchOutputItem:
    doi: str
    publicationYear: int = None
    resourceType: str = None
    title: str = None
    publisher: str = None
    createdAt: str = ""
    updatedAt: str = "" 
    isPublisher: bool = False
    isFunder: bool = None
    haveCreatorAffiliation: bool = False
    haveContributorAffiliation: bool = False
    isLatestVersion: bool = True
    isConceptDoi: bool = False
    #match on ROR
    matchPublisherRor: bool = False
    matchCreatorAffiliationRor: bool = False
    matchContributorAffiliationRor: bool = False
    matchFunderRor: bool = False
    #match on free text in name
    matchPublisherName: bool = False
    matchCreatorName: bool = False
    matchContributorName: bool = False
    matchFunderName: bool = False
    #where was the match found
    inDataCite: bool = None
    inOpenAire: bool = None
    inOpenAlex: bool = None
    inCrossRef: bool = None
    #datacite specific
    dataCiteResourceType: str = None
    dataCiteClientId: str = None
    dataCiteClientName: str = None
    dataCiteCitationCount: int = None
    dataCiteReferenceCount: int = None
    dataCiteViewCount: int = None
    dataCiteDownloadCount: int = None
    #openaire specific
    openAireResourceType: str = None
    openAireBestAccessRight: str = None
    openAireIndicatorsUsageCountsDownloads: int = None
    openAireIndicatorsUsageCountsViews: int = None
    openAireId: str = None
    #openalex specific
    openAlexResourceType: str = None
    openAlexId: str = None
    openAlexCitedByCount: int = None
    openAlexReferencedWorksCount: int = None
    #crossref specific
    crossRefResourceType: str = None
    crossRefReferenceCount: int = None
    crossRefIsReferencedByCount: int = None
    #extra fields
    titleWordCount: int = None
    referencedByDoi: str = None
    conceptDoi: str = None
