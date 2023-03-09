import requests
import os
import json
import shutil
import sys
import time

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
manifest_filters = [
    'https://ahikar-dev.sub.uni-goettingen.de/api/textapi/ahikar/arabic-karshuni/3r177/manifest.json',
    'https://ahikar-dev.sub.uni-goettingen.de/api/textapi/ahikar/arabic-karshuni/3r17b/manifest.json',
    'https://ahikar-dev.sub.uni-goettingen.de/api/textapi/ahikar/arabic-karshuni/3r17d/manifest.json',
    'https://ahikar-dev.sub.uni-goettingen.de/api/textapi/ahikar/arabic-karshuni/3r7vd/manifest.json',
    'https://ahikar-dev.sub.uni-goettingen.de/api/textapi/ahikar/arabic-karshuni/3r176/manifest.json',
    'https://ahikar-dev.sub.uni-goettingen.de/api/textapi/ahikar/arabic-karshuni/3r7tp/manifest.json'
]
# manifest_filters = []
crawl_annotations = True

server_base_url = 'https://ahikar-dev.sub.uni-goettingen.de/api'
output_base_url = 'http://localhost:8181/ahiqar'

for i, arg in enumerate(sys.argv):
    argNumber = i + 1

    if arg == '-c' and sys.argv[argNumber]:
        collection_url = sys.argv[argNumber]
    elif arg == '-fm' and sys.argv[argNumber]:
        manifest_filters = sys.argv[argNumber].split(',')


def crawl_collection(url):
    url_parts = url.replace(server_base_url + '/', '').split('/')

    if url_parts[-1] != 'collection.json':
        return

    url_parts.pop()

    path = output_dir + '/' + '/'.join(url_parts)

    os.makedirs(path, exist_ok=True)

    r = requests.get(url)
    collection_json = r.json()

    print('collection: ' + collection_json['title'][0]['title'])

    f = open(path + '/collection.json', 'w+')
    f.write(replace_base_url(json.dumps(collection_json)))
    f.close()

    collection_sequence = collection_json['sequence']

    if collection_json['sequence']:
        for seq_item in collection_sequence:
            if not manifest_filters or manifest_filters.count(seq_item['id']) > 0:
                crawl_manifest(seq_item['id'])


def crawl_manifest(url):
    url_parts = url.replace(server_base_url + '/', '').split('/')

    if url_parts[-1] != 'manifest.json':
        return

    dir_name = url_parts[-2]
    print('manifest: ' + dir_name)

    url_parts.pop()

    path = output_dir + '/' + '/'.join(url_parts)

    os.makedirs(path, exist_ok=True)

    r = requests.get(url)
    manifest_json = r.json()

    f = open(path + '/manifest.json', 'w+')
    f.write(replace_base_url(json.dumps(manifest_json)))
    f.close()

    sequence = manifest_json['sequence']

    if sequence:
        for i, seq_item in enumerate(sequence):
            if example_mode is False:
                crawl_item(seq_item['id'])
            else:
                if i < 2 or i > len(sequence) - 3:
                    crawl_item(seq_item['id'])


def crawl_item(url):
    url_parts = url.replace(server_base_url + '/', '').split('/')

    if url_parts[-1] != 'item.json':
        return

    item_slug = str(url_parts[-3])
    print('item: ' + item_slug)

    url_parts.pop()

    r = requests.get(url)
    item_json = None

    try:
        item_json = r.json()
    except:
        print('item:  ======== JSON parse error ========')

    if not item_json:
        return

    path = output_dir + '/' + '/'.join(url_parts)

    os.makedirs(path, exist_ok=True)

    f = open(path + '/item.json', 'w+')
    f.write(replace_base_url(json.dumps(item_json)))
    f.close()

    crawl_content(item_json['content'])

    if crawl_annotations and item_json['annotationCollection']:
        crawl_annotation_collection(item_json['annotationCollection'])


def crawl_content(content_arr):
    if not content_arr:
        return

    for content_item in content_arr:
        url = content_item['url']
        url_parts = url.replace(server_base_url + '/', '').split('/')
        content_file_name = url_parts[-1]

        r = requests.get(url)
        content = r.text

        url_parts.pop()

        path = output_dir + '/' + '/'.join(url_parts)

        os.makedirs(path, exist_ok=True)

        f = open(path + '/' + content_file_name, 'w+', encoding='utf-8')
        f.write(content)
        f.close()


def crawl_annotation_collection(url):
    url_parts = url.replace(server_base_url + '/', '').split('/')

    if url_parts[-1] != 'annotationCollection.json':
        return

    url_parts.pop()

    r = requests.get(url)
    anno_col_json = r.json()

    path = output_dir + '/' + '/'.join(url_parts)

    os.makedirs(path, exist_ok=True)

    f = open(path + '/annotationCollection.json', 'w+')
    f.write(replace_base_url(json.dumps(anno_col_json)))
    f.close()

    if anno_col_json['first']:
        crawl_annotation_page(anno_col_json['first'])


def crawl_annotation_page(url):
    url_parts = url.replace(server_base_url + '/', '').split('/')

    if url_parts[-1] != 'annotationPage.json':
        return

    url_parts.pop()

    r = requests.get(url)
    anno_page_json = r.json()

    path = output_dir + '/' + '/'.join(url_parts)

    os.makedirs(path, exist_ok=True)

    f = open(path + '/annotationPage.json', 'w+')
    f.write(replace_base_url(json.dumps(anno_page_json)))
    f.close()

def replace_base_url(data_string):
    return data_string.replace(server_base_url, output_base_url)


def main():
    # get the start time
    st = time.time()

    if os.path.exists(output_dir):
        shutil.rmtree(output_dir, ignore_errors=True)

    os.mkdir(output_dir)

    crawl_collection(collection_url)

    et = time.time()

    # get the execution time
    elapsed_time = et - st
    print('Execution time:', elapsed_time, 'seconds')


main()
