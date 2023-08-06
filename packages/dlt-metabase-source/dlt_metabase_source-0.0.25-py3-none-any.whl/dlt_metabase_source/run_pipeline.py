"""
This is a simple pipeline that you can use without further configuration.
If you want to parallelise the load or do a different workflow, create your own pipeline.
"""

from dlt_metabase_source._helpers import extract_data_and_prepare_schema, load_data
from dlt_metabase_source.metabase_source import MetabaseSource as DataSource
from dlt_metabase_source.mock_source import MockDataSource


def load(url='https://metabase-analytics.scalevector.com/',
         user='example1@scalevector.ai',
         password='',
         # for target credentials, pass a client_secrets.json or a credential json suitable for your db type.
         target_credentials={},
         #default tables, remove some if you do not want all of them
         tables=['activity', 'logs', 'stats', 'cards', 'collections', 'dashboards', 'databases', 'metrics', 'pulses', 'tables', 'segments', 'users', 'fields'],
         schema_name = 'metabase',
         mock_data = False):

    if mock_data:
        source = MockDataSource(url='', user='', password='')
    else:
        source = DataSource(url=url, user=user, password=password)

    tables_to_load = [t for t in source.tables() if t['table_name'] in tables]


    pipeline = None
    for table in tables_to_load:
        #add data to pipeline
        pipeline = extract_data_and_prepare_schema(pipeline,
                                        table['data'],
                                        #target creds will be moved to load
                                        credentials=target_credentials,
                                        table_name=table['table_name'],
                                        schema_file='schema',
                                        update_schema=False)
    #now load the data
    load_data(pipeline, credentials = target_credentials,
                  dataset_prefix='dlt',
                  dataset_name=schema_name)

    print(f"loaded {','.join(tables)}")


if __name__ == "__main__":

    load(url='ht',
         user='e.ai',
         password='',
         # for target credentials, pass a client_secrets.json or a credential json suitable for your db type.
         target_credentials={"type": "service_account",
                  "project_id": "zinc-mantra-353207",
                  "private_key_id": "ffff",
                  "private_key": "ffff",
                  "client_email": "data-load-tool@zinc-mantra-353207.iam.gserviceaccount.com",
                  "client_id": "100909481823688180493"},
         # default tables, remove some if you do not want all of them
         tables=['activity', 'logs', 'stats', 'cards', 'collections', 'dashboards', 'databases', 'metrics', 'pulses',
                 'tables', 'segments', 'users', 'fields'],
         schema_name='metabase',
         mock_data=True)



