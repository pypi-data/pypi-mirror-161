# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['wmill']

package_data = \
{'': ['*']}

install_requires = \
['windmill-api>=1.25.0,<2.0.0']

setup_kwargs = {
    'name': 'wmill',
    'version': '1.25.0',
    'description': 'A client library for accessing Windmill server wrapping the Windmill client API',
    'long_description': '# wmill\n\nThe core client for the [Windmill](https://windmill.dev) platform.\n\nIt is a convenient wrapper around the exhaustive, automatically generated from\nOpenApi but less user-friendly\n[windmill-api](https://pypi.org/project/windmill-api/).\n\n## Quickstart\n\n```python\nimport wmill\n\n\ndef main():\n    #os.environ.set("WM_TOKEN", "<mytoken>") OPTIONAL to set token used by the wmill client\n    version = wmill.get_version()\n    resource = wmill.get_resource("u/user/resource_path")\n\n    # run synchronously, will return the result\n    res = wmill.run_script_sync(hash="000000000000002a", args={})\n    print(res)\n\n    for _ in range(3):\n        # run asynchrnously, will return immediately. Can be scheduled\n        wmill.run_script_async(hash="000000000000002a", args={}, scheduled_in_secs=10)\n```\n',
    'author': 'Ruben Fiszel',
    'author_email': 'ruben@rubenfiszel.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://windmill.dev',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
