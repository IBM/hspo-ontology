import pandas as pd
import os
import json

def read_csv(path):
    return pd.read_csv(path)


def read_json(path):
        with open(path) as json_file:
            return json.load(json_file)


def save_json(file, path):
    with open(path, 'w') as outfile:
        json.dump(file, outfile)


def find_json_files(folder_path):
    files = []
    for file in os.listdir(folder_path):
        if file.endswith(".json"):
            files.append(file.split('.')[0])
    return files


def remove_empty_strings(text):
        clean_text = []
        for r in text.split('\n'):
            if r == '':
                continue
            else:
                clean_text.append(r)
        return clean_text
