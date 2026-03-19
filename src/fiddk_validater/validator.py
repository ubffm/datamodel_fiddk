from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple, Union

from pyshacl import validate as shacl_validate
from rdflib import Graph
from rdflib.util import guess_format as rdflib_guess_format

Pathish = Union[str, Path]


def _resolve_format(path: Pathish, provided: Optional[str]) -> Optional[str]:
  if provided:
    return provided
  try:
    return rdflib_guess_format(str(path))
  except Exception:
    return None


def validate(
  data_path: Pathish,
  shacl_path: Pathish,
  data_format: Optional[str] = None,
  shacl_format: Optional[str] = None,
  inference: str = "rdfs",
  advanced: bool = False,
  debug: bool = False,
) -> Tuple[bool, Graph, str]:
  data_graph = Graph()
  data_graph.parse(str(data_path), format=_resolve_format(data_path, data_format))

  shacl_graph = Graph()
  shacl_graph.parse(str(shacl_path), format=_resolve_format(shacl_path, shacl_format))

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
  data_format: Optional[str] = None,
  shacl_format: Optional[str] = None,
  report_format: Optional[str] = None,
  inference: str = "rdfs",
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
