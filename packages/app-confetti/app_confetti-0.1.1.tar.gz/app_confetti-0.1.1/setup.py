# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['app_confetti', 'app_confetti.fetch']

package_data = \
{'': ['*']}

install_requires = \
['python-dotenv>=0.15.0,<0.16.0']

extras_require = \
{'aws': ['boto3>=1.14.49,<2.0.0', 'ec2-metadata>=2.2.0,<3.0.0']}

setup_kwargs = {
    'name': 'app-confetti',
    'version': '0.1.1',
    'description': 'Environment application configuration',
    'long_description': '# Configuration Fetcher v0.1.1\n\nCommon code for interacting with dev environs, deployed environs with ENV vars\nor for deployed AWS (optional extra) environs.\n\n## Config class\n\n```python\n    from app_confetti import util\n\n    @dataclasses.dataclass(frozen=True)\n    class Config:\n        required_key: str = util.env("REQUIRED_KEY")\n        logging_level: str = util.env("LOGGING_LEVEL:INFO")\n        sentry_dsn: int = util.env("SENTRY_DSN:__NONE__")\n        debug: bool = util.env("DEBUG:__FALSE__")\n    \n        @property\n        def logging_config(self):\n            return {\n                "version": 1,\n                "disable_existing_loggers": False,\n                "formatters": {\n                    "default": {\n                        "format": "[%(asctime)s][%(name)s][%(levelname)s]: %(message)s",\n                        "datefmt": "%Y-%m-%d %H:%M:%S",\n                    },\n                },\n                "handlers": {\n                    "default": {\n                        "class": "logging.StreamHandler",\n                        "level": self.logging_level,\n                        "formatter": "default",\n                    },\n                    "sentry": {\n                        "level": "ERROR",\n                        "class": "raven.handlers.logging.SentryHandler",\n                        "dsn": self.sentry_dsn,\n                    },\n                },\n                "loggers": {\n                    "": {\n                        "handlers": ["default", "sentry"],\n                        "level": self.logging_level,\n                        "propagate": True,\n                    },\n                    "raven": {\n                        "handlers": ["default"],\n                        "level": "WARNING",\n                        "propagate": True,\n                    },\n                },\n            }\n```\n',
    'author': 'Daniel Edgecombe',
    'author_email': 'edgy.edgemond@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/EdgyEdgemond/app-confetti/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
