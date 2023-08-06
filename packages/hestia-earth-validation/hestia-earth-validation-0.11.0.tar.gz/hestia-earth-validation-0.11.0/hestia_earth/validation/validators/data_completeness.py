from hestia_earth.schema import SiteSiteType

from hestia_earth.validation.utils import _filter_list_errors


def _validate_cropland(data_completeness: dict, site: dict):
    validate_keys = [
        'animalFeed',
        'excretaManagement'
    ]
    site_type = site.get('siteType')

    def validate_key(key: str):
        return data_completeness.get(key) is True or {
            'level': 'warning',
            'dataPath': f".dataCompleteness.{key}",
            'message': f"should be true for site of type {site_type}"
        }

    return site_type != SiteSiteType.CROPLAND.value or _filter_list_errors(map(validate_key, validate_keys))


def _validate_all_values(data_completeness: dict):
    values = data_completeness.values()
    return next((value for value in values if isinstance(value, bool) and value is True), False) or {
        'level': 'warning',
        'dataPath': '.dataCompleteness',
        'message': 'may not all be set to false'
    }


def validate_dataCompleteness(data_completeness: dict, site=None):
    return _filter_list_errors([
        _validate_all_values(data_completeness),
        _validate_cropland(data_completeness, site) if site else True
    ])
