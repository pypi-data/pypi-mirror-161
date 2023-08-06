
from dlt.pipeline import Pipeline
# from dlt.pipeline.typing import GCPPipelineCredentials,  PostgresPipelineCredentials
import os
from metabase_source import MetabaseSource as DataSource
from mock_source import MockDataSource as MDataSource

"""
This utility extracts the schema of your data streams or tables.
"""

#metabase creds
url = ''
user = ''
password = ''

schema_file_name = 'schema'

source = MDataSource(url=url, user=user, password=password) # optionally mock DataSource

# here you can filter by removing from the tables list
tables = ['activity', 'logs', 'stats',
          'cards', 'collections', 'dashboards', 'databases', 'metrics', 'pulses',
          'tables', 'segments', 'users', 'fields'
          ]

tables_to_load = [t for t in source.tables() if t['table_name'] in tables]



def extract_schema(tables_to_load, schema_file_name, schema_name='metabase'):

    # --- DLT - related code below
    # fix a path to schema
    current_path = os.path.dirname(os.path.realpath(__file__))
    schema_file_path = os.path.join(current_path, f"{schema_file_name}.yml")
    # read schema if exists
    try:
        schema = Pipeline.load_schema_from_file(schema_file_path)
    except FileNotFoundError:
        schema = None

    # make pipeline if none was passed. Initiate with fake creds and set them later
    p = Pipeline(schema_name)
    # try which credential package is installed and make dummies
    try:
        from dlt.pipeline.typing import GCPPipelineCredentials
        credentials = {"type": "service_account", "project_id": "", "private_key_id": "",
                       "private_key": "", "client_email": "", "client_id": ""}
        cred_obj = GCPPipelineCredentials.from_services_dict(credentials, dataset_prefix='dlt')
    except ImportError:
        try:
            from dlt.pipeline.typing import PostgresPipelineCredentials
            credentials = ["redshift", "database_name", "schema_name", "user_name", "host", "password"]
            cred_obj = PostgresPipelineCredentials(*credentials)
        except ImportError:
            raise Exception('Error, no destination package found, please install the redshift or bigquery destination packages')

    # now create a pipeline
    p.create_pipeline(cred_obj, schema=schema)

    # now extract schema for each table
    for table in tables_to_load:
        #get actual data
        p.extract(table['data'], table_name=table['table_name'])
        #normalise the data into flat tables
        p.unpack()

    # if schema changed, update it.
    new_schema = p.get_default_schema().as_yaml(remove_defaults=True)

    if schema == new_schema:
        print('no schema changes detected')
    else:
        # save_schema
        f = open(schema_file_path, "w")
        f.write(new_schema)
        f.close()
        print('schema changes detected, schema file updated.')


extract_schema(tables_to_load, schema_file_name)