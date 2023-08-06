from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_new_practice

from hestia_earth.models.koble2014.residue import MODEL, run, _should_run

class_path = f"hestia_earth.models.{MODEL}.residue"
fixtures_folder = f"{fixtures_path}/{MODEL}/residue"


@patch(f"{class_path}.find_primary_product")
def test_should_run(mock_primary_product):
    # no primary product => no run
    mock_primary_product.return_value = None
    assert not _should_run({})

    # with primary product => run
    mock_primary_product.return_value = {}
    assert _should_run({}) is True


@patch(f"{class_path}._run_required", return_value=True)
@patch(f"{class_path}._new_practice", side_effect=fake_new_practice)
def test_run(*args):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected
