#!/usr/bin/env python3
"""
Generate a test dataset.
"""
import random
import string
import uuid

import bson
import lorem
import pymongo

import config
import structure
import utils
from user import PERMISSIONS


# helper functions
def make_description():
    """
    Make a random description based on lorem ipsum.

    Returns:
       str: a random description

    """
    desc = random.choice((lorem.sentence,
                          lorem.paragraph,
                          lorem.text))()
    return desc


# generator functions

EXTRA_FIELDS = {'method': ('rna-seq', 'chip-seq', 'X-ray'),
                'external': ('company1', 'company2', 'company3')}
EXTRA_KEYS = tuple(EXTRA_FIELDS.keys())

def gen_datasets(db, nr_datasets: int = 500):
    uuids = []
    orders = [entry['_id'] for entry in db['orders'].find()]
    for i in range(1, nr_datasets+1):
        dataset = structure.dataset()
        changes = {'title': f'Dataset {i} Title',
                   'description': make_description(),
                   'links': [{'description': f'Download location {j}',
                              'url': (f'https://data_source{i}/' +
                                      f'{random.choice(string.ascii_uppercase)}')}
                                 for j in range(1, random.randint(0, 6))]}
        # add extra field
        if random.random() > 0.9:
            tag = random.choice(EXTRA_KEYS)
            changes['extra'] = [{tag: random.choice(EXTRA_FIELDS[tag])}]
        dataset.update(changes)
        uuids.append(db['datasets'].insert_one(dataset).inserted_id)
        db['orders'].update_one({'_id': random.choice(orders)},
                                {'$push': {'datasets': uuids[-1]}})

    return uuids


def gen_facilities(db, nr_facilities: int = 30):
    countries = utils.country_list()
    uuids = []
    for i in range(1, nr_facilities+1):
        user = structure.user()
        changes = {'affiliation': 'University ' + random.choice(string.ascii_uppercase),
                   'api_key': uuid.uuid4().hex,
                   'auth_id': '--facility--',
                   'country': 'Sweden',
                   'email': f'facility{i}@domain{i}',
                   'name': f'Facility {i}',
                   'permissions': ['ORDERS_SELF']}
        user.update(changes)
        uuids.append(db['users'].insert_one(user).inserted_id)

    return uuids


def gen_orders(db, nr_orders: int = 300):
    uuids = []
    facilities = tuple(db['users'].find({'auth_id': '--facility--'}))
    users = tuple(db['users'].find({'auth_id': {'$ne': '--facility--'}}))
    for i in range(1, nr_orders+1):
        receiver_type = random.choice(('email', '_id'))
        order = structure.order()
        changes = {'creator': random.choice(facilities)['_id'],
                   'description': make_description(),
                   'receiver': random.choice(users)[receiver_type],
                   'title': f'Order {i} Title'}
        order.update(changes)
        uuids.append(db['orders'].insert_one(order).inserted_id)
    return uuids


def gen_projects(db, nr_projects: int = 500):
    datasets = tuple(db['datasets'].find())
    users = tuple(db['users'].find())
    for i in range(1, nr_projects+1):
        project = structure.project()
        changes = {'contact': f'email{i}@entity{i}',
                   'description': make_description(),
                   'datasets': [random.choice(datasets)['_id']
                                for _ in range(random.randint(0, 5))],
                   'dmp': f'http://dmp-url{i}',
                   'owners': list(set(random.choice(users)[random.choice(('email', '_id'))]
                                      for _ in range(random.randint(1,3)))),
                   'publications': [{'title': f'Title {j}', 'doi': f'doi{j}'}
                                    for j in range(random.randint(0, 5))],
                   'title': f'Project {i} Title'}
        project.update(changes)
        db['projects'].insert_one(project)


def gen_users(db, nr_users: int = 100):
    uuids = []
    perm_keys = tuple(PERMISSIONS.keys())
    # non-random users with specific rights
    special_users = [{'name': 'Base Test', 'permissions': [], 'email': 'base@example.com'},
                     {'name': 'Orders Test', 'permissions': ['ORDER_SELF'], 'email': 'orders@example.com'},
                     {'name': 'Owners Test', 'permissions': ['OWNERS_READ'], 'email': 'owners@example.com'},
                     {'name': 'Users Test', 'permissions': ['USER_MANAGEMENT'], 'email': 'users@example.com'},
                     {'name': 'Data Test', 'permissions': ['DATA_MANAGEMENT'], 'email': 'data@example.com'},
                     {'name': 'Doi Test', 'permissions': ['DOI_REVIEWER'], 'email': 'data@example.com'},
                     {'name': 'Root Test', 'permissions': list(perm_keys), 'email': 'root@example.com'}]

    for i, suser in enumerate(special_users):
        user = structure.user()
        user.update(suser)
        user.update({'affiliation' : 'Test university',
                     'api_key': uuid.uuid4().hex,
                     'auth_id' : f'hash{i}@suser',
                     'country' : 'Sweden'})
        db['users'].insert_one(user)

    countries = utils.country_list()
    for i in range(1, nr_users+1-3):
        user = structure.user()
        changes = {'affiliation': 'University ' + random.choice(string.ascii_uppercase),
                   'api_key': uuid.uuid4().hex,
                   'auth_id': f'hash{i}@elixir',
                   'country': random.choice(countries),
                   'email': f'user{i}@place{i}',
                   'name': f'First Last {i}',
                   'permissions': list(set(random.choice(perm_keys)
                                           for _ in range(random.randint(0,2))))}
        user.update(changes)
        uuids.append(db['users'].insert_one(user).inserted_id)
    return uuids


if __name__ == '__main__':
    CONF = config.read_config()
    DBSERVER = pymongo.MongoClient(host=CONF['mongo']['host'],
                                   port=CONF['mongo']['port'],
                                   username=CONF['mongo']['user'],
                                   password=CONF['mongo']['password'])
    codec_options = bson.codec_options.CodecOptions(uuid_representation=bson.binary.STANDARD)
    DB = DBSERVER.get_database(CONF['mongo']['db'],
                               codec_options=(codec_options))
    gen_facilities(DB)
    gen_users(DB)
    gen_orders(DB)
    gen_datasets(DB)
    gen_projects(DB)
