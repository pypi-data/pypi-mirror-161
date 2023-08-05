# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['redisbench_admin',
 'redisbench_admin.commands',
 'redisbench_admin.compare',
 'redisbench_admin.deploy',
 'redisbench_admin.environments',
 'redisbench_admin.export',
 'redisbench_admin.export.common',
 'redisbench_admin.export.google_benchmark',
 'redisbench_admin.export.memtier_benchmark',
 'redisbench_admin.export.pyperf',
 'redisbench_admin.export.redis_benchmark',
 'redisbench_admin.extract',
 'redisbench_admin.grafana_api',
 'redisbench_admin.profilers',
 'redisbench_admin.run',
 'redisbench_admin.run.aibench_run_inference_redisai_vision',
 'redisbench_admin.run.ann',
 'redisbench_admin.run.ann.pkg',
 'redisbench_admin.run.ann.pkg.ann_benchmarks',
 'redisbench_admin.run.ann.pkg.ann_benchmarks.algorithms',
 'redisbench_admin.run.ann.pkg.ann_benchmarks.plotting',
 'redisbench_admin.run.ann.pkg.protocol',
 'redisbench_admin.run.ann.pkg.test',
 'redisbench_admin.run.ftsb',
 'redisbench_admin.run.memtier_benchmark',
 'redisbench_admin.run.redis_benchmark',
 'redisbench_admin.run.redisgraph_benchmark_go',
 'redisbench_admin.run.tsbs_run_queries_redistimeseries',
 'redisbench_admin.run.ycsb',
 'redisbench_admin.run_local',
 'redisbench_admin.run_remote',
 'redisbench_admin.utils',
 'redisbench_admin.watchdog']

package_data = \
{'': ['*'],
 'redisbench_admin': ['results/glove-100-angular/10/redisearch-hnsw/*',
                      'results/mnist-784-euclidean/10/redisearch-hnsw/*'],
 'redisbench_admin.run.ann.pkg': ['.github/workflows/*',
                                  'install/*',
                                  'results/*',
                                  'templates/*']}

install_requires = \
['Flask-HTTPAuth>=4.4.0,<5.0.0',
 'Flask>=2.0.1,<3.0.0',
 'GitPython>=3.1.12,<4.0.0',
 'Jinja2>=3.0.3,<4.0.0',
 'PyYAML>=6.0,<7.0',
 'ansicolors>=1.1.8,<2.0.0',
 'boto3>=1.13.24,<2.0.0',
 'certifi>=2021.10.8,<2022.0.0',
 'daemonize>=2.5.0,<3.0.0',
 'docker>=5.0.2,<6.0.0',
 'flask-restx>=0.5.1,<0.6.0',
 'humanize>=2.4.0,<3.0.0',
 'jsonpath_ng>=1.5.2,<2.0.0',
 'matplotlib>=3.1.2,<4.0.0',
 'pandas>=1.0,<2.0',
 'paramiko>=2.7.2,<3.0.0',
 'psutil>=5.6.6,<6.0.0',
 'pyWorkFlow>=0.0.2,<0.0.3',
 'py_cpuinfo>=5.0.0,<6.0.0',
 'pysftp>=0.2.9,<0.3.0',
 'pytablewriter[html]>=0.64.1,<0.65.0',
 'python_terraform>=0.10.1,<0.11.0',
 'redis>=4.2.2,<5.0.0',
 'requests>=2.23.0,<3.0.0',
 'slack-bolt>=1.13.0,<2.0.0',
 'slack-sdk>=3.15.2,<4.0.0',
 'sshtunnel>=0.4.0,<0.5.0',
 'toml>=0.10.1,<0.11.0',
 'tox-docker>=3.1.0,<4.0.0',
 'tqdm>=4.46.1,<5.0.0',
 'watchdog>=2.1.6,<3.0.0',
 'wget>=3.2,<4.0']

entry_points = \
{'console_scripts': ['perf-daemon = redisbench_admin.profilers.daemon:main',
                     'redisbench-admin = redisbench_admin.cli:main']}

