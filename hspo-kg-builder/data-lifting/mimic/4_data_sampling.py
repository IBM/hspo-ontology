import argparse
from datetime import date
from utils_ import read_json, save_json


def add_record(sampled_data, data, k, ind, label):
    if k not in list(sampled_data.keys()):
        sampled_data[k] = {'1': {'readmission': label,
                                 'gender': data[k]['gender'],
                                 'religion': data[k]['admissions']['religion'][ind],
                                 'marital_status': data[k]['admissions']['marital_status'][ind],
                                 'ethnicity': data[k]['admissions']['ethnicity'][ind],
                                 'age': data[k]['admissions']['age'][ind],
                                 'diagnosis': data[k]['admissions']['diagnosis'][ind],
                                 'cpt_events': {'cpt_code': data[k]['cpt_events']['cpt_code'][ind], 
                                                'cpt_number': data[k]['cpt_events']['cpt_number'][ind],
                                                'cpt_suffix': data[k]['cpt_events']['cpt_suffix'][ind],
                                                'section_header': data[k]['cpt_events']['section_header'][ind],
                                                'subsection_header': data[k]['cpt_events']['subsection_header'][ind]},
                                 'diagnoses': {'icd9_code': data[k]['diagnoses']['icd9_code'][ind],
                                               'textual_description': data[k]['diagnoses']['textual_description'][ind]},
                                 'prescriptions': {'drug': data[k]['prescriptions']['drug'][ind],
                                                   'formulary_drug_cd': data[k]['prescriptions']['formulary_drug_cd'][ind],
                                                   'gsn': data[k]['prescriptions']['gsn'][ind],
                                                   'ndc': data[k]['prescriptions']['ndc'][ind]},
                                 'procedures': {'icd9_code': data[k]['procedures']['icd9_code'][ind],
                                                'textual_description': data[k]['procedures']['textual_description'][ind]}}}
    else:
        sampled_data[k][str(len(list((sampled_data[k].keys())))+1)] = {'readmission': label,
                                                                       'gender': data[k]['gender'],
                                                                       'religion': data[k]['admissions']['religion'][ind],
                                                                       'marital_status': data[k]['admissions']['marital_status'][ind],
                                                                       'ethnicity': data[k]['admissions']['ethnicity'][ind],
                                                                       'age': data[k]['admissions']['age'][ind],
                                                                       'diagnosis': data[k]['admissions']['diagnosis'][ind],
                                                                       'cpt_events': {'cpt_code': data[k]['cpt_events']['cpt_code'][ind],
                                                                                      'cpt_number': data[k]['cpt_events']['cpt_number'][ind],
                                                                                      'cpt_suffix': data[k]['cpt_events']['cpt_suffix'][ind],
                                                                                      'section_header': data[k]['cpt_events']['section_header'][ind],
                                                                                      'subsection_header': data[k]['cpt_events']['subsection_header'][ind]},
                                                                        'diagnoses': {'icd9_code': data[k]['diagnoses']['icd9_code'][ind],
                                                                                      'textual_description': data[k]['diagnoses']['textual_description'][ind]},
                                                                        'prescriptions': {'drug': data[k]['prescriptions']['drug'][ind],
                                                                                          'formulary_drug_cd': data[k]['prescriptions']['formulary_drug_cd'][ind],
                                                                                          'gsn': data[k]['prescriptions']['gsn'][ind],
                                                                                          'ndc': data[k]['prescriptions']['ndc'][ind]},
                                                                        'procedures': {'icd9_code': data[k]['procedures']['icd9_code'][ind],
                                                                                       'textual_description': data[k]['procedures']['textual_description'][ind]}}

    # Return the new key that was generated as: subject_id + '_' + new_key
    return k + '_' + list(sampled_data[k].keys())[-1]


def sample_data(data, threshold):
    mapped_keys = {}
    sampled_data = {}
    for k in data.keys():
        for i, d in enumerate(data[k]['admissions']['death']):
            if d == '1':
                continue
            else:
                # End of list
                if i+1 == len(data[k]['admissions']['death']):
                    if data[k]['death_overall'] == '0':
                        # The patient is still alive and didn't readmit to the hospital.
                        new_key = add_record(sampled_data, data, k, i, '0')
                        old_key = k + '_' + data[k]['admissions']['admission_id'][i]
                        mapped_keys[old_key] = new_key
                    else:
                        cur_discharged_time = data[k]['admissions']['discharged_time'][i]
                        date_of_death = data[k]['date_of_death']
                        d0 = date(int(cur_discharged_time.split(' ')[0].split('-')[0]), int(cur_discharged_time.split(' ')[0].split('-')[1]), int(cur_discharged_time.split(' ')[0].split('-')[2]))
                        d1 = date(int(date_of_death.split(' ')[0].split('-')[0]), int(date_of_death.split(' ')[0].split('-')[1]), int(date_of_death.split(' ')[0].split('-')[2]))
                        delta = d1 - d0
                        if delta.days > threshold:
                            new_key = add_record(sampled_data, data, k, i, '0')
                            old_key = k + '_' + data[k]['admissions']['admission_id'][i]
                            mapped_keys[old_key] = new_key
                        else:
                            # The patient died outside of the hospital within the given threshold, so readmission is not possible.
                            continue
                else:
                    cur_discharged_time = data[k]['admissions']['discharged_time'][i]
                    next_admission_time = data[k]['admissions']['admission_time'][i+1]
                    d0 = date(int(cur_discharged_time.split(' ')[0].split('-')[0]), int(cur_discharged_time.split(' ')[0].split('-')[1]), int(cur_discharged_time.split(' ')[0].split('-')[2]))
                    d1 = date(int(next_admission_time.split(' ')[0].split('-')[0]), int(next_admission_time.split(' ')[0].split('-')[1]), int(next_admission_time.split(' ')[0].split('-')[2]))
                    delta = d1 - d0
                    if delta.days <= threshold:
                        new_key = add_record(sampled_data, data, k, i, '1')
                        old_key = k + '_' + data[k]['admissions']['admission_id'][i]
                        mapped_keys[old_key] = new_key
                    else:
                        new_key = add_record(sampled_data, data, k, i, '0')
                        old_key = k + '_' + data[k]['admissions']['admission_id'][i]
                        mapped_keys[old_key] = new_key
    
    return sampled_data, mapped_keys


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--threshold", default=30, type=int, required=True,
                        help = "The span of days to monitor if the patient is going to be readmitted to the ICU or no.")
    
    args = parser.parse_args()

    # grouped ICD9 version
    data = read_json('data/processed_data/2_data_after_dictionary_mappings_grouped_icd9.json')
    sampled_data_final, mapped_keys = sample_data(data, args.threshold)
    save_json(sampled_data_final, 'data/processed_data/3_data_task_valid_grouped_icd9.json')
    save_json(mapped_keys, 'data/processed_data/key_mapping_from_total_to_task_valid.json')
    # non-grouped ICD9 version    
    data = read_json('data/processed_data/2_data_after_dictionary_mappings.json')
    sampled_data_final, mapped_keys = sample_data(data, args.threshold)
    save_json(sampled_data_final, 'data/processed_data/3_data_task_valid.json')