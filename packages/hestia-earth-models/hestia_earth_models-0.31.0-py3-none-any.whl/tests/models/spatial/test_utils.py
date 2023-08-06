from hestia_earth.models.spatial.utils import get_region_factor


def test_get_region_factor():
    site = {'country': {'@id': 'GADM-ALB'}}
    assert get_region_factor('croppingIntensity', site) == 1.7893
