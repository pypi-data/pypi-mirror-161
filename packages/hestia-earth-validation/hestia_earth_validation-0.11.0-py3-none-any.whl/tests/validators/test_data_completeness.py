import json

from hestia_earth.schema import SiteSiteType, TermTermType

from tests.utils import fixtures_path
from hestia_earth.validation.validators.data_completeness import (
    validate_dataCompleteness, _validate_all_values, _validate_cropland
)


def test_validate_dataCompleteness_valid():
    with open(f"{fixtures_path}/dataCompleteness/valid.json") as f:
        data = json.load(f)
    assert validate_dataCompleteness(data) is True


def test_validate_all_values_valid():
    with open(f"{fixtures_path}/dataCompleteness/valid.json") as f:
        data = json.load(f)
    assert _validate_all_values(data) is True


def test_validate_all_values_warning():
    with open(f"{fixtures_path}/dataCompleteness/all-values/warning.json") as f:
        data = json.load(f)
    assert _validate_all_values(data) == {
        'level': 'warning',
        'dataPath': '.dataCompleteness',
        'message': 'may not all be set to false'
    }


def test_validate_cropland_valid():
    with open(f"{fixtures_path}/dataCompleteness/cropland/site.json") as f:
        site = json.load(f)
    with open(f"{fixtures_path}/dataCompleteness/cropland/valid.json") as f:
        data = json.load(f)
    assert _validate_cropland(data, site) is True

    # also works if siteType is not cropland
    site['siteType'] = SiteSiteType.LAKE.value
    data[TermTermType.EXCRETAMANAGEMENT.value] = False
    assert _validate_cropland(data, site) is True


def test_validate_cropland_warning():
    with open(f"{fixtures_path}/dataCompleteness/cropland/site.json") as f:
        site = json.load(f)
    with open(f"{fixtures_path}/dataCompleteness/cropland/warning.json") as f:
        data = json.load(f)
    assert _validate_cropland(data, site) == [
        {
            'level': 'warning',
            'dataPath': '.dataCompleteness.animalFeed',
            'message': 'should be true for site of type cropland'
        },
        {
            'level': 'warning',
            'dataPath': '.dataCompleteness.excretaManagement',
            'message': 'should be true for site of type cropland'
        }
    ]
