import urllib.parse

from roagg.providers.datacite import DataCiteAPI


def test_publisher_wildcard_preserves_spaces_but_affiliations_escape_them():
    api = DataCiteAPI(name=["Bolin Cent*"])
    assert api.get_query_string() == (
        r"creators.affiliation.name:(Bolin\ Cent*) OR "
        r"contributors.affiliation.name:(Bolin\ Cent*) OR "
        "publisher.name:(Bolin Cent*)"
    )
    params = urllib.parse.parse_qs(urllib.parse.urlsplit(api.api_request_url()).query)
    assert params["query"] == [api.get_query_string()]


def test_publisher_mixed_wildcard_and_exact_names_keep_exact_quotes():
    query = DataCiteAPI(name=["Bolin Cent*", "Exact Institute"]).get_query_string()
    assert 'publisher.name:(Bolin Cent* OR "Exact Institute")' in query
    assert r'creators.affiliation.name:(Bolin\ Cent* OR "Exact Institute")' in query


def test_exact_names_and_ror_query_are_unchanged():
    api = DataCiteAPI(name=["Exact Institute"], ror="https://ror.org/012345678")
    query = api.get_query_string()
    for field in ("creators.affiliation.name", "contributors.affiliation.name", "publisher.name"):
        assert f'{field}:("Exact Institute")' in query
    assert 'publisher.publisherIdentifier:"https://ror.org/012345678"' in query
    assert 'publisher.publisherIdentifier:"012345678"' in query


def test_empty_names_do_not_create_a_name_query():
    assert DataCiteAPI().get_query_string() == ""
