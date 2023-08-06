from metabase_source import MetabaseSource as DataSource
import jsonlines

"""
This utility runs the data source extractor and writes the data to files in the sample_data folder
From here the data is automatically used to populate the mock source tables().
If you publish the source, take care that the data does not contain "Personally Identifiable Information"
"""

metabase_creds = dict(url='https://metabase-analytics.scalevector.ai/',
                 user='example@scalevector.ai',
                 password='')

s = DataSource(**metabase_creds)

tables = s.tables()

for table in tables:
    with jsonlines.open(f"test/{table['table_name']}.jsonl", mode='w') as writer:
        writer.write_all(table['data'])


