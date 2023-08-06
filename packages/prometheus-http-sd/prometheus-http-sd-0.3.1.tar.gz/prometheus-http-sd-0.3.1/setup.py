# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['prometheus_http_sd']

package_data = \
{'': ['*']}

install_requires = \
['Flask>=2.1.3,<3.0.0',
 'PyYAML>=6.0,<7.0',
 'prometheus-client>=0.14.1,<0.15.0',
 'waitress>=2.1.2,<3.0.0']

entry_points = \
{'console_scripts': ['prometheus-http-sd = prometheus_http_sd.app:main']}

setup_kwargs = {
    'name': 'prometheus-http-sd',
    'version': '0.3.1',
    'description': 'Prometheus HTTP SD framework.',
    'long_description': '# prometheus-http-sd\n\nThis is a\n[Prometheus HTTP SD](https://prometheus.io/docs/prometheus/latest/http_sd/)\nframework.\n\n[![Test](https://github.com/laixintao/prometheus-http-sd/actions/workflows/test.yaml/badge.svg)](https://github.com/laixintao/prometheus-http-sd/actions/workflows/test.yaml)\n\n## Features\n\n- Support static targets from Json file;\n- Support static targets from Yaml file;\n- Support generating target list using Python script;\n\n## Installation\n\n```shell\npip install prometheus-http-sd\n```\n\n## Usage\n\nFirst, you need a directory, everything in this directory will be used to\ngenerate targets for prometheus-http-sd.\n\n```shell\n$ mkdir targets\n```\n\nIn this directory:\n\n- Filename that ending with `.json` will be exposed directly\n- Filename that ending with `.yaml` will be exposed directly\n- Filename that ending with `.py` must include a `generate_targets()` function,\n  the function will be run, and it must return a `TargetList` (Type helper in\n  `prometheus_http_sd.targets.`)\n- Filename that starts with `_` will be ignored, so you can have some python\n  utils there, for e.g. `_utils/__init__.py` that you can import in you\n  `generate_targets()`\n- Filename that starts with `.` (hidden file in Linux) will also be ignored\n\nThen you can run `prometheus-http-sd -h 0.0.0.0 -p 8080 /tmp/targets`,\nprometheus-http-sd will start to expose targets at: http://0.0.0.0:8080/targets\n\nThe `-h` and `-p` is optional, defaults to `127.0.0.1` and `8080`.\n\n```shell\n$ prometheus-http-sd /tmp/good_root\n[2022-07-24 00:52:03,896] {wasyncore.py:486} INFO - Serving on http://127.0.0.1:8080\n```\n\n### Script Dependencies\n\nIf you want your scripts to use some other python library, just install them\ninto the **same virtualenv** that you install prometheus-http-sd, so that\nprometheus-http-sd can import them.\n\n## The Target Path\n\nprometheus-http-sd support sub-pathes.\n\nFor example, if we use `export PROMETHEUS_HTTP_SD_DIR=gateway`, and the\n`gateway` directory\'s structure is as follows:\n\n```shell\ngateway\n├── nginx\n│\xa0\xa0 ├── edge.py\n│\xa0\xa0 └── targets.json\n└── targets.json\n```\n\nThen:\n\n- `/targets/gateway` will return the targets from:\n  - `gateway/nginx/edge.py`\n  - `gateway/nginx/targets.json`\n  - `gateway/targets.json`\n- `/targets/gateway/nginx` will return the targets from:\n  - `gateway/nginx/edge.py`\n  - `gateway/nginx/targets.json`\n\nThis is very useful when you use vertical scaling. Say you have 5 Prometheus\ninstances, and you want each one of them scrape for different targets, then you\ncan use the sub-path feature of prometheus-http-sd.\n\nFor example, in one Prometheus\'s config:\n\n```yaml\nscrape_configs:\n  - job_name: "nginx"\n    http_sd_config:\n      url: http://prometheus-http-sd:8080/targets/nginx\n\n  - job_name: "etcd"\n    http_sd_config:\n      url: http://prometheus-http-sd:8080/targets/etcd\n```\n\nAnd in another one:\n\n```yaml\nscrape_configs:\n  - job_name: "nginx"\n    http_sd_config:\n      url: http://prometheus-http-sd:8080/targets/database\n\n  - job_name: "etcd"\n    http_sd_config:\n      url: http://prometheus-http-sd:8080/targets/application\n```\n\n## Update Your Scripts\n\nIf you want to update your script file or target json file, just upload and\noverwrite with your new version, it will take effect immediately after you\nmaking changes, **there is no need to restart** prometheus-http-sd,\nprometheus-http-sd will read the file (or reload the python script) every time\nserving a request.\n\nIt is worth noting that restarting is safe because if Prometheus failed to get\nthe target list via HTTP request, it won\'t update its current target list to\nempty, instead,\n[it will keep using the current list](https://prometheus.io/docs/prometheus/latest/http_sd/).\n\n> Prometheus caches target lists. If an error occurs while fetching an updated\n> targets list, Prometheus keeps using the current targets list.\n\nFor the same reason, if there are 3 scripts under `/targets/mysystem` and only\none failed for a request, prometheus-http-sd will return a HTTP 500 Error for\nthe whole request instead of returning the partial targets from the other two\nscripts.\n\nAlso for the same reason, if your script met any error, you should throw out\n`Exception` all the way to the top instead of catch it in your script and return\na null `TargetList`, if you return a null `TargetList`, prometheus-http-sd will\nthink that your script run successfully and empty the target list as well.\n\nYou can notice this error from stdout logs or `/metrics` from\nprometheus-http-sd.\n\n## Best Practice\n\nYou can use a git repository to manage your target generator.\n',
    'author': 'laixintao',
    'author_email': 'laixintaoo@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
