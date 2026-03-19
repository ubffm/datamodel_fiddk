import argparse
import sys

from .validator import validate_to_files


def main(argv: list[str] | None = None) -> None:
  parser = argparse.ArgumentParser(
    description="SHACL-Validierung für FID-Daten (pySHACL).",
  )
  parser.add_argument("-d", "--data", required=True, help="Pfad zur RDF-Datendatei")
  parser.add_argument("-s", "--shapes", default=None, help="Pfad zur SHACL-Shape-Datei (Standard: eingepackte Shapes)")
  parser.add_argument("-r", "--report", default="shacl-report.ttl", help="Pfad zum Report (RDF)")
  parser.add_argument("--data-format", help="Format der Daten (z. B. turtle, xml, json-ld)")
  parser.add_argument("--shapes-format", help="Format der Shapes")
  parser.add_argument("--report-format", help="Format des Reports (Standard: aus Endung)")
  parser.add_argument(
    "--inference",
    choices=["none", "rdfs", "owlrl"],
    default="rdfs",
    help="Inferenztiefe für pySHACL",
  )
  parser.add_argument("--no-text", action="store_true", help="Keinen Text-Report erzeugen (.txt)")

  args = parser.parse_args(argv)

  conforms = validate_to_files(
    data_path=args.data,
    shacl_path=args.shapes,
    report_path=args.report,
    data_format=args.data_format,
    shacl_format=args.shapes_format,
    report_format=args.report_format,
    inference=args.inference,
    advanced=False,
    debug=False,
    write_text_report=not args.no_text,
  )

  print(f"Konform: {'ja' if conforms else 'nein'}")
  sys.exit(0 if conforms else 2)
