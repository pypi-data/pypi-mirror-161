# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['graphdna',
 'graphdna.detectors',
 'graphdna.entities',
 'graphdna.entities.interfaces',
 'graphdna.heuristics',
 'graphdna.heuristics.gql_queries',
 'graphdna.heuristics.web_properties']

package_data = \
{'': ['*']}

install_requires = \
['JSON-log-formatter>=0.5.1,<0.6.0', 'aiohttp[speedups]>=3.8.1,<4.0.0']

entry_points = \
{'console_scripts': ['graphdna = graphdna:cli']}

setup_kwargs = {
    'name': 'graphdna',
    'version': '1.1.0',
    'description': 'Fast and powerful GraphQL engine fingerprinting tool',
    'long_description': '# GraphDNA ![PyPI](https://img.shields.io/pypi/v/GraphDNA) [![CI](https://github.com/Escape-Technologies/GraphDNA/actions/workflows/ci.yaml/badge.svg)](https://github.com/Escape-Technologies/GraphDNA/actions/workflows/ci.yaml) [![CD](https://github.com/Escape-Technologies/GraphDNA/actions/workflows/cd.yaml/badge.svg)](https://github.com/Escape-Technologies/GraphDNA/actions/workflows/cd.yaml)\n\nGraphDNA is a tool that uses multiple heuristics to fingerprint GraphQL endpoints.\n\n![Banner](docs/banner.png)\n\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/GraphDNA)\n![PyPI - Downloads](https://img.shields.io/pypi/dm/GraphDNA)\n\n## Getting Started\n\nIt takes only two simple steps to fingerprint an endpoint using GraphDNA.\n\n```bash\npip install graphdna\ngraphdna -u https://example.com/graphql\n```\n\nThe full list of supported engines is accessible [here](https://github.com/Escape-Technologies/GraphDNA/blob/main/graphdna/entities/engines.py).\n\n![Banner](docs/hackerone.png)\n\n## Documentation\n\n```python\nimport logging\nfrom typing import Dict, Optional\n\nfrom graphdna import detect_engine, detect_engine_async\nfrom graphdna.entities import GraphQLEngine\n\ndef detect_engine(\n    url: str,\n    headers: Optional[Dict[str, str]] = None,\n    logger: Optional[logging.Logger] = None,\n) -> Optional[GraphQLEngine]:\n    ...\n\n\nasync def detect_engine_async(\n    url: str,\n    headers: Optional[Dict[str, str]] = None,\n    logger: Optional[logging.Logger] = None,\n) -> Optional[GraphQLEngine]:\n    ...\n```\n\n## Environment Variables\n\n**Logger** - *No effect if you pass your own logger*\n| Name | Values  | Default| Behavior|\n|------|--------|--------|--------|\n| `LOG_FORMAT` | `console`, `json` | `console` | Change the log format accordingly |\n| `DEBUG` | `True`, `False` | `False` | Enable debug logging |\n\n## Local installation\n\n```bash\ngit clone git@github.com:Escape-Technologies/GraphDNA.git\ncd GraphDNA\nchmod +x ./install-dev.sh\n./install-dev.sh\n```\n\n## Credits\n\n* [Graphw00f](https://github.com/dolevf/graphw00f)\n* [Dolev Farhi](https://github.com/dolevf)\n\n## Contributing\n\nPull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.\n\nPlease make sure to update tests as appropriate.\n\n## License ![PyPI - License](https://img.shields.io/pypi/l/GraphDNA)\n\n[MIT](https://choosealicense.com/licenses/mit/)\n',
    'author': 'Escape Technologies SAS',
    'author_email': 'ping@escape.tech',
    'maintainer': 'Swan',
    'maintainer_email': 'swan@escape.tech',
    'url': 'https://escape.tech/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<=3.11',
}


setup(**setup_kwargs)
