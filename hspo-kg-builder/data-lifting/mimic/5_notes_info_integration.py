import os
import argparse
import pandas as pd
from utils_ import read_json, save_json, find_json_files

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--grouped_ICD9", default=None, type=int, required=True,
                        help = "Flag to define the input data (grouped ICD9 version or non-grouped ICD9 version).")
    parser.add_argument("--umls_codes_path", default=None, type=str, required=True,
                        help = "The path where the mapped extracted UMLS codes are stored.")
    parser.add_argument("--employment_mapping_path", default=None, type=str, required=True,
                        help = "The path of the employment mapping csv file.")
    parser.add_argument("--household_mapping_path", default=None, type=str, required=True,
                        help = "The path of the household mapping csv file.")
    parser.add_argument("--housing_mapping_path", default=None, type=str, required=True,
                        help = "The path of the housing mapping csv file.")
    
    args = parser.parse_args()

    if args.grouped_ICD9:
        data_init = read_json('data/processed_data/3_data_task_valid_grouped_icd9.json')
    else:
        data_init = read_json('data/processed_data/3_data_task_valid.json')
    
    social_files = find_json_files(args.umls_codes_path)

    employment_mapping = pd.read_csv(args.employment_mapping_path)
    employment_umls_codes = employment_mapping['CUI'].tolist()
    employment_textual_description = employment_mapping['Description'].tolist()

    household_mapping = pd.read_csv(args.household_mapping_path)
    household_umls_codes = household_mapping['CUI'].tolist()
    household_textual_description = household_mapping['Description'].tolist()

    housing_mapping = pd.read_csv(args.housing_mapping_path)
    housing_umls_codes = housing_mapping['CUI'].tolist()
    housing_textual_description = housing_mapping['Description'].tolist()  

    for f in social_files:
        s_f = read_json(f)
        name = f.split('/')[-1].split('.')[0]
        k1 = name.split('_')[0]
        k2 = name.split('_')[1]
        data_init[k1][k2]['notes_info'] = {'umls_codes': s_f['umls_codes'],
                                        'textual_description': s_f['textual_description']}
        data_init[k1][k2]['social_info'] = {'employment': {'umls_codes': [],
                                                        'textual_description': []},
                                            'housing': {'umls_codes': [],
                                                        'textual_description': []},
                                            'household_composition': {'umls_codes': [],
                                                                    'textual_description': []}}
        for c in s_f['umls_codes']:
            # Treat employment codes
            try:
                employment_index = employment_umls_codes.index(c)
                data_init[k1][k2]['social_info']['employment']['umls_codes'].append(c)
                data_init[k1][k2]['social_info']['employment']['textual_description'].append(employment_textual_description[employment_index].lower())
            except:
                pass
            # Treat household
            try:
                household_index = household_umls_codes.index(c)
                data_init[k1][k2]['social_info']['household_composition']['umls_codes'].append(c)
                data_init[k1][k2]['social_info']['household_composition']['textual_description'].append(household_textual_description[household_index].lower())
            except:
                pass
            # Treat housing
            try:
                housing_index = housing_umls_codes.index(c)
                data_init[k1][k2]['social_info']['housing']['umls_codes'].append(c)
                data_init[k1][k2]['social_info']['housing']['textual_description'].append(housing_textual_description[housing_index].lower())
            except:
                pass
    
    output_path = "data/processed_data/"
    if args.grouped_ICD9:
        save_json(data_init, output_path + '4_data_after_adding_notes_info_grouped_icd9.json')
    else:
        save_json(data_init, output_path + '4_data_after_adding_notes_info.json')