setup_kwargs = {
    'name': 'redisbench-admin',
    'version': '0.9.17',
    'description': 'Redis benchmark run helper. A wrapper around Redis and Redis Modules benchmark tools ( ftsb_redisearch, memtier_benchmark, redis-benchmark, aibench, etc... ).',
    'long_description': '[![codecov](https://codecov.io/gh/RedisLabsModules/redisbench-admin/branch/master/graph/badge.svg)](https://codecov.io/gh/RedisLabsModules/redisbench-admin)\n![Actions](https://github.com/RedisLabsModules/redisbench-admin/workflows/Run%20Tests/badge.svg?branch=master)\n![Actions](https://badge.fury.io/py/redisbench-admin.svg)\n\n# [redisbench-admin](https://github.com/RedisLabsModules/redisbench-admin)\n\nRedis benchmark run helper can help you with the following tasks:\n\n- Setup abd teardown of benchmarking infrastructure specified\n  on [RedisLabsModules/testing-infrastructure](https://github.com/RedisLabsModules/testing-infrastructure)\n- Setup and teardown of an Redis and Redis Modules DBs for benchmarking\n- Management of benchmark data and specifications across different setups\n- Running benchmarks and recording results\n- Exporting performance results in several formats (CSV, RedisTimeSeries, JSON)\n- Finding on-cpu, off-cpu, io, and threading performance problems by attaching profiling tools/probers ( perf (a.k.a. perf_events), bpf tooling, vtune )\n- **[SOON]** Finding performance problems by attaching telemetry probes\n\nCurrent supported benchmark tools:\n\n- [redis-benchmark](https://github.com/redis/redis)\n- [memtier_benchmark](https://github.com/RedisLabs/memtier_benchmark)\n- [redis-benchmark-go](https://github.com/filipecosta90/redis-benchmark-go)\n- [YCSB](https://github.com/RediSearch/YCSB)\n- [tsbs](https://github.com/RedisTimeSeries/tsbs)\n- [redisgraph-benchmark-go](https://github.com/RedisGraph/redisgraph-benchmark-go)\n- [ftsb_redisearch](https://github.com/RediSearch/ftsb)\n- [ann-benchmarks](https://github.com/RedisAI/ann-benchmarks)\n- [SOON][aibench](https://github.com/RedisAI/aibench)\n\n## Installation\n\nInstallation is done using pip, the package installer for Python, in the following manner:\n\n```bash\npython3 -m pip install https://codeload.github.com/redis/redis-py/zip/refs/tags/v4.2.0rc3\npython3 -m pip install redisbench-admin\n```\n\n## Profiler daemon\n\nYou can use the profiler daemon by itself in the following manner. \nOn the target machine do as follow:\n\n```bash\npip3 install --upgrade pip\npip3 install redisbench-admin --ignore-installed PyYAML\n\n# install perf\napt install linux-tools-common linux-tools-generic linux-tools-`uname -r` -y\n\n# ensure perf is working\nperf --version\n\n# install awscli\nsnap install aws-cli --classic\n\n\n# configure aws\naws configure\n\n# start the perf-daemon\nperf-daemon start\nWARNING:root:Unable to detected github_actor. caught the following error: No section: \'user\'\nWritting log to /tmp/perf-daemon.log\nStarting perf-daemon. PID file /tmp/perfdaemon.pid. Daemon workdir: /root/RedisGraph\n\n# check daemon is working appropriatelly\ncurl localhost:5000/ping\n\n# start a profile\ncurl -X POST localhost:5000/profiler/perf/start/<pid to profile>\n\n# stop a profile\ncurl -X POST -d \'{"aws_access_key_id":$AWS_ACCESS_KEY_ID,"aws_secret_access_key":$AWS_SECRET_ACCESS_KEY}\' localhost:5000/profiler/perf/stop/<pid to profile>\n```\n\n\n## Development\n\n1. Install [pypoetry](https://python-poetry.org/) to manage your dependencies and trigger tooling.\n```sh\npip install poetry\n```\n\n2. Installing dependencies from lock file\n\n```\npoetry install\n```\n\n### Running formaters\n\n```sh\npoetry run black .\n```\n\n\n### Running linters\n\n```sh\npoetry run flake8\n```\n\n\n### Running tests\n\nA test suite is provided, and can be run with:\n\n```sh\n$ tox\n```\n\nTo run a specific test:\n```sh\n$ tox -- tests/test_redistimeseries.py\n```\n\n## License\n\nredisbench-admin is distributed under the BSD3 license - see [LICENSE](LICENSE)\n',
    'author': 'filipecosta90',
    'author_email': 'filipecosta.90@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.9,<4.0.0',
}


setup(**setup_kwargs)
