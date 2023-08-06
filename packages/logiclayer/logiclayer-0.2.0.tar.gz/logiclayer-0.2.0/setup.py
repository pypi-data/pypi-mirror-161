# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['logiclayer']

package_data = \
{'': ['*']}

install_requires = \
['asyncio>=3.4.0,<4.0.0', 'fastapi>=0.75,<1.0']

setup_kwargs = {
    'name': 'logiclayer',
    'version': '0.2.0',
    'description': 'A simple framework to quickly compose and use multiple functionalities as endpoints.',
    'long_description': 'A simple framework to quickly compose and use multiple functionalities as endpoints.  \nLogicLayer is built upon FastAPI to provide a simple way to group functionalities into reusable modules.\n\n<p>\n<a href="https://github.com/Datawheel/logiclayer/releases"><img src="https://flat.badgen.net/github/release/Datawheel/logiclayer" /></a>\n<a href="https://github.com/Datawheel/logiclayer/blob/master/LICENSE"><img src="https://flat.badgen.net/github/license/Datawheel/logiclayer" /></a>\n<a href="https://github.com/Datawheel/logiclayer/"><img src="https://flat.badgen.net/github/checks/Datawheel/logiclayer" /></a>\n<a href="https://github.com/Datawheel/logiclayer/issues"><img src="https://flat.badgen.net/github/issues/Datawheel/logiclayer" /></a>\n</p>\n\n## Getting started\n\nLogicLayer allows to group multiple endpoints with related functionality into a single module, which can be installed in a single step, and with the option to share external objects and make them available to the routes.\n\nThe unit of functionality is a Module, which must be a subclass of the `LogicLayerModule` class. Then you can mark its methods as module routes using the `route` decorator:\n\n```python\n# echo.py\nimport logiclayer as ll\nimport platform\n\nclass EchoModule(ll.LogicLayerModule):\n    def get_python_version():\n        return platform.python_version()\n\n    @ll.route("GET", "/")\n    def route_status(self):\n        return {\n            "module": "echo", \n            "version": "0.1.0", \n            "python": self.get_python_version(),\n        }\n\n    [...more methods]\n```\n\nYou can setup multiple methods in your module class, and only the decorated ones will be setup as routes in your module. The `ll.route` method accepts the same parameters as FastAPI\'s `app.get/head/post/put` methods, with the difference you can set multiple methods at once passing a list instead of the HTTP method as string:\n\n```python\nll.route("GET", "/")\n# is the same as\nll.route(["GET"], "/")\n# so this also works\nll.route(["GET", "HEAD"], "/")\n# (...just be careful to leave the answer empty when needed)\n```\n\nThen just create a new `LogicLayer` instance and add the module using the `add_module()` method. The first argument is the prefix to the paths of all URLs for this module, and the second is the instance of the LogicLayerModule subclass:\n\n```python\n# example.py\n\nimport requests\nimport logiclayer as ll\nfrom .echo import EchoModule\n\nlayer = LogicLayer()\n\n# this will work as a healthcheck for the app\ndef is_online() -> bool:\n    """Checks if the machine is online."""\n    res = requests.get("http://clients3.google.com/generate_204")\n    return (res.status_code == 204) and (res.headers.get("Content-Length") == "0")\n# healthchecks are set to run in the root `/_health` path\nlayer.add_check(is_online)\n\necho = EchoModule()\nlayer.add_module("/demo", echo)\n```\n\nThe `layer` object is an ASGI-compatible application, that can be used with uvicorn/gunicorn to run a server, the same way as you would with a FastAPI instance.\n\n```bash\n$ pip install uvicorn[standard]\n$ uvicorn example:layer\n```\n\nNote the `example:layer` parameter is the reference to the `layer` variable in the `example` module/file, which [points to the ASGI app instance](https://www.uvicorn.org/#usage).\n\nOptionally, you can also install a module in a common FastAPI instance, using the internal `APIRouter` instance:\n\n```python\napp = FastAPI()\necho = EchoModule()\n\napp.include_router(echo.router, prefix="/demo")\n```\n\n---\n&copy; 2022 [Datawheel, LLC.](https://www.datawheel.us/)  \nThis project is licensed under [MIT](./LICENSE).\n',
    'author': 'Francisco Abarzua',
    'author_email': 'francisco@datawheel.us',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Datawheel/logiclayer',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
