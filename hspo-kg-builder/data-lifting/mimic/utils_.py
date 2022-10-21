import pandas as pd
import json
import os

def read_csv(path):
    return pd.read_csv(path, dtype = str)

def read_json(path):
        with open(path) as json_file:
            return json.load(json_file)

def save_json(file, path):
    with open(path, 'w') as outfile:
        json.dump(file, outfile)

def convert_to_str(l):
    l_str = [str(it) for it in l]
    return l_str

def find_json_files(folder_path):
    files = []
    for file in os.listdir(folder_path):
        if file.endswith(".json"):
            files.append(os.path.join(folder_path, file))
    return files