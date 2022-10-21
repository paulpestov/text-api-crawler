import requests
import os
import json
import shutil

collection_url = 'https://ahiqar.uni-goettingen.de/api/textapi/ahikar/arabic-karshuni/collection.json'

output_dir = 'output'
collections_dir = 'collections'
manifests_dir = 'manifests'
items_dir = 'items'
collections_path = output_dir + '/' + collections_dir


def crawl_manifest(url):
    url_arr = url.split('/')
    if url_arr[len(url_arr) - 1] != 'manifest.json':
        return

    dir_name = url_arr[len(url_arr) - 2]

    path = output_dir + '/' + manifests_dir + '/' + dir_name
    os.makedirs(path, exist_ok=True)

    r = requests.get(url)
    manifest_json = r.json()

    f = open(path + '/manifest.json', 'w+')
    f.write(json.dumps(manifest_json))


if os.path.exists(output_dir):
    shutil.rmtree(output_dir, ignore_errors=True)

os.mkdir(output_dir)

if not os.path.exists(collections_dir):
    os.mkdir(collections_path)

r = requests.get(collection_url)
collection_json = r.json()

f = open(collections_path + '/collection.json', 'w+')
f.write(json.dumps(collection_json))

collection_sequence = collection_json['sequence']

for seq_item in collection_sequence:
    crawl_manifest(seq_item['id'])
    print(seq_item)




# def print_hi(name):
#     # Use a breakpoint in the code line below to debug your script.
#     print(f'Hi, {name}')  # Press Strg+F8 to toggle the breakpoint.
#
#
# # Press the green button in the gutter to run the script.
# if __name__ == '__main__':
#     print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
