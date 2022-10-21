import requests
import os
import json
import shutil
import numpy as np

collection_url = 'https://ahiqar.uni-goettingen.de/api/textapi/ahikar/arabic-karshuni/collection.json'

output_dir = 'output'
collections_dir = 'collections'
manifests_dir = 'manifests'
items_dir = 'items'


def crawl_item(url):
    url_arr = url.split('/')
    if url_arr[len(url_arr) - 1] != 'item.json' and url_arr[len(url_arr) - 2] != 'latest':
        return

    item_name = url_arr[len(url_arr) - 3]

    print('item: ' + item_name)

    path = output_dir + '/' + items_dir + '/' + item_name
    os.makedirs(path, exist_ok=True)

    r = requests.get(url)
    try:
        item_json = r.json()
        f = open(path + '/item.json', 'w+')
        f.write(json.dumps(item_json))
    except:
        print('item: JSON parse error')


def crawl_manifest(url):
    url_arr = url.split('/')
    if url_arr[len(url_arr) - 1] != 'manifest.json':
        return

    dir_name = url_arr[len(url_arr) - 2]
    print('manifest:' + dir_name)

    path = output_dir + '/' + manifests_dir + '/' + dir_name
    os.makedirs(path, exist_ok=True)

    r = requests.get(url)
    manifest_json = r.json()

    f = open(path + '/manifest.json', 'w+')
    f.write(json.dumps(manifest_json))

    sequence = manifest_json['sequence']

    if sequence:
        if not isinstance(sequence, (list, tuple, np.ndarray)):
            sequence = [sequence]

        for seq_item in sequence:
            crawl_item(seq_item['id'])


def crawl_collection(url):
    path = output_dir + '/' + collections_dir
    os.makedirs(path, exist_ok=True)

    r = requests.get(url)
    collection_json = r.json()

    print('collection:' + collection_json['title'][0]['title'])

    f = open(path + '/collection.json', 'w+')
    f.write(json.dumps(collection_json))

    collection_sequence = collection_json['sequence']

    if collection_json['sequence']:
        for seq_item in collection_sequence:
            crawl_manifest(seq_item['id'])


def main():
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir, ignore_errors=True)

    os.mkdir(output_dir)
    crawl_collection(collection_url)


main()