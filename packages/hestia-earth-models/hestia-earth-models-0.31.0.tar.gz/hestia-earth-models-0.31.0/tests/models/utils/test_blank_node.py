from hestia_earth.schema import SiteSiteType

from hestia_earth.models.utils.blank_node import _run_required


def test_run_required():
    assert not _run_required('model', 'ch4ToAirAquacultureSystems', {
        'site': {'siteType': SiteSiteType.CROPLAND.value}
    })
    assert _run_required('model', 'ch4ToAirAquacultureSystems', {
        'site': {'siteType': SiteSiteType.POND.value}
    }) is True
