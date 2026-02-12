# Research output aggregator 

The goal of this project is to create a script to get a summarization for a research organization about the research output.  
First target is to query and process information from DataCite.  

The goal for this script is to create a list over research output where an organization is mentioned as:
* publisher
* creator with affiliation to the organization
* contributor with affiliation to the organization

Input: ROR-id and list of variants on the organization name.

## Properties to collect for each research output

Roagg collects a fiew fields for each resource found and do de-duplications based on the DOI found in each source.

<details>

<summary>List of all properties in the aggregated results</summary>

|Field                                 |Type   |Comment                                                                                |
|--------------------------------------|-------|---------------------------------------------------------------------------------------|
|publicationYear                       |integer|The year of publication, can be empty in some cases                                    |
|resourceType                          |string |The resource type (free text string)                                                   |
|title                                 |string |Title of the resource (first one if multiple)                                          |
|publisher                             |string |Publisher (free text)                                                                  |
|createdAt                             |string |Created date if available                                                              |
|updatedAt                             |string |Updatade date if availible                                                             |
|isPublisher                           |bool   |True if the the publisher match the requested organisation                             |
|isFunder                              |bool   |True if the the funder match the requested organisation                                |
|haveCreatorAffiliation                |bool   |True if the the any creator match the requested organisation                           |
|haveContributorAffiliation            |bool   |True if the the any contributor match the requested organisation                       |
|isLatestVersion                       |bool   |True if the DataCite metadata indicates this beeing the latest version                 |
|isConceptDoi                          |bool   |True if the DataCite metadata indicates this beeing a concept DOI                      |
|matchPublisherRor                     |bool   |True if the ROR id for publisher match the ROR in the provided argument                |
|matchCreatorAffiliationRor            |bool   |True if the ROR id for a creator affiliation match the ROR in the provided argument    |
|matchContributorAffiliationRor        |bool   |True if the ROR id for a contributor affiliation match the ROR in the provided argument|
|matchFunderRor                        |bool   |True if the ROR id for funder match the ROR in the provided argument                   |
|matchPublisherName                    |bool   |True if any of the names supplied matches the publisher name in the resource           |
|matchCreatorName                      |bool   |True if any of the names supplied matches the creator name in the resource             |
|matchContributorName                  |bool   |True if any of the names supplied matches the contributor name in the resource         |
|matchFunderName                       |bool   |True if any of the names supplied matches the funder name in the resource              |
|inDataCite                            |bool   |True if the DOI was matched in the DataCite                                            |
|inOpenAire                            |bool   |True if the DOI was matched in OpenAire                                                |
|inOpenAlex                            |bool   |True if the DOI was matched in OpenAlex                                                |
|inCrossRef                            |bool   |True if the DOI was matched in CrossRef                                                |
|dataCiteClientId                      |string |The client id for the organisation minting the DOI                                     |
|dataCiteClientName                    |string |The human readable name of the minting organisation                                    |
|dataCiteCitationCount                 |integer|Citation count for the resource provided by the DataCite API                           |
|dataCiteReferenceCount                |integer|Reference count for the resource provided by the DataCite API                          |
|dataCiteViewCount                     |integer|View count for the resource provided by the DataCite API                               |
|dataCiteDownloadCount                 |integer|Download count for the resource provided by the DataCite API                           |
|openAireBestAccessRight               |string |Access Rights for the resource indicated indicated by the OpenAire API                 |
|openAireIndicatorsUsageCountsDownloads|integer|Download count for the resource indicated by the OpenAire API                          |
|openAireIndicatorsUsageCountsViews    |integer|View count for the resource provided by the OpenAire API                               |
|openAireId                            |string |Id for the resource in OpenAire                                                        |
|openAlexId                            |string |Id for the resource in OpenAlex                                                        |
|openAlexCitedByCount                  |integer|Citation count for the resource provided by the OpenAlex API                           |
|openAlexReferencedWorksCount          |integer|Reference count for the resource provided by the OpenAlex API                          |
|titleWordCount                        |integer|Number of words in the title (useful for sorting in some cases)                        |
|referencedByDoi                       |string |DOI of object(s) (for instance papers) referencing this object (JSON list)                                                                                       |

</details>

## Install
`pip install roagg`

## Run
List arguments:  
`roagg --help`  

## Install dev
`git clone git@github.com:snd-sweden/roagg.git`  
`cd roagg`  
`pip install -e .`  

## Tests
Some tests are available, to run them:  
`python -m pytest`

## Development stuff to do
- [x] ROR get name variants from ROR
- [x] CLI add options to get name list from txt
- [x] DataCite API build query for matching publisher and affiliation
- [x] Publish as cmd tool on PyPI
- [ ] Crossref API build query for matching publisher and affiliation

### Some example arguments
Chalmers with ror and name list:  
```bash
roagg --ror https://ror.org/040wg7k59 --name-txt tests/name-lists/chalmers.txt --output chalmers.csv
```

GU with ror, name list and extra name not in the text file:  
```bash
roagg --name "Department of Nephrology Gothenburg" --ror https://ror.org/01tm6cn81 --name-txt tests/name-lists/gu.txt --output data/gu.csv
```

KTH with ror and name list:  
```bash
roagg --ror https://ror.org/026vcq606 --name-txt tests/name-lists/kth.txt --output data/kth.csv
```

KAU with ror:  
```bash
roagg --ror https://ror.org/05s754026 --output kau.csv
```

## License
[MIT License](LICENSE)
