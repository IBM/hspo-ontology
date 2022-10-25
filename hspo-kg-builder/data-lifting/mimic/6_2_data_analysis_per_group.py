import json
from statistics import mean
from datetime import date
import numpy as np
import pandas as pd
import argparse
import os

from utils_ import read_json, DataAnalysisOntMapping


class DataAnalysis:
    def __init__(self, input_path, output_path, diagnoses_dict_path1, diagnoses_dict_path2,
                 procedures_dict_path1, procedures_dict_path2, age_group_step, 
                 co_morbidity_group_step, ethnicity_mapping, marital_status_mapping, religion_mapping):
        self.input_path = input_path
        self.output_path = output_path
        self.file = self.read_json(self.input_path)
        self.age_group_step = age_group_step
        self.co_morbidity_group_step = co_morbidity_group_step
        self.readmission_0, self.readmission_1 = self.divide_data_based_on_readmission_label()
        # Mappings
        self.ethnicity_mapping = ethnicity_mapping
        self.marital_status_mapping = marital_status_mapping 
        self.religion_mapping = religion_mapping
        # Dictionaries (diagnoses and procedures) for textual description mapping
        self.diagnoses_dict1 = pd.read_csv(diagnoses_dict_path1, dtype = str)
        self.icd_codes_diagnoses1 = self.convert_to_str(self.diagnoses_dict1['icd9_code'.upper()].tolist())
        self.long_title_diagnoses1 = self.diagnoses_dict1['long_title'.upper()].tolist()
        self.diagnoses_dict2 = self.read_json(diagnoses_dict_path2)
        self.icd_codes_diagnoses2, self.long_title_diagnoses2 = self.get_codes_descr(self.diagnoses_dict2)
        self.procedures_dict1 = pd.read_csv(procedures_dict_path1, dtype = str)
        self.icd_codes_procedures1 = self.convert_to_str(self.procedures_dict1['icd9_code'.upper()].tolist())
        self.long_title_procedures1 = self.procedures_dict1['long_title'.upper()].tolist()
        self.procedures_dict2 = self.read_json(procedures_dict_path2)
        self.icd_codes_procedures2, self.long_title_procedures2 = self.get_codes_descr(self.procedures_dict2)
        

    
    def divide_data_based_on_readmission_label(self):
        readmission_0 = {}
        readmission_1 = {}
        for k1 in self.file.keys():
            for k2 in self.file[k1].keys():
                if self.file[k1][k2]['readmission'] == '0':
                    if k1 not in readmission_0.keys():
                        readmission_0[k1] = {k2: self.file[k1][k2]}
                    else:
                        readmission_0[k1][k2] = self.file[k1][k2]
                else:
                    if k1 not in readmission_1.keys():
                        readmission_1[k1] = {k2: self.file[k1][k2]}
                    else:
                        readmission_1[k1][k2] = self.file[k1][k2]
        return readmission_0, readmission_1


    def exec_analysis(self):
        info_0 = self.get_info(self.readmission_0)
        self.save_json(info_0, '0')
        self.save_csv(info_0, '0')
        info_1 = self.get_info(self.readmission_1)
        self.save_json(info_1, '1')
        self.save_csv(info_1, '1')
        # Mapped on ontology
        readmission_0_ont = DataAnalysisOntMapping('', self.output_path + '/' + '0' + '/', 
                                                   self.ethnicity_mapping, self.marital_status_mapping, 
                                                   self.religion_mapping, self.readmission_0)
        readmission_0_ont.save_json()
        readmission_0_ont.save_csv()
        readmission_1_ont = DataAnalysisOntMapping('', self.output_path + '/' + '1' + '/', 
                                                   self.ethnicity_mapping, self.marital_status_mapping, 
                                                   self.religion_mapping, self.readmission_1)
        readmission_1_ont.save_json()
        readmission_1_ont.save_csv()
    

    def get_info(self, data):
        info = {}
        info['total_subjects'] = len(list(data.keys()))
        info['avg_admissions_per_subject'] = self.get_average_admissions_per_subj(data)
        info['gender_distribution'] = self.get_distribution('gender', data)
        info['age_distribution'] = self.get_distribution('age', data)
        info['age_group_distribution'] = self.get_age_group_distribution(info['age_distribution'])
        info['religion_distribution'] = self.get_distribution('religion', data)
        info['race_distribution'] = self.get_distribution('ethnicity', data)
        info['marital_status_distribution'] = self.get_distribution('marital_status', data)
        info['readmissions'] = self.get_distribution('readmission', data)
        info['initial_diagnosis'] = self.get_distribution('diagnosis', data)
        info['cpt_events_section_header'] = self.get_distribution_second_order(data, 'cpt_events', 'section_header', 1)
        info['cpt_events_subsection_header'] = self.get_distribution_second_order(data, 'cpt_events', 'subsection_header', 1)
        info['diagnoses_icd9_code'] = self.get_distribution_second_order(data, 'diagnoses', 'icd9_code', 1)
        info['prescriptions_drug'] = self.get_distribution_second_order(data, 'prescriptions', 'drug', 1)
        info['procedures_icd9_code'] = self.get_distribution_second_order(data, 'procedures', 'icd9_code', 1)
        info['employment'] = self.get_distribution_third_order('social_info', 'employment', 'textual_description', 1)
        info['household_composition'] = self.get_distribution_third_order('social_info', 'household_composition', 'textual_description', 1)
        info['housing'] = self.get_distribution_third_order('social_info', 'housing', 'textual_description', 1)
        info['co-morbidity'] = self.get_co_morbidity_group_distribution(data)

        return info


    def get_co_morbidity_group_distribution(self, data):
        co_morbidity_groups_distr, ranges = self.get_co_morbidity_groups()
        for k1 in data.keys():
            for k2 in data[k1].keys():
                n_diagnoses = len(list(set(data[k1][k2]['diagnoses']['icd9_code'])))
                for i, r in enumerate(ranges):
                    if n_diagnoses >= r[0] and n_diagnoses <= r[1]:
                        co_morbidity_groups_distr[list(co_morbidity_groups_distr.keys())[i]] += 1
        
        return self.sort_dict(co_morbidity_groups_distr)
        
    
    def get_co_morbidity_groups(self):
        co_morbidity_groups_distr = {}
        ranges = []
        for i in range(0, 40, self.co_morbidity_group_step):
            co_morbidity_groups_distr[str(i) + '-' + str(i+self.co_morbidity_group_step-1)] = 0
            ranges.append((i, i+self.co_morbidity_group_step-1))

        return co_morbidity_groups_distr, ranges


    def get_age_group_distribution(self, age_distr):
        age_groups_distr, ranges = self.get_age_groups()
        for k in age_distr.keys():
            for i, r in enumerate(ranges):
                if int(k) >= r[0] and int(k) <= r[1]:
                    age_groups_distr[list(age_groups_distr.keys())[i]] += age_distr[k]

        return self.sort_dict(age_groups_distr)
    

    def get_age_groups(self):
        age_groups_distr = {}
        ranges = []
        for i in range(0, 85, self.age_group_step):
            age_groups_distr[str(i) + '-' + str(i+self.age_group_step-1)] = 0
            ranges.append((i, i+self.age_group_step-1))

        age_groups_distr['85-88'] = 0
        ranges.append((85, 88))
        age_groups_distr['89-_'] = 0
        ranges.append((89, 400))
        return age_groups_distr, ranges


    def get_distribution_third_order(self, key1, key2, key3, set_=0):
        """ 
            @param set_: boolean (0 or 1), defines if we need to take the set of the list (unique values) or not. 
                         e.g.: the prescription list has many duplicates (medication received more than once).
        """
        distr = {}
        for k1 in self.file.keys():
            for k2 in self.file[k1].keys():
                if set_ == 0:
                    for it in self.file[k1][k2][key1][key2][key3]:
                        if it not in distr.keys():
                            distr[it] = 1
                        else:
                            distr[it] += 1
                else:
                    try:
                        for it in list(set(self.file[k1][k2][key1][key2][key3])):
                            if it not in distr.keys():
                                distr[it] = 1
                            else:
                                distr[it] += 1
                    except:
                        pass
        return self.sort_dict(distr)
        

    def get_distribution_second_order(self, data, key1, key2, set_=0):
        """ 
            @param set_: boolean (0 or 1), defines if we need to take the set of the list (unique values) or not. 
                         e.g.: the prescription list has many duplicates (medication received more than once).
        """
        distr = {}
        for k1 in data.keys():
            for k2 in data[k1].keys():
                if set_ == 0:
                    for it in data[k1][k2][key1][key2]:
                        if it not in distr.keys():
                            distr[it] = 1
                        else:
                            distr[it] += 1
                else:
                    for it in list(set(data[k1][k2][key1][key2])):
                        if it not in distr.keys():
                            distr[it] = 1
                        else:
                            distr[it] += 1
        return self.sort_dict(distr)


    def get_distribution(self, key, data):
        distr = {}
        for k1 in data.keys():
            for k2 in data[k1].keys():
                if data[k1][k2][key] not in distr.keys():
                    distr[data[k1][k2][key]] = 1
                else:
                    distr[data[k1][k2][key]] += 1
        return self.sort_dict(distr)


    def get_codes_descr(self, dict_):
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


    def sort_dict(self, dict_):
        sorted_dict = {}
        sorted_keys = sorted(dict_, key=dict_.get, reverse=True)

        for w in sorted_keys:
            sorted_dict[w] = dict_[w]
        return sorted_dict


    def get_average_admissions_per_subj(self, data):
        n_adm = []
        for k in data.keys():
            n_adm.append(len(list(data[k].keys())))
        return round(mean(n_adm), 2)
    

    def read_json(self, path):
        with open(path) as json_file:
            return json.load(json_file)


    def save_json(self, info, group):
        with open(self.output_path + group + '/' + 'info_distributions.json', 'w') as outfile:
            json.dump(info, outfile)


    def save_csv(self, info, group):
        for k in info.keys():
            if k in ['total_subjects', 'avg_admissions_per_subject']:
                continue
            elif k == 'diagnoses_icd9_code':
                tmp_text_discr = []
                for icd9_code in list(info[k].keys()):
                    if icd9_code == '':
                        tmp_text_discr.append('')
                    else:
                        try:
                            ind = self.icd_codes_diagnoses1.index(icd9_code)
                            tmp_text_discr.append(self.long_title_diagnoses1[ind])
                        except:
                            ind = self.icd_codes_diagnoses2.index(icd9_code)
                            tmp_text_discr.append(self.long_title_diagnoses2[ind])

                df = pd.DataFrame({'Value' : list(info[k].keys()),
                                   'Frequency': list(info[k].values()),
                                   'Textual description': tmp_text_discr})
                df.to_csv(self.output_path + '/' + group + '/' + k + '.csv', index=False, encoding="utf-8")
            elif k == 'procedures_icd9_code':
                tmp_text_discr = []
                for icd9_code in list(info[k].keys()):
                    if icd9_code == '':
                        tmp_text_discr.append('')
                    else:
                        try:
                            ind = self.icd_codes_procedures1.index(icd9_code)
                            tmp_text_discr.append(self.long_title_procedures1[ind])
                        except:
                            ind = self.icd_codes_procedures2.index(icd9_code)
                            tmp_text_discr.append(self.long_title_procedures2[ind])

                df = pd.DataFrame({'Value' : list(info[k].keys()),
                                   'Frequency': list(info[k].values()),
                                   'Textual description': tmp_text_discr})
                df.to_csv(self.output_path + '/' + group + '/' + k + '.csv', index=False, encoding="utf-8")
            else:
                df = pd.DataFrame({'Value' : list(info[k].keys()),
                                   'Frequency': list(info[k].values())})
                df.to_csv(self.output_path + '/' + group + '/' + k + '.csv', index=False, encoding="utf-8")


    def convert_to_str(self, l):
        l_str = [str(it) for it in l]
        return l_str




