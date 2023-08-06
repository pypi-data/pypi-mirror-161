
import requests
import time
from requests import Session
import json




class MetabaseSource:
    _url: str = None
    _user: str = None
    _password: str = None


    def __init__(self, url: str, user: str, password: str) -> None:
        """

        Your description goes here

        :param url: Metabase api url
        :param user: Metabase username
        :param password: Metabase password

        :return: new MetabaseApi instance
        """
        self._url = url
        self._user = user
        self._password = password

    @property
    def url(self) -> str:
        return self._url.strip("/")

    @property
    def user(self) -> str:
        return self._user

    @property
    def password(self) -> str:
        return self._password

    @property
    def session(self) -> Session:
        payload = dict(username=self.user,
                       password=self.password)

        response = requests.post(f"{self.url}/api/session",
                                 data=json.dumps(payload),
                                 headers={"Content-Type": "application/json"})

        response.raise_for_status()

        json_body = response.json()

        json_body["X-Metabase-Session"] = json_body.pop("id")
        json_body["Content-Type"] = "application/json"

        session = requests.Session()

        session.headers.update(json_body)

        return session



    def _get_data(self, endpoint, params=None, metadata=False):
        print(f"getting data from {self.url}/api/{endpoint}")
        res = self.session.get(f"{self.url}/api/{endpoint}", params=params)
        res_json = res.json()
        if isinstance(res_json, list):
            data = res_json
        else:
            if 'data' in res_json:
                data = res_json.get('data')
            else:
                data = [res_json]
        if params:
            for d in data:
                d['request_params'] = str(params)
        for row in data:
            yield row



    def _get_database_ids(self):
        databases = self._get_data('database')
        database_ids = [d['id'] for d in databases]
        return database_ids

    def _get_fields_endpoints(self):
        return [f"database/{id}/fields" for id in self._get_database_ids()]

    def _get_field_data(self):
        for p in self._get_fields_endpoints():
            data = self._get_data(p)
            for row in data:
                yield row


    def get_table_rows(self, table, params={}):
        """this function returns an interator of rows"""
        #if it's a simple call, we return the result in a list
        simple_endpoints = [dict(endpoint='util/stats', table='stats'),
                     dict(endpoint='card', table='cards'),
                     dict(endpoint='collection', table='collections'),
                     dict(endpoint='dashboard', table='dashboards'),
                     dict(endpoint='database', table='databases'),
                     dict(endpoint='metric', table='metrics'),
                     dict(endpoint='pulse', table='pulses'),
                     dict(endpoint='table', table='tables'),
                     dict(endpoint='segment', table='segments'),
                     dict(endpoint='user', table='users', params={'status': 'all'}),
                     dict(endpoint='activity', table='activity'),
                     dict(endpoint='util/logs', table='logs'),
                     ]
        if table in [e['table'] for e in simple_endpoints]:
            endpoint = [d for d in simple_endpoints if table == d['table']][0]
            data = self._get_data(endpoint.get('endpoint'), params=endpoint.get('params'))
            return data

        #for tables that need more calls, we return a generator
        if table == 'fields':
            return self._get_field_data()

    def tables(self, params={}):
        """
         A list of tables that can be passed to get_table_rows() to get an interator of rows

            Metabase publishes logs to a buffer that keeps a running window.
            depending on how many events are generated in your instance,
            you might want to schedule a read every few minutes or every few days.

            They are set to "append-only" mode, so deduplication will be done by you by your optimal cost scenario
            event_window_tables = ['activity', 'logs']


            pass them to get_endpoint_rows() to get an iterator of rows.
            These are stateful and should be replaced
            stateful_tables = ['stats', 'cards', 'collections', 'dashboards', 'databases',
                           'metrics', 'pulses', 'tables', 'segments', 'users', 'fields']
            returns a list of available tasks (to get data sets).
        """
        table_names = ['activity', 'logs',
                  'stats', 'cards', 'collections', 'dashboards', 'databases',
                  'metrics', 'pulses', 'tables', 'segments', 'users', 'fields']

        _tables = [{'table_name':t, 'data': self.get_table_rows(t, params=params)} for t in table_names]
        return _tables


if __name__ == "__main__":
    # you can consume the generators as below
    m = MetabaseSource(url ='', user='', password='')
    ts = m.tables()
    for t in ts:
        print(t)
        data_generator = t['data']
        #for row in data_generator:
        #    pass
        #    # do something
        #    # to see the data just look at the sample files perhaps

    """
    {'table_name': 'activity', 'data': <generator object MetabaseSource._get_data at 0x1022ce660>}
    {'table_name': 'logs', 'data': <generator object MetabaseSource._get_data at 0x1022cea50>}
    {'table_name': 'stats', 'data': <generator object MetabaseSource._get_data at 0x1022ceac0>}
    {'table_name': 'cards', 'data': <generator object MetabaseSource._get_data at 0x1022ceba0>}
    {'table_name': 'collections', 'data': <generator object MetabaseSource._get_data at 0x1022cec80>}
    {'table_name': 'dashboards', 'data': <generator object MetabaseSource._get_data at 0x1022cecf0>}
    {'table_name': 'databases', 'data': <generator object MetabaseSource._get_data at 0x1022ced60>}
    {'table_name': 'metrics', 'data': <generator object MetabaseSource._get_data at 0x1022cedd0>}
    {'table_name': 'pulses', 'data': <generator object MetabaseSource._get_data at 0x1022cee40>}
    {'table_name': 'tables', 'data': <generator object MetabaseSource._get_data at 0x1022ceeb0>}
    {'table_name': 'segments', 'data': <generator object MetabaseSource._get_data at 0x1022cef20>}
    {'table_name': 'users', 'data': <generator object MetabaseSource._get_data at 0x1022cef90>}
    {'table_name': 'fields', 'data': <generator object MetabaseSource._get_field_data at 0x1022f1040>}
    """
