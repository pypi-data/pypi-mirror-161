from dlt.pipeline import Pipeline
import os

"""experimental utilities to support varying workflows"""

def save_schema(schema_yaml, fn):
    current_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(current_path, f"{fn}.yml")
    f = open(file_path, "w")
    f.write(schema_yaml)
    f.close()

def read_schema(fn):
    current_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(current_path, f"{fn}.yml")
    schema = Pipeline.load_schema_from_file(file_path)
    return schema

def make_credentials_object(credentials):
    if isinstance(credentials, dict):
        try:
            from dlt.pipeline.typing import GCPPipelineCredentials
            cred_obj = GCPPipelineCredentials.from_services_dict(credentials, dataset_prefix='dlt')
        except ImportError as e:
            raise Exception(f'{e} Error, no destination package found, install relevant destination packages')
    elif isinstance(credentials, list):
        if credentials[0] == 'redshift':
            try:
                from dlt.pipeline.typing import PostgresPipelineCredentials
                cred_obj = PostgresPipelineCredentials(*credentials)
            except ImportError as e:
                raise Exception(f'{e} Error, no destination package found, install relevant destination packages')
    return cred_obj


def extract_data_and_prepare_schema(pipeline, data, credentials, table_name=None, schema_file=None, update_schema=True, dataset_name='dlt_source_extractor'):

    if schema_file:
        try:
            schema = read_schema(schema_file)
        except FileNotFoundError:
            current_path = os.path.dirname(os.path.realpath(__file__))
            file_path = os.path.join(current_path, f"{schema_file}.yml")
            print(f'Schema file does not exist at location {file_path}, creating...')
            schema = None
    else:
        schema= None

    # make pipeline if none was passed. Initiate with fake creds and set them later
    if pipeline is None:
        p = Pipeline(dataset_name)
        cred = make_credentials_object(credentials)
        p.create_pipeline(cred, schema=schema)
    else:
        p = pipeline
    p.extract(data, table_name=table_name)
    p.unpack()
    new_schema = p.get_default_schema().as_yaml(remove_defaults=True)
    if schema == new_schema:
        print('no schema changes detected')
    elif update_schema:
        save_schema(new_schema, schema_file)
        print('schema changes detected, schema file updated.')
    else:
        print('schema changes detected but not saved.')
    return p


def load_data(pipeline, credentials = {}, dataset_prefix='dlt', dataset_name='dlt_source_extractor'):
    #pipeline.credentials = make_credentials_object(credentials)
    # set pipeline name, which together with dataset_prefix becomes the schema name
    pipeline.pipeline_name = dataset_name
    #load
    pipeline.load()

