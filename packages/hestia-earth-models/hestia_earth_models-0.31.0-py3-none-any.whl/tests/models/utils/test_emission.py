from unittest.mock import patch
from tests.utils import TERM, fake_new_emission

from hestia_earth.models.utils.emission import _new_emission, _default_emission

class_path = 'hestia_earth.models.utils.emission'


@patch(f'{class_path}._include_methodModel', side_effect=lambda n, x: n)
@patch(f'{class_path}.download_hestia', return_value=TERM)
def test_new_emission(*args):
    # with a Term as string
    emission = _new_emission('term')
    assert emission == {
        '@type': 'Emission',
        'term': TERM
    }

    # with a Term as dict
    emission = _new_emission(TERM)
    assert emission == {
        '@type': 'Emission',
        'term': TERM
    }


@patch(f"{class_path}._new_emission", side_effect=fake_new_emission)
def test_default_emission(*args):
    returns_data = {
        'Emission': [{
            'sd': '',
            'statsDefinition': 'modelled'
        }]
    }
    assert _default_emission('model', 'id', {}, returns_data)[0] == {
        '@type': 'Emission',
        'term': {
            '@type': 'Term',
            '@id': 'id'
        },
        'methodModel': {
            '@type': 'Term',
            '@id': 'model'
        },
        'value': [0],
        'statsDefinition': 'modelled'
    }
    # Transformation should not return an emission
    assert _default_emission('model', 'id', {'@type': 'Transformation'}, {}) == []
