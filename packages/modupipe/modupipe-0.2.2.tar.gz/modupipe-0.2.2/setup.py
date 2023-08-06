# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['modupipe']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'modupipe',
    'version': '0.2.2',
    'description': 'A modular and extensible ETL-like pipeline builder',
    'long_description': '[![Build](https://github.com/vigenere23/modupipe/actions/workflows/build.yml/badge.svg)](https://github.com/vigenere23/modupipe/actions/workflows/build.yml)\n\n# ModuPipe : A modular and extensible ETL-like pipeline builder\n\n## Benefits\n\n- Entirely typed\n- Abstract, so it fits any use case\n- Class-based for easy configurations and injections\n\n## Usage\n\nExtract-Transform-Load (ETL) pipelines are a classic form of data-processing pipelines used in the industry. It consists of 3 main elements:\n\n1. A **`Source`**, which returns data in a stream-like structure (`Iterator` in Python) using a pull strategy.\n2. A (list of) **`Mapper`** (optional), which transforms (parse, converts, filters, etc.) the data obtained from the source(s). Mappers can be chained together, and chained to a source in order to form a new source.\n3. A **`Sink`**, which receives the maybe-transformed data using a push strategy. Sinks can be multiple (with `SinkList`).\n\nTherefore, those 3 processes are offered as interfaces, easily chainable and interchangeable at any time.\n\nAn interface `Runnable` is also offered in order to interface the concept of "running a pipeline". This enables a powerfull composition pattern for wrapping the execution behaviour of runnables.\n\n## Examples\n\nUsage examples are present in the [examples](./examples) folder.\n\n## Discussion\n\n### Optimizing pushing to multiple sinks\n\nIf you have multiple sinks (using the `SinkList` class), but performance is a must, then you should use a multi-processing approach, and push to 1 queue per sink. Each queue will also become a direct source for each sink, all running in parallel. This is especially usefull when at least one of the sinks takes a long processing time.\n\nAs an example, let\'s take a `Sink1` which is very slow, and a `Sink2` which is normally fast. You\'ll be going from :\n\n```\n┌─── single pipeline ───┐\n Source ┬🠦 Sink1 (slow)\n        └🠦 Sink2 (late)\n```\n\nto :\n\n```\n┌──── pipeline 1 ────┐             ┌──── pipeline 2 ─────┐\n Source ┬🠦 QueueSink1 ─🠦 Queue1 🠤─ QueueSource1 ─🠦 Sink1 (slow)\n        └🠦 QueueSink1 ─🠦 Queue2 🠤─ QueueSource2 ─🠦 Sink2 (not late)\n                                   └──── pipeline 3 ─────┘\n```\n\nThis will of course not accelerate the `Sink1` processing time, but all the other sinks performances will be greatly improved by not waiting for each other.\n',
    'author': 'vigenere23',
    'author_email': 'lolgab1@hotmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/vigenere23/modupipe',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
