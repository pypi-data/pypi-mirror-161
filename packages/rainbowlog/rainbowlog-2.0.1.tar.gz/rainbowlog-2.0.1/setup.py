# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['rainbowlog']

package_data = \
{'': ['*']}

install_requires = \
['constyle>=1.0.2,<2.0.0', 'importlib-metadata>=4.11,<5.0']

setup_kwargs = {
    'name': 'rainbowlog',
    'version': '2.0.1',
    'description': 'Format your python logs with colours based on the log levels.',
    'long_description': '# Rainbow Log\n\nFormat your python logs with colours based on the log levels.\n\n## Installation\n\nYou can instll the package with pip or conda.\n```sh\n$ pip install rainbowlog\n```\n```sh\n$ conda install rainbowlog -c abrahammurciano\n```\n\n## Docs\n\nYou can find the documentation [here](https://abrahammurciano.github.io/rainbowlog/rainbowlog)\n\n## Usage\n\nHere\'s a basic example of a script that logs colorfully to the console, but regularly to a file.\n\n```python\nimport logging\nimport rainbowlog\n\nlogger = logging.getLogger(__name__)\n\n# This one will write to the console\nstream_handler = logging.StreamHandler()\n\n# This one will write to a file\nfile_handler = logging.FileHandler("output.log")\n\n# Here we decide how we want the logs to look like\nformatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")\n\n# We want the stream handler to be colorful\nstream_handler.setFormatter(rainbowlog.Formatter(formatter))\n\n# We don\'t want the file handler to be colorful\nfile_handler.setFormatter(formatter)\n\n# Finally we add the handlers to the logger\nlogger.addHandler(stream_handler)\nlogger.addHandler(file_handler)\n\nif __name__ == "__main__":\n\tlogger.debug("This is a debug message")\n\tlogger.info("This is an info message")\n\tlogger.warning("This is a warning message")\n\tlogger.error("This is an error message")\n\tlogger.critical("This is a critical message")\n```\n\nIf you want to change the format of the logs for each log level, you can use any callable that takes a string and returns the same string with ANSI codes surrounding it. There are many libraries you can use to provide such callables.\n\n```py\nimport logging\nfrom rainbowlog import Formatter\n\n# Here are some libraries you can use to get a style callable without dealing with ANSI codes\nfrom constyle import Style, Attributes as Attrs\nimport termcolor\nfrom functools import partial\n\n\nformatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")\ncolor_formatter = Formatter(\n\tformatter,\n\tlog_styles={\n\t\tlogging.DEBUG: Style(Attrs.BLUE, Attrs.FAINT), # An example using constyle\n\t\tlogging.INFO: lambda s: f"\\033[32m{s}\\033[0m", # An example using lambdas\n\t\tlogging.WARNING: termcolor.red, # An example using termcolor\'s predifined functions\n\t\tlogging.ERROR: partial(termcolor.colored, color="red", on_color="on_white", attrs=["bold"]), # An example using functools.partial\n\t\tlogging.CRITICAL: Attrs.RED + Attrs.ON_YELLOW + Attrs.BOLD + Attrs.UNDERLINE, # An example using constyle\'s added attributes\n\t}\n\texception_style=lambda s: f"{Attrs.RED + Attrs.ON_WHITE + Attrs.BOLD}{s}{Attrs.RESET}" # An example using lambdas and constyle,\n\tstack_style=Attrs.RED, # An example using a single constyle attribute\n)\n```',
    'author': 'Abraham Murciano',
    'author_email': 'abrahammurciano@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/abrahammurciano/rainbowlog',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
