A simple framework to quickly compose and use multiple functionalities as endpoints.  
LogicLayer is built upon FastAPI to provide a simple way to group functionalities into reusable modules.

<p>
<a href="https://github.com/Datawheel/logiclayer/releases"><img src="https://flat.badgen.net/github/release/Datawheel/logiclayer" /></a>
<a href="https://github.com/Datawheel/logiclayer/blob/master/LICENSE"><img src="https://flat.badgen.net/github/license/Datawheel/logiclayer" /></a>
<a href="https://github.com/Datawheel/logiclayer/"><img src="https://flat.badgen.net/github/checks/Datawheel/logiclayer" /></a>
<a href="https://github.com/Datawheel/logiclayer/issues"><img src="https://flat.badgen.net/github/issues/Datawheel/logiclayer" /></a>
</p>

## Getting started

LogicLayer allows to group multiple endpoints with related functionality into a single module, which can be installed in a single step, and with the option to share external objects and make them available to the routes.

The unit of functionality is a Module, which must be a subclass of the `LogicLayerModule` class. Then you can mark its methods as module routes using the `route` decorator:

```python
# echo.py
import logiclayer as ll
import platform

class EchoModule(ll.LogicLayerModule):
    def get_python_version():
        return platform.python_version()

    @ll.route("GET", "/")
    def route_status(self):
        return {
            "module": "echo", 
            "version": "0.1.0", 
            "python": self.get_python_version(),
        }

    [...more methods]
```

You can setup multiple methods in your module class, and only the decorated ones will be setup as routes in your module. The `ll.route` method accepts the same parameters as FastAPI's `app.get/head/post/put` methods, with the difference you can set multiple methods at once passing a list instead of the HTTP method as string:

```python
ll.route("GET", "/")
# is the same as
ll.route(["GET"], "/")
# so this also works
ll.route(["GET", "HEAD"], "/")
# (...just be careful to leave the answer empty when needed)
```

Then just create a new `LogicLayer` instance and add the module using the `add_module()` method. The first argument is the prefix to the paths of all URLs for this module, and the second is the instance of the LogicLayerModule subclass:

```python
# example.py

import requests
import logiclayer as ll
from .echo import EchoModule

layer = LogicLayer()

# this will work as a healthcheck for the app
def is_online() -> bool:
    """Checks if the machine is online."""
    res = requests.get("http://clients3.google.com/generate_204")
    return (res.status_code == 204) and (res.headers.get("Content-Length") == "0")
# healthchecks are set to run in the root `/_health` path
layer.add_check(is_online)

echo = EchoModule()
layer.add_module("/demo", echo)
```

The `layer` object is an ASGI-compatible application, that can be used with uvicorn/gunicorn to run a server, the same way as you would with a FastAPI instance.

```bash
$ pip install uvicorn[standard]
$ uvicorn example:layer
```

Note the `example:layer` parameter is the reference to the `layer` variable in the `example` module/file, which [points to the ASGI app instance](https://www.uvicorn.org/#usage).

Optionally, you can also install a module in a common FastAPI instance, using the internal `APIRouter` instance:

```python
app = FastAPI()
echo = EchoModule()

app.include_router(echo.router, prefix="/demo")
```

---
&copy; 2022 [Datawheel, LLC.](https://www.datawheel.us/)  
This project is licensed under [MIT](./LICENSE).
