from app.services.breach_client import _parse_leakcheck_sources


def test_parse_leakcheck_sources_dedupes():
    sources = [
        {"name": "Avito.ru", "date": "2016-11"},
        {"name": "Avito.ru", "date": "2016-11"},
        {"name": "Litres.ru", "date": "2023-08"},
    ]
    breaches = _parse_leakcheck_sources(sources)
    assert len(breaches) == 2
    assert breaches[0].title == "Avito.ru"
    assert breaches[0].breach_date == "2016-11-01"
