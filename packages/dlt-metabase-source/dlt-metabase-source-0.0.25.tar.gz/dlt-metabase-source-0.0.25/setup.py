# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dlt_metabase_source', 'dlt_metabase_source.sample_data']

package_data = \
{'': ['*'], 'dlt_metabase_source': ['example_schemas/*']}

install_requires = \
['google-cloud-bigquery', 'psycopg2-binary', 'python-dlt']

setup_kwargs = {
    'name': 'dlt-metabase-source',
    'version': '0.0.25',
    'description': '',
    'long_description': '# dlt-metabase-source\n\n\n# Parent tables \n\n\nStateful tables: these get replaced on each load\n```\n\'stats\', \'cards\', \'collections\', \'dashboards\', \'databases\', \'metrics\', \'pulses\',\n\'tables\', \'segments\', \'users\', \'fields\'\n  ```               \nAppend (event) tables: these endpoints buffer a small event window, you need to merge it afterwards\n\nto do - add time filter parameters to only load filtered requested data.\n```\n\'activity\', \'logs\'\n\n```\nsome of these tables have sub-tables\n\nto join the parent table to the sub table, use the join `parent.dlt_id = child.parent_dlt_id`\n\n# Usage\n\noptionally Create a virtual environment\n```\npython3 -m venv ./dlt_metabase_env4\nsource ./dlt_metabase_env4/bin/activate\n```\n\ninstall library\n\n```pip install dlt-metabase-source```\n\nIf the library cannot be found, ensure you have the required python version as per the `pyproject.toml`file.\n(3.8+)\n\nYou can run the snippet file below to load a sample data set. \nYou would need to add your target credentials first.\n\n```python run_load.py```\n\nFirst, import the loading method and add your credentials\n\n```\nfrom dlt_metabase_source import load\n\n\n# target credentials\n# example for bigquery\ncreds = {\n  "type": "service_account",\n  "project_id": "zinc-mantra-353207",\n  "private_key_id": "example",\n  "private_key": "",\n  "client_email": "example@zinc-mantra-353207.iam.gserviceaccount.com",\n  "client_id": "100909481823688180493"}\n  \n# or example for redshift:\n# creds = ["redshift", "database_name", "schema_name", "user_name", "host", "password"]\n```\nMetabase credentials\n```\n\nurl=\'http....com\',\nuser=\'example@ai\',\npassword=\'dolphins\',\n\n\n```\n\n\nNow, you can use the code below to do a serial load:\n\n`mock_data=True` flag below will load sample data.\n\nRemove or set to False the `mock_data` flag to enable loading your data.\n\n```\n# remove some tables from this list of you only want some endpoints\ntables=[\'activity\', \'logs\', \'stats\', \'cards\', \'collections\', \'dashboards\', \'databases\', \'metrics\', \'pulses\',\n                 \'tables\', \'segments\', \'users\', \'fields\']\n                 \nload(url=url,\n         user=user\',\n         password=password,\n         target_credentials=creds,\n         tables=tables,\n         schema_name=\'metabase\',\n         mock_data=True)\n\n```\nor, for parallel load, create airflow tasks for each table like so:\n```\n\nfor table in tables:\n    load(url=url,\n         user=user\',\n         password=password,\n         target_credentials=creds,\n         tables=[table],\n         schema_name=\'metabase\',\n         mock_data=True)\n\n```\n\nIf you want to do your own pipeline or consume the source differently:\n```\nfrom dlt_metabase_source import MetabaseSource, MetabaseMockSource\n\nprod = MetabaseSource(url=\'http....com\',\n         user=\'example@ai\',\n         password=\'dolphins\')\n              \ndummy = PersonioSourceDummy()\n\nsample_data = dummy.tasks() \n\nfor task in tasks:\n    print(task[\'table_name\'])\n    for row in task[\'data\']\n        print(row)\n\n```',
    'author': 'Adrian Brudaru',
    'author_email': 'adrian@scalevector.ai',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
