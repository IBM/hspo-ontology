import pandas as pd
import argparse
import os
from utils_ import read_csv, save_json, find_json_files, remove_empty_strings


def dataframe_to_dictionary_notes(df):
    notes_dict = {}
    for _, row in df.iterrows():
        if str(row['subject_id']) + '_' + str(int(float(row['hadm_id'])))  not in notes_dict.keys():
            clean_text = remove_empty_strings(row['text'])
            notes_dict[str(row['subject_id']) + '_' + str(int(float(row['hadm_id'])))] = []
            notes_dict[str(row['subject_id']) + '_' + str(int(float(row['hadm_id'])))].extend(clean_text)
        else:
            # If there is a key for this subject_id + admission_id combination then extend the note list.
            clean_text = remove_empty_strings(row['text'])
            notes_dict[str(row['subject_id']) + '_' + str(int(float(row['hadm_id'])))].extend(clean_text)
    return notes_dict


def join_notes(dict_):
    parser = argparse.ArgumentParser()
    parser.add_argument("--bucket_size", default=1000, type=int, required=True,
                        help = "The size for each bucket of notes.")
    
    args = parser.parse_args()

    notes_dict_joined = {}
    for k in dict_.keys():
        joined_text_0 = ' '.join(dict_[k])
        joined_text_1 = joined_text_0.replace('__', ' ')
        joined_text_2 = joined_text_1.replace('  ', '')
        joined_text_3 = joined_text_2.replace('  ', '')
        joined_text_4 = joined_text_3.replace('  ', '')
        joined_text_5 = joined_text_4.replace('*', '')
        joined_text_6 = joined_text_5.replace('|', '')
        notes_dict_joined[k] = joined_text_6
    return notes_dict_joined


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--bucket_size", default=1000, type=int, required=False,
                        help = "The size of each bucket of notes.")
    
    args = parser.parse_args()

    notes = read_csv('../data/selected_data/noteevents.csv')
    notes_clear = notes.dropna(subset=['hadm_id'])
    notes_dict = dataframe_to_dictionary_notes(notes_clear)
    notes_dict_joined = join_notes(notes_dict)
    file_names = list(notes_dict.keys())

    umls_codes_path = '../data/processed_data/umls_codes_notes/'
    if not os.path.exists(umls_codes_path):
        os.makedirs(umls_codes_path)
    files_done = find_json_files(umls_codes_path)

    print("Number of processed notes: {}" .format(len(files_done)))

    files_to_be_done = []
    for f in file_names:
        if f not in files_done:
            files_to_be_done.append(f)

    print("Number of notes to be processed: {}" .format(len(files_to_be_done)))
    
    chunks = []
    for i in range(0, len(files_to_be_done), args.bucket_size):
        chunks.append({'filenames': files_to_be_done[i:i+args.bucket_size]}) 

    
    bucket_path = '../data/processed_data/filenames_notes/'
    if not os.path.exists(bucket_path):
        os.makedirs(bucket_path)
    files_done = find_json_files(bucket_path)

    for i, l in enumerate(chunks):
        save_json(l, bucket_path + 'bucket_' + str(i) + '.json')

    for i, c in enumerate(chunks):
        tmp_dict_notes = {}
        for k in c['filenames']:
            tmp_dict_notes[k] = notes_dict_joined[k]
        save_json(tmp_dict_notes, bucket_path + 'notes_bucket_' + str(i) + '.json')
