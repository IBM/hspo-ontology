from utils_ import read_csv, read_json, save_json, convert_to_str
import pandas as pd

def find_black_list(data, codes, key_name):
    black_list = []
    for k in data.keys():
        for l_ in data[k][key_name]['icd9_code']:
            for it in l_:
                if it not in codes:
                    if it not in black_list:
                        black_list.append(it)  

    return black_list


def find_black_list_second_level(old_black_list, codes):
    black_list = []
    for c in old_black_list:
        if c not in codes:
            black_list.append(c)  

    return black_list


def mapping_to_dictionary(data, codes, descriptions, key_name):
    for k in data.keys():
        data[k][key_name]['textual_description'] = []
        for l_ in data[k][key_name]['icd9_code']:
            tmp_l = []
            for it in l_:
                ind = codes.index(it)
                tmp_l.append(descriptions[ind])

            data[k][key_name]['textual_description'].append(tmp_l)

    
def mapping_to_dictionary_two_levels(data, codes1, descriptions1, key_name, codes2, descriptions2):
    for k in data.keys():
        data[k][key_name]['textual_description'] = []
        for l_ in data[k][key_name]['icd9_code']:
            tmp_l = []
            for it in l_:
                try:
                    ind = codes1.index(it)
                    tmp_l.append(descriptions1[ind])
                except:
                    ind = codes2.index(it)
                    tmp_l.append(descriptions2[ind])

            data[k][key_name]['textual_description'].append(tmp_l)


def get_codes_descr(dict_):
        codes = []
        descr = []
        for l in dict_:
            for d in l:
                if d['code'] == None or '-' in d['code'] or d['code'] in codes:
                    continue
                else:
                    codes.append(d['code'].replace('.', ''))
                    descr.append(d['descr'].lower())
        return codes, descr


if __name__ == '__main__':
    output_path = 'data/processed_data/'
    data = read_json('data/processed_data/1_data_after_data_wrangling_grouped_icd9.json')

    ## Mapping diagnoses
    d_icd_diagnoses = read_csv('data/dictionaries/D_ICD_DIAGNOSES_updated.csv')
    icd_codes_diagnoses = convert_to_str(d_icd_diagnoses['icd9_code'.upper()].tolist())
    black_list_icd_diagnoses = find_black_list(data, icd_codes_diagnoses, 'diagnoses')
    
    codes_diag = read_json('data/dictionaries/codes_diag_updated.json')
    codes_diagnoses, descr_diagnoses = get_codes_descr(codes_diag)
    new_black_list_icd_diagnoses = find_black_list_second_level(black_list_icd_diagnoses, codes_diagnoses)
    long_title_diagnoses = d_icd_diagnoses['long_title'.upper()].tolist()
    mapping_to_dictionary_two_levels(data, icd_codes_diagnoses, 
                                     long_title_diagnoses, 'diagnoses', 
                                     codes_diagnoses, descr_diagnoses)

    # Mapping procedures
    d_icd_procedures = read_csv('data/dictionaries/D_ICD_PROCEDURES.csv')
    icd_codes_procedures = convert_to_str(d_icd_procedures['icd9_code'.upper()].tolist())
    black_list_icd_procedures = find_black_list(data, icd_codes_procedures, 'procedures')

    codes_proc = read_json('data/dictionaries/codes_proc_updated.json')
    codes_procedures, descr_procedures = get_codes_descr(codes_proc)
    new_black_list_icd_procedures = find_black_list_second_level(black_list_icd_procedures, codes_procedures)

    long_title_procedures = d_icd_procedures['long_title'.upper()].tolist()
    mapping_to_dictionary_two_levels(data, icd_codes_procedures, 
                                     long_title_procedures, 'procedures', 
                                     codes_procedures, descr_procedures)

    save_json(data, output_path + '2_data_after_dictionary_mappings_grouped_icd9.json')