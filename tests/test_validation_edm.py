import sys
from pathlib import Path

# Sicherstellen, dass das src-Verzeichnis im sys.path ist (für Imports ohne Installation)
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from fiddk_validator.validator import validate  # noqa: E402


def test_valid_minimal_conforms():
    data_path = ROOT / "tests" / "data" / "edm" / "valid" / "minimal.ttl"
    conforms, _, _ = validate(data_path=data_path, inference="rdfs")
    assert conforms is True


def test_valid_rich_conforms():
    data_path = ROOT / "tests" / "data" / "edm" / "valid" / "rich.ttl"
    conforms, _, _ = validate(data_path=data_path, inference="rdfs")
    assert conforms is True


def test_invalid_missing_required_not_conform():
    data_path = ROOT / "tests" / "data" / "edm" / "invalid" / "missing_required.ttl"
    conforms, _, _ = validate(data_path=data_path, inference="rdfs")
    assert conforms is False
