from pathlib import Path

import luigi

from fiddk_validator.luigi_tasks import ValidateRDFTask


def test_validate_rdf_task_valid_dataset_creates_reports_and_succeeds(tmp_path: Path) -> None:
    # Arrange: Eingabedaten (gültiges Minimalbeispiel) und Shapes-Verzeichnis
    data_path = Path(__file__).parent / "data" / "edm" / "valid" / "minimal.ttl"
    shacl_path = Path(__file__).resolve().parents[1] / "src" / "fiddk_validator" / "shapes"
    report_path = tmp_path / "report.ttl"

    assert data_path.is_file(), f"Testdatendatei fehlt: {data_path}"
    assert shacl_path.is_dir(), f"Shapes-Verzeichnis fehlt: {shacl_path}"

    # Act: Luigi-Task ausführen
    task = ValidateRDFTask(
        data_path=str(data_path),
        shacl_path=str(shacl_path),
        report_path=str(report_path),
        inference="rdfs",
        write_text_report=True,
        fail_on_violation=True,
    )

    success = luigi.build([task], workers=1, local_scheduler=True)

    # Assert: Erfolgreiche Ausführung und erzeugte Reports
    assert success is True, "Luigi-Task sollte erfolgreich sein (konforme Daten)."
    assert report_path.exists() and report_path.stat().st_size > 0, "RDF-Report wurde nicht erstellt."

    # Text-Report: Implementierungen verwenden entweder <basename>.txt oder <basename>.<rdf-suffix>.txt
    txt_candidate1 = report_path.with_suffix(".txt")  # z. B. report.txt
    txt_candidate2 = Path(str(report_path) + ".txt")  # z. B. report.ttl.txt
    assert txt_candidate1.exists() or txt_candidate2.exists(), "Text-Report (.txt) wurde nicht erstellt."
