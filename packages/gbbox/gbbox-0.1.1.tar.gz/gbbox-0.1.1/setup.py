# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gbbox']

package_data = \
{'': ['*']}

install_requires = \
['pydantic==1.9.1']

setup_kwargs = {
    'name': 'gbbox',
    'version': '0.1.1',
    'description': 'Simple Python module for calculating bounding box (bbox) from given GeoJSON object',
    'long_description': '## 📐 geojson-bbox\n\nSimple Python module for calculating bounding box (bbox) from given GeoJSON object.\n\nCurrently following GeoJSON objects are supported ([RFC 7946](https://datatracker.ietf.org/doc/html/rfc7946)):\n\n1. [Point](https://datatracker.ietf.org/doc/html/rfc7946#section-3.1.2)\n2. [MultiPoint](https://datatracker.ietf.org/doc/html/rfc7946#section-3.1.3)\n3. [LineString](https://datatracker.ietf.org/doc/html/rfc7946#section-3.1.4)\n4. [MultiLineString](https://datatracker.ietf.org/doc/html/rfc7946#section-3.1.5)\n5. [Polygon](https://datatracker.ietf.org/doc/html/rfc7946#section-3.1.6)\n6. [MultiPolygon](https://datatracker.ietf.org/doc/html/rfc7946#section-3.1.7)\n7. [GeometryCollection](https://datatracker.ietf.org/doc/html/rfc7946#section-3.1.8)\n\n### Installation\n\n```bash\n$ pip install gbbox\n```\n\n### Usage\n\n```python\n>>> from gbbox import LineString\n>>>\n>>> linestring_geojson = {\n>>>     "type": "LineString",\n>>>     "coordinates": [\n>>>         [1.0, 2.0],\n>>>         [3.0, 4.0]\n>>>     ]\n>>> }\n>>>\n>>> linestring = LineString(**linestring_geojson)\n>>> linestring_bbox = linestring.bbox()\n\n>>> print(linestring_bbox)\n>>> [1.0, 2.0, 3.0, 4.0]\n\n>>> print(linestring.min_lon)\n>>> 1.0\n```\n\n### Development\n\n```bash\n$ docker compose up -d\n# Start bash within container and enter it\n$ docker exec -it gbbox bash\n```\n\nProject will be automatically installed within docker container in an editable mode and\nany code changes will be immediately reflected. Keep in mind that if you have python shell\nrunning then you have to restart it.\n\nYou can also use `make lint` and `make test` as shortcuts to run linters and tests.\n\n### Contributing\n\nI am open to, and grateful for, any contributions made by the community.\n',
    'author': 'Łukasz Mikołajczak',
    'author_email': 'mikolajczak.luq@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/luqqk/geojson-bbox',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9.5,<4.0.0',
}


setup(**setup_kwargs)
