import json

from tests.utils import fixtures_path
from hestia_earth.validation.validators.impact_assessment import (
    validate_impact_assessment, validate_linked_cycle_product
)


def test_validate_valid():
    with open(f"{fixtures_path}/impactAssessment/valid.json") as f:
        node = json.load(f)
    assert validate_impact_assessment(node) == [True] * 18


def test_validate_linked_cycle_product_valid():
    with open(f"{fixtures_path}/impactAssessment/cycle/valid.json") as f:
        data = json.load(f)
    assert validate_linked_cycle_product(data, data.get('cycle')) is True


def test_validate_linked_cycle_product_invalid():
    with open(f"{fixtures_path}/impactAssessment/cycle/invalid.json") as f:
        data = json.load(f)
    assert validate_linked_cycle_product(data, data.get('cycle')) == {
        'level': 'error',
        'dataPath': '.product',
        'message': 'should be included in the cycle products',
        'params': {
            'product': {
                '@type': 'Term',
                '@id': 'maizeGrain'
            },
            'node': {
                'type': 'Cycle',
                'id': '3'
            }
        }
    }
