import argparse
import sys
from pathlib import Path

from .validator import _resolve_format, validate


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="SHACL-Validierung für FID-Daten (pySHACL).",
    )
    parser.add_argument("-d", "--data", required=True, help="Pfad zur RDF-Datendatei")
    parser.add_argument(
        "-s",
        "--shapes",
        default=None,
        help="Pfad zur SHACL-Shape-Datei (Standard: eingepackte Shapes)",
    )
    parser.add_argument(
        "-r",
        "--report",
        default=None,
        help="Pfad zum Report (RDF); wenn gesetzt, erfolgt keine Ausgabe auf stdout",
    )
    parser.add_argument("--data-format", help="Format der Daten (z. B. turtle, xml, json-ld)")
    parser.add_argument("--shapes-format", help="Format der Shapes")
    parser.add_argument("--report-format", help="Format des Reports (Standard: aus Endung)")
    parser.add_argument(
        "--inference",
        choices=["none", "rdfs", "owlrl"],
        default="none",
        help="Inferenztiefe für pySHACL",
    )
    parser.add_argument("--no-text", action="store_true", help="Keinen Text-Report erzeugen (.txt)")

    args = parser.parse_args(argv)

    # Validierung ausführen, damit wir bei Bedarf den Text-Report direkt ausgeben können.
    conforms, results_graph, results_text = validate(
        data_path=args.data,
        shacl_path=args.shapes,
        data_format=args.data_format,
        shacl_format=args.shapes_format,
        inference=args.inference,
        advanced=False,
        debug=False,
    )

    # Report schreiben nur, wenn -r/--report angegeben ist; dann keine Ausgabe auf stdout
    if args.report:
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        rfmt = args.report_format or _resolve_format(report_path, None) or "turtle"
        serialized = results_graph.serialize(format=rfmt)
        if isinstance(serialized, bytes):
            serialized = serialized.decode("utf-8")
        report_path.write_text(serialized, encoding="utf-8")
        if not args.no_text:
            report_path.with_suffix(".txt").write_text(results_text, encoding="utf-8")
    else:
        if conforms:
            print("Konform: ja")
        else:
            print("Konform: nein")
            print("\nSHACL-Report (Kurzfassung):")
            print(results_text)

    sys.exit(0 if conforms else 2)
