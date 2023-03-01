import requests
import os
import json
import shutil
import numpy as np
import sys

# If True the crawler does not iterate over the complete collections, manifests and items but rather
# only a small portion of the endpoints to just get an idea of how the API is structured.
# This can be useful when you quickly want to create integration or end-to-end tests for your application and need some
# real world data.

example_mode = True

collection_url = 'https://ahikar-dev.sub.uni-goettingen.de/api/textapi/ahikar/arabic-karshuni/collection.json'

output_dir = 'output'
collections_dir = 'collections'
manifests_dir = 'manifests'
items_dir = 'items'
manifest_filters = []
crawl_annotations = True

for i, arg in enumerate(sys.argv):
    argNumber = i + 1

    if arg == '-c' and sys.argv[argNumber]:
        collection_url = sys.argv[argNumber]
    elif arg == '-fm' and sys.argv[argNumber]:
        manifest_filters = sys.argv[argNumber].split(',')


def crawl_item(url, parent_path):
    url_arr = url.split('/')
    if url_arr[len(url_arr) - 1] != 'item.json' and url_arr[len(url_arr) - 2] != 'latest':
        return

    item_name = url_arr[len(url_arr) - 3]
    revision = url_arr[len(url_arr) - 2]

    print('item: ' + item_name)

    path = parent_path + '/' + item_name + '/' + revision
    os.makedirs(path, exist_ok=True)

    r = requests.get(url)
    try:
        item_json = r.json()
        f = open(path + '/item.json', 'w+')
        f.write(json.dumps(item_json))

        if crawl_annotations and item_json['annotationCollection']:
            crawl_annotation_collection(item_json['annotationCollection'], path)
    except:
        print('item: JSON parse error')


def crawl_manifest(url, parent_path):
    url_arr = url.split('/')
    if url_arr[len(url_arr) - 1] != 'manifest.json':
        return

    dir_name = url_arr[len(url_arr) - 2]
    print('manifest:' + dir_name)

    path = parent_path + '/' + dir_name
    os.makedirs(path, exist_ok=True)

    r = requests.get(url)
    manifest_json = r.json()

    f = open(path + '/manifest.json', 'w+')
    f.write(json.dumps(manifest_json))

    sequence = manifest_json['sequence']

    if sequence:
        for i, seq_item in enumerate(sequence):
            if example_mode is False:
                crawl_item(seq_item['id'], path)
            else:
                if i < 3:
                    crawl_item(seq_item['id'], path)


def crawl_collection(url):
    url_arr = url.split('/')
    dir_name = url_arr[len(url_arr) - 2]

    path = output_dir + '/' + dir_name
    os.makedirs(path, exist_ok=True)

    r = requests.get(url)
    collection_json = r.json()

    print('collection:' + collection_json['title'][0]['title'])

    f = open(path + '/collection.json', 'w+')
    f.write(json.dumps(collection_json))

    collection_sequence = collection_json['sequence']

    if collection_json['sequence']:
        for seq_item in collection_sequence:
            if manifest_filters.count(seq_item['id']) > 0:
                crawl_manifest(seq_item['id'], path)


def crawl_annotation_collection(url, parent_path):
    r = requests.get(url)
    anno_col_json = r.json()
    f = open(parent_path + '/annotationCollection.json', 'w+')
    f.write(json.dumps(anno_col_json))

    if anno_col_json['first']:
        crawl_annotation_page(anno_col_json['first'], parent_path)


def crawl_annotation_page(url, parent_path):
    r = requests.get(url)
    anno_page_json = r.json()
    f = open(parent_path + '/annotationPage.json', 'w+')
    f.write(json.dumps(anno_page_json))


def main():
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir, ignore_errors=True)

    os.mkdir(output_dir)
    crawl_collection(collection_url)


main()
