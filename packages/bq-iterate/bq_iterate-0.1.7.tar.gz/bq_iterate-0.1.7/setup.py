# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['bq_iterate']

package_data = \
{'': ['*']}

install_requires = \
['google-cloud-bigquery>=2.2.0,<3.0.0', 'tenacity>=7.0.0,<8.0.0']

setup_kwargs = {
    'name': 'bq-iterate',
    'version': '0.1.7',
    'description': 'Work with BigQuery data as you do with lists in python',
    'long_description': '# Introduction\nThis project serves as a BigQuery helper that allows you to query data from BigQuery, without worrying about memory limitation concerns, it makes working with BigQuery data as easy as working with lists in python\n\n## Installation : \n```python3.8 -m pip install  bq-iterate```\n## Usage\n```python\nfrom bq_iterate import BqQueryRowIterator, batchify_iterator\nquery = "select * from <project_id>.<dataset_id>.<table_id>"\nrow_itrator = BqQueryRowIterator(query=query, batch_size=2000000) #  choose a batch_size that will fit into your memory\nbatches = batchify_iterator(row_itrator, batch_slice=50000) #  choose a batch_slice that will fit into your memory\ndata = []\nfor batch in batches:\n    # do your batch processing here\n    data.append(len(batch))\nprint(sum(data))\n```\n\n## What happens behind the scenes :\n\n**bq_iterate provide two functionalities\xa0:**\n\n* 2 classes BqQueryIterator and BqTableRowIterator, they behave like an iterator, where they hold only <batch_size> elements in memory and when you want to access the element <batch_size + 1> the iterator calls in memory the next batch_size + 1 elements\n\n* A function batchify_iterator, what this function does, it takes an iterator and yields slices of it, the <batch_slice> can be bigger than the <batch_size> even if by common sens it\'s supposed to be smaller, it doesn\'t matter, since batchify_iterator will create in memory at each batch it yields, a list of <batch_slice> elements, once the batch consumed it freed from memory, since it\'s a generator\n',
    'author': 'Senhaji-Rhazi-Hamza',
    'author_email': 'hamza.senhajirhazi@gmal.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Senhaji-Rhazi-Hamza/bq_iterate',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8',
}


setup(**setup_kwargs)
