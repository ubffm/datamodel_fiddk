from __future__ import annotations

from importlib import resources
from pathlib import Path

from pyshacl import validate as shacl_validate
from rdflib import Graph
from rdflib.util import guess_format as rdflib_guess_format

Pathish = str | Path


def _resolve_format(path: Pathish, provided: str | None) -> str | None:
  if provided:
    return provided
  try:
    return rdflib_guess_format(str(path))
  except Exception:
    return None


def validate(
  data_path: Pathish,
  shacl_path: Pathish | None = None,
  data_format: str | None = None,
  shacl_format: str | None = None,
  inference: str = "none",
  advanced: bool = False,
  debug: bool = False,
) -> tuple[bool, Graph, str]:
  data_graph = Graph()
  data_graph.parse(str(data_path), format=_resolve_format(data_path, data_format))

  shacl_graph = Graph()
  if shacl_path is None:
    shapes_dir = resources.files("fiddk_validator").joinpath("shapes")
    loaded = False
    if shapes_dir.is_dir():
      for entry in shapes_dir.iterdir():
        if entry.is_file() and entry.name.endswith(".ttl"):
          shacl_graph.parse(data=entry.read_text(encoding="utf-8"), format="turtle")
          loaded = True
    else:
      entry = resources.files("fiddk_validator").joinpath("shapes").joinpath("fiddk.ttl")
      if entry.is_file():
        shacl_graph.parse(data=entry.read_text(encoding="utf-8"), format="turtle")
        loaded = True
    if not loaded:
      raise FileNotFoundError("Eingepackte SHACL-Shapes wurden nicht gefunden.")
  else:
    spath = Path(shacl_path)
    if spath.is_dir():
      for entry in spath.iterdir():
        if entry.is_file():
          fmt = _resolve_format(entry, shacl_format) or rdflib_guess_format(entry.name) or "turtle"
          shacl_graph.parse(str(entry), format=fmt)
    else:
      shacl_graph.parse(str(spath), format=_resolve_format(spath, shacl_format))

  conforms, results_graph, results_text = shacl_validate(
    data_graph=data_graph,
    shacl_graph=shacl_graph,
    inference=inference,
    advanced=advanced,
    debug=debug,
  )
  return bool(conforms), results_graph, str(results_text)


def validate_to_files(
  data_path: Pathish,
  shacl_path: Pathish,
  report_path: Pathish,
  data_format: str | None = None,
  shacl_format: str | None = None,
  report_format: str | None = None,
  inference: str = "none",
  advanced: bool = False,
  debug: bool = False,
  write_text_report: bool = True,
) -> bool:
  conforms, results_graph, results_text = validate(
    data_path=data_path,
    shacl_path=shacl_path,
    data_format=data_format,
    shacl_format=shacl_format,
    inference=inference,
    advanced=advanced,
    debug=debug,
  )
  report_path = Path(report_path)
  report_path.parent.mkdir(parents=True, exist_ok=True)
  fmt = report_format or _resolve_format(report_path, None) or "turtle"
  serialized = results_graph.serialize(format=fmt)
  if isinstance(serialized, bytes):
    serialized = serialized.decode("utf-8")
  report_path.write_text(serialized, encoding="utf-8")
  if write_text_report:
    Path(report_path).with_suffix(".txt").write_text(results_text, encoding="utf-8")
  return conforms
