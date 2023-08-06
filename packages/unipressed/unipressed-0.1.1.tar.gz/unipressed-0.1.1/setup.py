# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['unipressed', 'unipressed.types']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.28.1,<3.0.0', 'typing-extensions>=4.3.0,<5.0.0']

setup_kwargs = {
    'name': 'unipressed',
    'version': '0.1.1',
    'description': 'Comprehensive Python client for the Uniprot REST API',
    'long_description': '# Unipressed\n\n**Please visit the [project website](https://multimeric.github.io/Unipressed/) for more comprehensive documentation.**\n\n## Introduction\n\nUnipressed (Uniprot REST) is an API client for the protein database [Uniprot](https://www.uniprot.org/).\nIt provides thoroughly typed and documented code to ensure your use of the library is easy, fast, and correct!\n\n### Example\nLet\'s say we\'re interested in very long proteins that are encoded within a chloroplast, in any organism:\n```python\nimport json\nfrom unipressed import UniprotkbSearch\n\nfor record in UniprotkbSearch(\n    query={\n        "and_": [\n            {"organelle": "chloroplast"},\n            {"length": (5000, "*")}\n        ]\n    },\n    fields=["length", "gene_names"]\n).each_record():\n    print(json.dumps(record, indent=4))\n```\n\nThis will print:\n```json\n{\n    "primaryAccession": "A0A088CK67",\n    "genes": [\n        {\n            "geneName": {\n                "evidences": [\n                    {\n                        "evidenceCode": "ECO:0000313",\n                        "source": "EMBL",\n                        "id": "AID67672.1"\n                    }\n                ],\n                "value": "ftsH"\n            }\n        }\n    ],\n    "sequence": {\n        "length": 5242\n    }\n}\n```\n\n### Advantages\n\n* Detailed type hints for autocompleting queries as you type\n* Autocompletion for return fields\n* Documentation for each field\n* Automatic results parsing, for `json`, `tsv`, `list`, and `xml`\n* Built-in pagination, so you don\'t have to handle any of that yourself!\n* Most of the API is automatically generated, ensuring very rapid updates whenever the API changes\n* Thoroughly tested, with 41 unit tests and counting!\n\n## Usage\n\n### Installation\n\nIf you\'re using poetry:\n```bash\npoetry add unipressed\n```\n\nOtherwise:\n```bash\npip install unipressed\n```\n\n### Query Syntax\n\nYou can\'t go wrong by following the type hints.\nI strongly recommend using something like [`pylance`](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance) for [Visual Studio Code](https://code.visualstudio.com/), which will provide automatic completions and warn you when you have used the wrong syntax.\n\nIf you already know how to use the Uniprot query language, you can always just input your queries as strings:\n```python\nUniprotkbSearch(query="(gene:BRCA*) AND (organism_id:10090)")\n```\n\nHowever, if you want some built-in query validation and code completion using Python\'s type system, then you can instead use a dictionary.\nThe simplest query is a dictionary with a single key: \n```python\n{\n    "family": "kinase"\n}\n```\n\nYou can compile more complex queries using the `and_`, `or_` and `not_` keys.\nThese first two operators take a list of query dictionaries: \n```python\n{\n    "and_": [\n        {"family": "kinase"},\n        {"organism_id": "9606"},\n    ]\n}\n```\n\nMost "leaf" nodes of the query tree (ie those that aren\'t operators like `and_`) are strings. \nA few are integers or floats, and a few are *ranges*, which you input using a tuple with two elements, indicating the start and end of the range.\nIf you use the literal `"*"` then you can leave the range open at one end. \nFor example, this query returns any protein that is in the range $(5000, \\infty)$\n```python\n{"length": (5000, "*")}\n```',
    'author': 'Michael Milton',
    'author_email': 'michael.r.milton@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://multimeric.github.io/Unipressed',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
