import pandas as pd
import os
from utils_ import read_csv, save_json


def check_nan(arg):
    if pd.isna(arg):
        return ''
    else:
        return arg


if __name__ == '__main__':
    input_path = 'data/selected_data/'
    output_path = 'data/processed_data/'
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    patients = read_csv(input_path + "patients.csv")
    unified_data = {}
    for index, row in patients.iterrows():
        if row['subject_id'] in unified_data.keys():
            print('Check')
        else:
            unified_data[str(row['subject_id'])] = {'gender': row['gender'],
                                                    'date_of_birth': row['dob'],
                                                    'date_of_death': row['dod'],
                                                    'death_overall': str(row['expire_flag']),
                                                    'admissions': {'admission_id': [],
                                                                'admission_time': [],
                                                                'discharged_time': [],
                                                                'death': [],
                                                                'religion': [],
                                                                'marital_status': [],
                                                                'ethnicity': [],
                                                                'diagnosis': []}}

    
    admissions = read_csv(input_path + "admissions.csv")
    for index, row in admissions.iterrows():
        unified_data[str(row['subject_id'])]['admissions']['admission_id'].append(check_nan(str(row['hadm_id'])))
        unified_data[str(row['subject_id'])]['admissions']['admission_time'].append(check_nan(row['admittime']))
        unified_data[str(row['subject_id'])]['admissions']['discharged_time'].append(check_nan(row['dischtime']))
        unified_data[str(row['subject_id'])]['admissions']['death'].append(str(check_nan(row['hospital_expire_flag'])))
        unified_data[str(row['subject_id'])]['admissions']['religion'].append(check_nan(row['religion']))
        unified_data[str(row['subject_id'])]['admissions']['marital_status'].append(check_nan(row['marital_status']))
        unified_data[str(row['subject_id'])]['admissions']['ethnicity'].append(check_nan(row['ethnicity']))
        unified_data[str(row['subject_id'])]['admissions']['diagnosis'].append(check_nan(row['diagnosis']))

    
    icustays = read_csv(input_path + "icustays.csv")
    # Update/Initialize the dictionary with new lists to respect 1-1 mapping between the IDs of ICU stay and admissions.
    for k in unified_data.keys():
        unified_data[k]['icu_stay'] = {'icu_stay_id': [0]*len(unified_data[k]['admissions']['admission_id']),
                                       'length_of_stay': [0.0]*len(unified_data[k]['admissions']['admission_id']),
                                       'dbsource': ['']*len(unified_data[k]['admissions']['admission_id'])}
    
    for index, row in icustays.iterrows():
        ind = unified_data[str(row['subject_id'])]['admissions']['admission_id'].index(str(row['hadm_id']))
        unified_data[str(row['subject_id'])]['icu_stay']['icu_stay_id'][ind] = str(check_nan(row['icustay_id']))
        unified_data[str(row['subject_id'])]['icu_stay']['length_of_stay'][ind] = str(check_nan(row['los']))
        unified_data[str(row['subject_id'])]['icu_stay']['dbsource'][ind] = check_nan(row['dbsource'])


    cptevents = read_csv(input_path + "cptevents.csv")
    # Update/Initialize the dictionary with new lists to respect the mapping between the admission IDs and CPT events.
    for k in unified_data.keys():
        unified_data[k]['cpt_events'] = {'cpt_code': [[] for _ in range(len(unified_data[k]['admissions']['admission_id']))],
                                        'cpt_number': [[] for _ in range(len(unified_data[k]['admissions']['admission_id']))],
                                        'cpt_suffix': [[] for _ in range(len(unified_data[k]['admissions']['admission_id']))],
                                        'section_header': [[] for _ in range(len(unified_data[k]['admissions']['admission_id']))],
                                        'subsection_header': [[] for _ in range(len(unified_data[k]['admissions']['admission_id']))]}

    for index, row in cptevents.iterrows():
        ind = unified_data[str(row['subject_id'])]['admissions']['admission_id'].index(str(row['hadm_id']))
        unified_data[str(row['subject_id'])]['cpt_events']['cpt_code'][ind].append(str(check_nan(row['cpt_cd'])))
        unified_data[str(row['subject_id'])]['cpt_events']['cpt_number'][ind].append(str(check_nan(row['cpt_number'])))
        unified_data[str(row['subject_id'])]['cpt_events']['cpt_suffix'][ind].append(str(check_nan(row['cpt_suffix'])))
        unified_data[str(row['subject_id'])]['cpt_events']['section_header'][ind].append(check_nan(row['sectionheader']))
        unified_data[str(row['subject_id'])]['cpt_events']['subsection_header'][ind].append(check_nan(row['subsectionheader']))

    
    diagnoses = read_csv(input_path + "diagnoses_icd.csv")
    # Update/Initialize the dictionary with new lists to respect the mapping between the admission IDs and diagnoses.
    for k in unified_data.keys():
        unified_data[k]['diagnoses'] = {'icd9_code': [[] for _ in range(len(unified_data[k]['admissions']['admission_id']))]}

    for index, row in diagnoses.iterrows():
        if str(check_nan(row['icd9_code'])) == '':
            continue
        else:
            ind = unified_data[str(row['subject_id'])]['admissions']['admission_id'].index(str(row['hadm_id']))
            unified_data[str(row['subject_id'])]['diagnoses']['icd9_code'][ind].append(check_nan(row['icd9_code']))


    prescriptions = read_csv(input_path + "prescriptions.csv")
    # Update/Initialize the dictionary with new lists to respect the mapping between the admission IDs and prescriptions.
    for k in unified_data.keys():
        unified_data[k]['prescriptions'] = {'drug': [[] for _ in range(len(unified_data[k]['admissions']['admission_id']))],
                                            'formulary_drug_cd': [[] for _ in range(len(unified_data[k]['admissions']['admission_id']))],
                                            'gsn': [[] for _ in range(len(unified_data[k]['admissions']['admission_id']))],
                                            'ndc': [[] for _ in range(len(unified_data[k]['admissions']['admission_id']))]}
    
    for index, row in prescriptions.iterrows():
        ind = unified_data[str(row['subject_id'])]['admissions']['admission_id'].index(str(row['hadm_id']))
        unified_data[str(row['subject_id'])]['prescriptions']['drug'][ind].append(check_nan(row['drug']))
        unified_data[str(row['subject_id'])]['prescriptions']['formulary_drug_cd'][ind].append(check_nan(row['formulary_drug_cd']))
        unified_data[str(row['subject_id'])]['prescriptions']['gsn'][ind].append(str(check_nan(row['gsn'])))
        unified_data[str(row['subject_id'])]['prescriptions']['ndc'][ind].append(str(check_nan(row['ndc'])))


    procedures = read_csv(input_path + "procedures_icd.csv")
    # Update/Initialize the dictionary with new lists to respect the mapping between the admission IDs and procedures.
    for k in unified_data.keys():
        unified_data[k]['procedures'] = {'icd9_code': [[] for _ in range(len(unified_data[k]['admissions']['admission_id']))]}

    for index, row in procedures.iterrows():
        if str(check_nan(row['icd9_code'])) == '':
            continue
        else:
            ind = unified_data[str(row['subject_id'])]['admissions']['admission_id'].index(str(row['hadm_id']))
            unified_data[str(row['subject_id'])]['procedures']['icd9_code'][ind].append(str(check_nan(row['icd9_code'])))


    # Update the dictionary with the age of the patient
    for k in unified_data.keys():
        tmp_age = []
        for a_t in unified_data[k]['admissions']['admission_time']:
            tmp_age.append(str((int(a_t.split('-')[0]) - int(unified_data[k]['date_of_birth'].split('-')[0]))))
        unified_data[k]['admissions']['age'] = tmp_age

    # Unify, if possible, the age, the religion, marital_status and ethnicity information
    for k in unified_data.keys():
        # Age
        age_unified =  unified_data[k]['admissions']['age'][0]
        for a in unified_data[k]['admissions']['age']:
            if a != age_unified:
                age_unified = ''
                break
        unified_data[k]['age_unified'] = age_unified
        # Religion
        rel_unified =  unified_data[k]['admissions']['religion'][0]
        for r in unified_data[k]['admissions']['religion']:
            if r != rel_unified:
                rel_unified = ''
                break
        unified_data[k]['religion_unified'] = rel_unified
        # Marital status
        mar_status_unified = unified_data[k]['admissions']['marital_status'][0]
        for m_s in unified_data[k]['admissions']['marital_status']:
            if m_s != mar_status_unified:
                mar_status_unified = ''
                break
        unified_data[k]['marital_status_unified'] = mar_status_unified
        # Ethnicity
        ethnicity_unified = unified_data[k]['admissions']['ethnicity'][0]
        for eth in unified_data[k]['admissions']['ethnicity']:
            if eth != ethnicity_unified:
                ethnicity_unified = ''
                break
        unified_data[k]['ethnicity_unified'] = ethnicity_unified
    
    save_json(unified_data, output_path + '1_data_after_data_wrangling.json')
