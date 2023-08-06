# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['featurestorebundle',
 'featurestorebundle.attribute',
 'featurestorebundle.checkpoint',
 'featurestorebundle.databricks',
 'featurestorebundle.databricks.feature.reader',
 'featurestorebundle.databricks.feature.writer',
 'featurestorebundle.db',
 'featurestorebundle.delta',
 'featurestorebundle.delta.feature',
 'featurestorebundle.delta.feature.filter',
 'featurestorebundle.delta.feature.reader',
 'featurestorebundle.delta.feature.writer',
 'featurestorebundle.delta.join',
 'featurestorebundle.delta.metadata',
 'featurestorebundle.delta.metadata.reader',
 'featurestorebundle.delta.metadata.writer',
 'featurestorebundle.delta.target',
 'featurestorebundle.delta.target.reader',
 'featurestorebundle.entity',
 'featurestorebundle.feature',
 'featurestorebundle.feature.reader',
 'featurestorebundle.feature.writer',
 'featurestorebundle.frequency',
 'featurestorebundle.metadata',
 'featurestorebundle.metadata.reader',
 'featurestorebundle.metadata.writer',
 'featurestorebundle.notebook',
 'featurestorebundle.notebook.decorator',
 'featurestorebundle.notebook.decorator.tests',
 'featurestorebundle.notebook.functions',
 'featurestorebundle.notebook.services',
 'featurestorebundle.notebook.tests',
 'featurestorebundle.orchestration',
 'featurestorebundle.target.reader',
 'featurestorebundle.test',
 'featurestorebundle.utils',
 'featurestorebundle.widgets']

package_data = \
{'': ['*'], 'featurestorebundle': ['_config/*']}

install_requires = \
['daipe-core>=1.4.2,<2.0.0',
 'databricks-bundle>=1.4.3,<2.0.0',
 'pyfony-bundles>=0.4.4,<0.5.0']

entry_points = \
{'pyfony.bundle': ['create = '
                   'featurestorebundle.FeatureStoreBundle:FeatureStoreBundle']}

setup_kwargs = {
    'name': 'feature-store-bundle',
    'version': '2.5.2.dev1',
    'description': 'Feature Store for the Daipe AI Platform',
    'long_description': '# Feature Store bundle\n\n**This package is distributed under the "DataSentics SW packages Terms of Use." See [license](https://raw.githubusercontent.com/daipe-ai/feature-store-bundle/master/LICENSE)**\n\nFeature store bundle allows you to store features with metadata.\n',
    'author': 'Datasentics',
    'author_email': 'jiri.koutny@datasentics.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/daipe-ai/feature-store-bundle',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
