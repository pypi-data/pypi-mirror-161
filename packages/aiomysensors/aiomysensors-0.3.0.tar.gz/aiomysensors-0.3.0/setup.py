# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['aiomysensors',
 'aiomysensors.cli',
 'aiomysensors.model',
 'aiomysensors.model.protocol',
 'aiomysensors.transport']

package_data = \
{'': ['*']}

install_requires = \
['aiofiles>=0.8,<0.9',
 'asyncio-mqtt>=0.12,<0.13',
 'awesomeversion>=22.6,<23.0',
 'click>=8.1,<9.0',
 'marshmallow>=3.17,<4.0',
 'pyserial-asyncio>=0.6,<0.7']

entry_points = \
{'console_scripts': ['aiomysensors = aiomysensors.cli:cli']}

setup_kwargs = {
    'name': 'aiomysensors',
    'version': '0.3.0',
    'description': 'Python asyncio package to connect to MySensors gateways.',
    'long_description': '# aiomysensors\n\n<p align="center">\n  <a href="https://github.com/MartinHjelmare/aiomysensors/actions?query=workflow%3ACI">\n    <img src="https://img.shields.io/github/workflow/status/MartinHjelmare/aiomysensors/CI/main?label=CI&logo=github&style=flat-square" alt="CI Status" >\n  </a>\n  <a href="https://codecov.io/gh/MartinHjelmare/aiomysensors">\n    <img src="https://img.shields.io/codecov/c/github/MartinHjelmare/aiomysensors.svg?logo=codecov&logoColor=fff&style=flat-square" alt="Test coverage percentage">\n  </a>\n</p>\n<p align="center">\n  <a href="https://python-poetry.org/">\n    <img src="https://img.shields.io/badge/packaging-poetry-299bd7?style=flat-square&logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA4AAAASCAYAAABrXO8xAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAJJSURBVHgBfZLPa1NBEMe/s7tNXoxW1KJQKaUHkXhQvHgW6UHQQ09CBS/6V3hKc/AP8CqCrUcpmop3Cx48eDB4yEECjVQrlZb80CRN8t6OM/teagVxYZi38+Yz853dJbzoMV3MM8cJUcLMSUKIE8AzQ2PieZzFxEJOHMOgMQQ+dUgSAckNXhapU/NMhDSWLs1B24A8sO1xrN4NECkcAC9ASkiIJc6k5TRiUDPhnyMMdhKc+Zx19l6SgyeW76BEONY9exVQMzKExGKwwPsCzza7KGSSWRWEQhyEaDXp6ZHEr416ygbiKYOd7TEWvvcQIeusHYMJGhTwF9y7sGnSwaWyFAiyoxzqW0PM/RjghPxF2pWReAowTEXnDh0xgcLs8l2YQmOrj3N7ByiqEoH0cARs4u78WgAVkoEDIDoOi3AkcLOHU60RIg5wC4ZuTC7FaHKQm8Hq1fQuSOBvX/sodmNJSB5geaF5CPIkUeecdMxieoRO5jz9bheL6/tXjrwCyX/UYBUcjCaWHljx1xiX6z9xEjkYAzbGVnB8pvLmyXm9ep+W8CmsSHQQY77Zx1zboxAV0w7ybMhQmfqdmmw3nEp1I0Z+FGO6M8LZdoyZnuzzBdjISicKRnpxzI9fPb+0oYXsNdyi+d3h9bm9MWYHFtPeIZfLwzmFDKy1ai3p+PDls1Llz4yyFpferxjnyjJDSEy9CaCx5m2cJPerq6Xm34eTrZt3PqxYO1XOwDYZrFlH1fWnpU38Y9HRze3lj0vOujZcXKuuXm3jP+s3KbZVra7y2EAAAAAASUVORK5CYII=" alt="Poetry">\n  </a>\n  <a href="https://github.com/ambv/black">\n    <img src="https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square" alt="black">\n  </a>\n  <a href="https://github.com/pre-commit/pre-commit">\n    <img src="https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white&style=flat-square" alt="pre-commit">\n  </a>\n</p>\n<p align="center">\n  <a href="https://pypi.org/project/aiomysensors/">\n    <img src="https://img.shields.io/pypi/v/aiomysensors.svg?logo=python&logoColor=fff&style=flat-square" alt="PyPI Version">\n  </a>\n  <img src="https://img.shields.io/pypi/pyversions/aiomysensors.svg?style=flat-square&logo=python&amp;logoColor=fff" alt="Supported Python versions">\n  <img src="https://img.shields.io/pypi/l/aiomysensors.svg?style=flat-square" alt="License">\n</p>\n\nPython asyncio package to connect to MySensors gateways.\n\n## Installation\n\nInstall this via pip (or your favourite package manager):\n\n`pip install aiomysensors`\n\n## Example\n\n```py\n"""Show a minimal example using aiomysensors."""\nimport asyncio\n\nfrom aiomysensors import AIOMySensorsError, Gateway, SerialTransport\n\n\nasync def run_gateway() -> None:\n    """Run a serial gateway."""\n    port = "/dev/ttyACM0"\n    baud = 115200\n    transport = SerialTransport(port, baud)\n\n    try:\n        async with Gateway(transport) as gateway:\n            async for message in gateway.listen():\n                print("Message received:", message)\n    except AIOMySensorsError as err:\n        print("Error:", err)\n\n\nif __name__ == "__main__":\n    try:\n        asyncio.run(run_gateway())\n    except KeyboardInterrupt:\n        pass\n```\n\n## Command Line Interface\n\nThere\'s a CLI for testing purposes.\n\n```sh\naiomysensors --debug serial-gateway -p /dev/ttyACM0\n```\n\n## Credits\n\nThis package was created with\n[Cookiecutter](https://github.com/audreyr/cookiecutter) and the\n[browniebroke/cookiecutter-pypackage](https://github.com/browniebroke/cookiecutter-pypackage)\nproject template.\n',
    'author': 'Martin Hjelmare',
    'author_email': 'marhje52@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/MartinHjelmare/aiomysensors',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