if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_path", default='data/processed_data/4_data_after_adding_notes_info_grouped_icd9.json', type=str, required=False,
                        help = "The path of the final json file with the data.")
    parser.add_argument("--output_path", default='data/distributions/readmission_case/per_group/grouped_icd9/', type=str, required=False,
                        help = "The output path where distributions are going to be stored.")
    parser.add_argument("--diagnoses_dictionary_path", default='data/dictionaries/D_ICD_DIAGNOSES_updated.csv', type=str, required=False,
                        help = "The path of the diagnoses dictionary.")
    parser.add_argument("--procedures_dictionary_path", default='data/dictionaries/D_ICD_PROCEDURES.csv', type=str, required=False,
                        help = "The path of the procedure dictionary.")
    parser.add_argument("--diagnoses_manual_dict_path", default='data/dictionaries/codes_diag_updated.json', type=str, required=False,
                        help = "The path of the diagnoses manual dictionary.")
    parser.add_argument("--procedures_manual_dict_path", default='data/dictionaries/codes_proc_updated.json', type=str, required=False,
                        help = "The path of the procedure manual dictionary.")
    parser.add_argument("--ethnicity_mapping_path", default='data/ethnicity_mappings.json', type=str, required=False,
                        help = "The path of the ethnicity mapping file.")
    parser.add_argument("--marital_status_mapping_path", default='data/marital_status_mappings.json', type=str, required=False,
                        help = "The path of the marital status mapping file.")
    parser.add_argument("--religion_mapping_path", default='data/religion_mappings.json', type=str, required=False,
                        help = "The path of the relation mapping file.")


    args = parser.parse_args()

    if not os.path.exists(args.output_path + '0/'):
        os.makedirs(args.output_path+ '0/')
    if not os.path.exists(args.output_path + '1/'):
        os.makedirs(args.output_path+ '1/')


    ethnicity_mapping = read_json(args.ethnicity_mapping_path) 
    marital_status_mapping = read_json(args.marital_status_mapping_path)  
    religion_mapping = read_json(args.religion_mapping_path)

    obj_analysis = DataAnalysis(args.data_path, 
                                args.output_path,
                                args.diagnoses_dictionary_path,
                                args.diagnoses_manual_dict_path,
                                args.procedures_dictionary_path,
                                args.procedures_manual_dict_path,
                                5, 2,
                                ethnicity_mapping, 
                                marital_status_mapping, 
                                religion_mapping)
    
    obj_analysis.exec_analysis()