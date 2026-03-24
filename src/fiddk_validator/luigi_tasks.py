from __future__ import annotations

from pathlib import Path

import luigi

from .validator import _resolve_format, validate


class ValidateRDFTask(luigi.Task):
    data_path = luigi.Parameter()
    shacl_path = luigi.OptionalParameter(default=None)
    report_path = luigi.Parameter()
    data_format = luigi.OptionalParameter(default=None)
    shacl_format = luigi.OptionalParameter(default=None)
    report_format = luigi.OptionalParameter(default=None)
    inference = luigi.Parameter(default="rdfs")
    advanced = luigi.BoolParameter(default=False)
    debug = luigi.BoolParameter(default=False)
    write_text_report = luigi.BoolParameter(default=True)
    fail_on_violation = luigi.BoolParameter(default=False)

    def output(self):
        return luigi.LocalTarget(self.report_path)

    def complete(self):
        path = Path(self.report_path)
        if not path.exists():
            return False

        # Ohne strenge Behandlung reicht die Existenz des Outputs.
        if not self.fail_on_violation:
            return True

        # Streng: nur komplett, wenn sh:conforms == true.
        try:
            # Bevorzugt Textreport auswerten
            if self.write_text_report:
                txt = path.with_suffix(".txt")
                if txt.exists():
                    content = txt.read_text(encoding="utf-8").lower()
                    if "conforms: true" in content:
                        return True
                    return False

            # Fallback: RDF-Report parsen und sh:conforms prüfen
            from rdflib import Graph, Namespace
            from rdflib.namespace import RDF

            SH = Namespace("http://www.w3.org/ns/shacl#")

            g = Graph()
            fmt = _resolve_format(path, None) or "turtle"
            g.parse(str(path), format=fmt)

            for rep in g.subjects(RDF.type, SH.ValidationReport):
                for val in g.objects(rep, SH.conforms):
                    try:
                        if bool(val.toPython()):
                            return True
                        return False
                    except Exception:
                        return str(val).strip().lower() == "true"

            # Keine Aussage gefunden → sicherheitshalber nicht komplett
            return False
        except Exception:
            return False

    def run(self):
        conforms, results_graph, results_text = validate(
            data_path=self.data_path,
            shacl_path=self.shacl_path,
            data_format=self.data_format if self.data_format else None,
            shacl_format=self.shacl_format if self.shacl_format else None,
            inference=self.inference,
            advanced=self.advanced,
            debug=self.debug,
        )

        # Zielverzeichnis sicherstellen
        Path(self.output().path).parent.mkdir(parents=True, exist_ok=True)

        rfmt = self.report_format or _resolve_format(self.output().path, None) or "turtle"
        serialized = results_graph.serialize(format=rfmt)
        if isinstance(serialized, bytes):
            serialized = serialized.decode("utf-8")

        with self.output().open("w") as f:
            f.write(serialized)

        if self.write_text_report:
            txt_path = Path(self.output().path).with_suffix(".txt")
            txt_path.write_text(results_text, encoding="utf-8")

        if self.fail_on_violation and not conforms:
            raise RuntimeError("SHACL-Validierung nicht konform.")
