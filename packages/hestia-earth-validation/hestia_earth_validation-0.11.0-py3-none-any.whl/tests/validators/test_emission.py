import json

from tests.utils import fixtures_path
from hestia_earth.validation.validators.emission import validate_linked_terms


def test_validate_linked_terms_valid():
    # no emissions should be valid
    assert validate_linked_terms({}, 'emissions', 'inputs', 'inputs') is True

    with open(f"{fixtures_path}/emission/linked-terms/inputs/valid.json") as f:
        data = json.load(f)
    assert validate_linked_terms(data, 'emissions', 'inputs', 'inputs') is True

    with open(f"{fixtures_path}/emission/linked-terms/transformation/valid.json") as f:
        data = json.load(f)
    assert validate_linked_terms(data, 'emissions', 'transformation', 'transformations') is True


def test_validate_linked_terms_invalid():
    with open(f"{fixtures_path}/emission/linked-terms/inputs/invalid.json") as f:
        data = json.load(f)
    assert validate_linked_terms(data, 'emissions', 'inputs', 'inputs', True) == {
        'level': 'warning',
        'dataPath': '.emissions[1]',
        'message': 'should add the linked inputs to the cycle',
        'params': {
            'term': {
                '@type': 'Term',
                '@id': 'ch4ToAirEntericFermentation',
                'termType': 'emission'
            },
            'expected': [
                {
                    '@id': 'seed',
                    '@type': 'Term',
                    'name': 'Seed',
                    'termType': 'other'
                }
            ]
        }
    }

    with open(f"{fixtures_path}/emission/linked-terms/transformation/error.json") as f:
        data = json.load(f)
    assert validate_linked_terms(data, 'emissions', 'transformation', 'transformations') == {
        'level': 'error',
        'dataPath': '.emissions[1]',
        'message': 'must add the linked transformations to the cycle',
        'params': {
            'term': {
                '@type': 'Term',
                '@id': 'ch4ToAirEntericFermentation',
                'termType': 'emission'
            },
            'expected': {
                '@id': 'compostingInVessel',
                '@type': 'Term',
                'name': 'Composting - In Vessel',
                'termType': 'excretaManagement'
            }
        }
    }

    with open(f"{fixtures_path}/emission/linked-terms/transformation/warning.json") as f:
        data = json.load(f)
    assert validate_linked_terms(data, 'emissions', 'transformation', 'transformations') == {
        'level': 'error',
        'dataPath': '.emissions[1]',
        'message': 'must add the linked transformations to the cycle',
        'params': {
            'term': {
                '@type': 'Term',
                '@id': 'ch4ToAirEntericFermentation',
                'termType': 'emission'
            },
            'expected': {
                '@id': 'compostingInVessel',
                '@type': 'Term',
                'name': 'Composting - In Vessel',
                'termType': 'excretaManagement'
            }
        }
    }
