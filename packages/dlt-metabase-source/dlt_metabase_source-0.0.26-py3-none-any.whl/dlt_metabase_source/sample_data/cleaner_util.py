import jsonlines
import json

def read_file(fn):
    with open(f'{fn}.jsonl', "r", encoding="utf-8") as f:
            yield from jsonlines.Reader(f, loads=json.loads)

def write_file(data, fn):
    with jsonlines.open(f'{fn}_cleaned.jsonl', mode='w') as writer:
        writer.write_all(data)

def get_columns(fn):
    columns = set()
    for row in read_file(fn):
        for key in row.keys():
            columns.add(key)
    return columns

def get_sensitive_columns(fn, columns):
    out = []
    for row in read_file(fn):
        newrow = {}
        for c in columns:
            newrow[c]=row[c]
        out.append(newrow)
    return out

def merge_back_sensitive_columns(original_data, edited_data, join_col):
    out_data = []
    for o_row in original_data:
        update_row = [row for row in edited_data if row[join_col] == o_row[join_col]][0]
        o_row.update(update_row)
        out_data.append(o_row)
    return out_data


user_data = [
{'first_name': 'Fran', 'id': 10, 'common_name': 'normal person', 'email': 'fran.g.pani@johndoes.com', 'last_name': 'Pani'},
{'first_name': 'Lemon', 'id': 2, 'common_name': 'Lemon Husk', 'email': 'lemon.husk@johndoes.com', 'last_name': 'Husk'},
{'first_name': 'Bees', 'id': 15, 'common_name': 'Bees Wishes', 'email': 'bees.wishes@johndoes.ai', 'last_name': 'Wishes'},
{'first_name': 'Paige', 'id': 18, 'common_name': 'Paige Turner', 'email': 'paige.turner@johndoes.com', 'last_name': 'Turner'},
{'first_name': 'Tim', 'id': 7, 'common_name': 'Tim Toast', 'email': 'timothy.toast@johndoes.com', 'last_name': 'Toast'},
{'first_name': 'JJ', 'id': 8, 'common_name': 'JJ', 'email': 'john.jinja@johndoes.ai', 'last_name': 'Jinja'},
{'first_name': 'Just', 'id': 11, 'common_name': 'Just bowling', 'email': 'justwent.bowling@johndoes.ai', 'last_name': 'bowling'},
{'first_name': 'Barren', 'id': 17, 'common_name': 'Barren socket', 'email': 'barren.socket@johndoes.com', 'last_name': 'socket'},
{'first_name': 'Rod', 'id': 3, 'common_name': 'Rod knee', 'email': 'rod.knee@johndoes.com', 'last_name': 'knee'},
{'first_name': 'Box', 'id': 5, 'common_name': 'Box tobacco', 'email': 'box.tobacco@johndoes.com', 'last_name': 'tobacco'},
{'first_name': 'Dan', 'id': 9, 'common_name': 'Dan dangerous', 'email': 'dan.dangerous@johndoes.ai', 'last_name': 'dangerous'},
{'first_name': 'Jane', 'id': 6, 'common_name': 'Jane just', 'email': 'jane.just@johndoes.com', 'last_name': 'just'},
{'first_name': 'Ai', 'id': 12, 'common_name': 'Ai test', 'email': 'ai.v7.14@johndoes.ai', 'last_name': 'test'},
{'first_name': 'Allie', 'id': 13, 'common_name': 'Alligator', 'email': 'allie.gater@johndoes.com', 'last_name': 'gater'},
{'first_name': 'Peg', 'id': 14, 'common_name': 'Peg legge', 'email': 'peg.legge@johndoes.com', 'last_name': 'legge'},
{'first_name': 'Patty', 'id': 1, 'common_name': 'Patty furniture', 'email': 'patty.furniture@johndoes.com', 'last_name': 'furniture'},
{'first_name': 'John', 'id': 16, 'common_name': 'John varnish', 'email': 'john.varnish@johndoes.com', 'last_name': 'varnish'},
{'first_name': 'Willhe', 'id': 4, 'common_name': 'Willhe findit', 'email': 'willhe.findit@johndoes.ai', 'last_name': 'findit'}
]


def update_activity(u_data):
    data = read_file('activity')
    out_data = []
    for o_row in data:
        update_row = [row for row in u_data if row['id'] == o_row['user_id']][0]
        o_row['user'].update(update_row)
        out_data.append(o_row)
    write_file(out_data, 'activity')

def update_cards(u_data):
    data = read_file('cards')
    out_data = []
    for o_row in data:
        update_row = [row for row in u_data if row['id'] == o_row['creator']['id']][0]
        o_row['creator'].update(update_row)
        out_data.append(o_row)
    write_file(out_data, 'cards')

from slugify import slugify

def update_collections(u_data):
    data = read_file('collections')
    out_data = []
    for o_row in data:
        if o_row.get('personal_owner_id'):
            update_row = [row for row in u_data if row['id'] == o_row.get('personal_owner_id')][0]
            o_row['name'] = f"{update_row['common_name']}'s Personal Collection"
            o_row['slug'] = slugify(f"{update_row['common_name']}'s Personal Collection")
        out_data.append(o_row)
    write_file(out_data, 'collections')

def update_dashboards(u_data):
    data = read_file('dashboards')
    out_data = []
    for o_row in data:
        update_row = [row for row in u_data if row['id'] == o_row['creator']['id']][0]
        o_row['creator'].update(update_row)
        out_data.append(o_row)
    write_file(out_data, 'dashboards')

update_dashboards(user_data)