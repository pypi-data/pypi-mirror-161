from hestia_earth.schema import SchemaType
from hestia_earth.utils.api import download_hestia
from hestia_earth.utils.model import linked_node
from hestia_earth.utils.tools import non_empty_value

from . import _term_id, _include_methodModel


def _new_emission(term, model=None):
    node = {'@type': SchemaType.EMISSION.value}
    node['term'] = linked_node(term if isinstance(term, dict) else download_hestia(_term_id(term)))
    return _include_methodModel(node, model)


def _default_emission(model: str, term_id: str, data: dict, returns_data: dict):
    node_type = data.get('@type', data.get('type'))
    return_data = returns_data.get('Emission', [{"value": [0]}])[0]
    # need to keep only keys with a value
    return_data = {k: v for k, v in return_data.items() if non_empty_value(v)}
    return [{
        **_new_emission(term_id, model),
        **return_data,
        'value': [0]
    }] if node_type != SchemaType.TRANSFORMATION.value else []
