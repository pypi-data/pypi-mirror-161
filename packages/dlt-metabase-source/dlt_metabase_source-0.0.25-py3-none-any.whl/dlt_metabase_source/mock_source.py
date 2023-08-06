import jsonlines
from typing import Iterator

from dlt.common import json
from dlt.common.typing import DictStrAny, StrOrBytesPath

from os import listdir
from os.path import isfile, join
import os

current_path = os.path.dirname(os.path.abspath(__file__))
data_folder_path = join(current_path, 'sample_data')
metabase_files = [join(data_folder_path, f) for f in listdir(data_folder_path) if isfile(join(data_folder_path, f)) ]


class MockDataSource:

        """ you can use this class to yield "tables" from the "sample_data" folder with json files """

        def __init__(self, url: str, user: str, password: str) -> None:
            pass

        def get_file_names(self):
            current_path = os.path.dirname(os.path.abspath(__file__))
            data_folder_path = join(current_path, 'sample_data')
            files = [join(data_folder_path, f) for f in listdir(data_folder_path) if isfile(join(data_folder_path, f))]
            return files

        def get_table_rows(self, tablename: StrOrBytesPath) -> Iterator[DictStrAny]:
            current_path = os.path.dirname(os.path.abspath(__file__))
            data_folder_path = os.path.join(current_path, 'sample_data')
            file_path = os.path.join(data_folder_path, f'{tablename}')
            with open(file_path, "r", encoding="utf-8") as f:
                yield from jsonlines.Reader(f, loads=json.loads)

        def tables(self):
            files = self.get_file_names()
            _tables = [dict(table_name = os.path.basename(f.replace('.jsonl', '')),
                         data = self.get_table_rows(os.path.basename(f)))
                    for f in files]

            return _tables