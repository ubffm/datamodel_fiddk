from pathlib import Path

from fiddk_validator.validator import validate


def test_two_pref_labels_without_lang_tag_fails(tmp_path: Path) -> None:
    data = """
    @prefix ex:   <http://example.org/> .
    @prefix skos: <http://www.w3.org/2004/02/skos/core#> .

    ex:c a skos:Concept ;
        skos:prefLabel "Label 1" ;
        skos:prefLabel "Label 2" .
    """
    data_path = tmp_path / "concept_no_lang.ttl"
    data_path.write_text(data, encoding="utf-8")

    conforms, _results_graph, results_text = validate(
        data_path=data_path,
        shacl_path=None,
        inference="none",
        advanced=False,
        debug=False,
    )

    assert conforms is False, f"Erwartet: nicht konform (2 prefLabel ohne Sprach-Tag).\nReport:\n{results_text}"


def test_two_pref_labels_same_language_tag_fails(tmp_path: Path) -> None:
    data = """
    @prefix ex:   <http://example.org/> .
    @prefix skos: <http://www.w3.org/2004/02/skos/core#> .

    ex:c a skos:Concept ;
        skos:prefLabel "Label 1"@de ;
        skos:prefLabel "Label 2"@de .
    """
    data_path = tmp_path / "concept_same_lang.ttl"
    data_path.write_text(data, encoding="utf-8")

    conforms, _results_graph, results_text = validate(
        data_path=data_path,
        shacl_path=None,
        inference="none",
        advanced=False,
        debug=False,
    )

    assert conforms is False, f"Erwartet: nicht konform (2 prefLabel mit de-Sprach-Tag).\nReport:\n{results_text}"
