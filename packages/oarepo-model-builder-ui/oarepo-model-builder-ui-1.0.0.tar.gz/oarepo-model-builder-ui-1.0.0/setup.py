# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['oarepo_model_builder_ui',
 'oarepo_model_builder_ui.invenio',
 'oarepo_model_builder_ui.model_preprocessors',
 'oarepo_model_builder_ui.outputs']

package_data = \
{'': ['*']}

install_requires = \
['langcodes>=3.3.0', 'oarepo-model-builder>=0.9.24']

entry_points = \
{'oarepo.model_schemas': ['layout_jsonschema = '
                          'oarepo_model_builder_ui:layout_jsonschema.json5',
                          'layout_settings = '
                          'oarepo_model_builder_ui:layout_settings.json5'],
 'oarepo_model_builder.builders': ['1050-layout-data = '
                                   'oarepo_model_builder_ui.invenio.invenio_layout_data:InvenioLayoutBuilder'],
 'oarepo_model_builder.model_preprocessors': ['30-layout = '
                                              'oarepo_model_builder_ui.model_preprocessors.layout_settings:LayoutSettingsPreprocessor'],
 'oarepo_model_builder.outputs': ['layout = '
                                  'oarepo_model_builder_ui.outputs.layout:LayoutOutput']}

setup_kwargs = {
    'name': 'oarepo-model-builder-ui',
    'version': '1.0.0',
    'description': '',
    'long_description': '# OARepo Model Builder UI\n\n',
    'author': 'Alzbeta Pokorna',
    'author_email': 'alzbeta.pokorna@cesnet.cz',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
