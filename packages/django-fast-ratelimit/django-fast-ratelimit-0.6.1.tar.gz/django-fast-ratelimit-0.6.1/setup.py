# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ratelimit']

package_data = \
{'': ['*']}

install_requires = \
['django>=3.0']

extras_require = \
{'test': ['tox']}

setup_kwargs = {
    'name': 'django-fast-ratelimit',
    'version': '0.6.1',
    'description': 'Fast ratelimit implementation with django caches',
    'long_description': '# django-fast-ratelimit\n\n\nDjango-fast-ratelimit provides a secure and fast ratelimit facility based on the django caching framework.\nIt uses a "Fixed window counter"-algorithm based on:\nhttps://medium.com/figma-design/an-alternative-approach-to-rate-limiting-f8a06cf7c94c\n\n\n\n## Installation\n\n```` bash\npip install django-fast-ratelimit\n\n````\n\nNote: pip >= 19 is required\n\n## usage\n\n\nDecorator:\n\n```` python\nimport ratelimit\n\n@ratelimit.decorate(key="ip", rate="1/s")\ndef expensive_func(request):\n    # how many ratelimits request limiting\n    if request.ratelimit["request_limit"] > 0:\n        # reschedule with end of rate epoch\n        return request_waiting(request.ratelimit["end"])\n\n````\n\nblocking Decorator (raises RatelimitError):\n\n```` python\nimport ratelimit\n\n@ratelimit.decorate(key="ip", rate="1/s", block=True, methods=ratelimit.UNSAFE)\ndef expensive_func(request):\n    # how many ratelimits request limiting\n    if request.ratelimit["end"] > 0:\n\n````\n\n\n\ndecorate View (requires group):\n\n```` python\nimport ratelimit\nfrom django.views.generic import View\nfrom django.utils.decorators import method_decorator\n\n\n@method_decorator(ratelimit.decorate(\n  key="ip", rate="1/s", block=True, methods=ratelimit.SAFE, group="required"\n), name="dispatch")\nclass FooView(View):\n    ...\n\n````\n\nmanual\n```` python\nimport ratelimit\n\n\ndef func(request):\n    ratelimit.get_ratelimit(key="ip", rate="1/s", request=request, group="123")\n    # or only for GET\n    ratelimit.get_ratelimit(\n        key="ip", rate="1/s", request=request, group="123", methods="GET"\n    )\n    # also simple calls possible (note: key in bytes format)\n    ratelimit.get_ratelimit(\n        key=b"abc", rate="1/s", group="123"\n    )\n    # check constraints of rate\n    r = ratelimit.parse_rate("1/s")  # returns tuple (amount, period)\n    assert(r[1]==1)  #  assert period is 1 second\n    # for simple naming use o2g (object to group)\n    ratelimit.get_ratelimit(\n        key=b"abc", rate=r, group=ratelimit.o2g(func)\n    )\n\n````\n\n## parameters\n\n### ratelimit.get_ratelimit:\n\n* group: group name, can be callable (fun(request))\n* methods: set of checked methods, can be callable (fun(request, group)), modes:\n  * callable(request, group): allow dynamic\n  * ratelimit.ALL (default): all methods are checked\n  * \\("HEAD", "GET"\\): list of checked methods\n  * ratelimit.invertedset(["HEAD", "GET"]): inverted set of checked methods. Here: every method is checked, except HEAD, GET\n* request: ingoing request (optional if key supports it and methods=ratelimit.ALL (default))\n* key: multiple modes possible:\n    * bool: True: skip key (should only be used for baking), False: disable cache (like RATELIMIT_ENABLE=False)\n    * int:  sidestep cache, value will be used for request_limit. 0 is for never blocking, >=1 blocks\n    * str: "path.to.method:argument"\n    * str: "inbuildmethod:argument" see methods for valid arguments\n    * str: "inbuildmethod"  method which is ready to use for (request, group)\n    * tuple,list: ["method", args...]: method (can be also inbuild) with arbitary arguments\n    * bytes: static key (supports mode without request)\n    * callable: check return of function (fun(request, group)), return must be string (converted to bytes), bytes, bool or int (see "key" for effects)\n  * empty_to: convert empty keys (b"") to parameter. Must be bytes, bool or int (see "key" for effects) (default: keep b"")\n  * cache: specify cache to use, defaults to RATELIMIT_DEFAULT_CACHE setting (default: "default")\n  * hash_algo: name of hash algorithm for creating cache_key (defaults to RATELIMIT_KEY_HASH setting (default: "sha256"))\n    Note: group is seperately hashed\n  * hashctx: optimation parameter, read the code and only use if you know what you are doing. It basically circumvents the parameter hashing and only hashes the key. If the key parameter is True even the key is skipped\n  * action {ratelimit.Action}:\n    *  PEEK: only lookup\n    *  INCREASE: count up and return result\n    *  RESET: return former result and reset (default: {PEEK})\n  * include_reset: add reset method to Ratelimit object if no cache bypass is in use\n\nreturns following dict\n\n* count: how often in the window the ip whatever was calling\n* limit: limit when it should block\n* request_limit: >=1 should block or reject, 0: should accept\n* end: when does the block end\n* group: group name\n\n\n### ratelimit.decorate:\n\nAll of ratelimit.get_ratelimit except request. group is here optional (except for decorations with method_decorator (no access to wrapped function)).\nAlso supports:\n* block: should hard block with an RatelimitExceeded exception (subclass of PermissionDenied) or only annotate request with ratelimit\n\n## helpers\n\n* ratelimit.invertedset: inverts a collection, useful for http methods\n* ratelimit.o2g: auto generate group names\n\n## methods\n\nSee in methods which methods are available. Here some of them:\n* ip: use ip address as key, argument: [netmask ipv4/]netmask ipv6\n* user: authenticated user primary key or b""\n* user_or_ip: use autenticated user primary key as key. If not autenticated fallback to ip, also with netmask argument\n* user_and_ip: same like user_or_ip except that the ip matching also applies for authenticated users\n* get: generate key from multiple sources, input can be multiple input args or a dict with options\n\n## settings\n\n* RATELIMIT_GROUP_HASH: hash function which is used for the group hash (default: md5)\n* RATELIMIT_KEY_HASH: hash function which is used as default for the key hash, can be overridden with hash_algo (default: md5)\n* RATELIMIT_ENABLE disable ratelimit (e.g. for tests) (default: enabled)\n* RATELIMIT_KEY_PREFIX: internal prefix for the hash keys (so you don\'t have to create a new cache). Defaults to "frl:".\n* RATELIMIT_DEFAULT_CACHE: default cache to use, defaults to "default" and can be overridden by cache parameter\n\n\n## TODO\n\n* more documentation\n',
    'author': 'Alexander Kaftan',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/devkral/django-fast-ratelimit',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.9',
}


setup(**setup_kwargs)
