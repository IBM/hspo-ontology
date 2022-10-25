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






class DataAnalysisOntMapping:
    def __init__(self, input_path, output_path, ethnicity_mapping,
                 marital_status_mapping, religion_mapping, file={}):
        self.input_path = input_path
        self.output_path = output_path
        if len(file.keys()) == 0:
            self.file = self.read_json(self.input_path)
        else:
            self.file = file
        self.ethnicity_mapping = ethnicity_mapping
        self.marital_status_mapping = marital_status_mapping
        self.religion_mapping = religion_mapping


    def exec_analysis(self):
        info = {}
        info['religion_distribution_mapped_to_ont'] = self.get_distribution('religion')
        info['race_distribution_mapped_to_ont'] = self.get_distribution('ethnicity')
        info['marital_status_distribution_mapped_to_ont'] = self.get_distribution('marital_status')
        return info


    def get_distribution(self, key):
        distr = {}
        for k1 in self.file.keys():
            for k2 in self.file[k1].keys():
                if key == 'religion':
                    mapping = self.religion_mapping[self.file[k1][k2][key].lower()]
                elif key == 'marital_status':
                    mapping = self.marital_status_mapping[self.file[k1][k2][key].lower()]
                elif key == 'ethnicity':
                    mapping = self.ethnicity_mapping[self.file[k1][k2][key].lower()]
                if mapping not in distr.keys():
                    distr[mapping] = 1
                else:
                    distr[mapping] += 1
                    
        return self.sort_dict(distr)


    def sort_dict(self, dict_):
        sorted_dict = {}
        sorted_keys = sorted(dict_, key=dict_.get, reverse=True)

        for w in sorted_keys:
            sorted_dict[w] = dict_[w]
        return sorted_dict


    def read_json(self, path):
        with open(path) as json_file:
            return json.load(json_file)


    def save_json(self):
        info_distr = self.exec_analysis()
        with open(self.output_path + 'info_distributions_mapped_to_ont.json', 'w') as outfile:
            json.dump(info_distr, outfile)


    def save_csv(self):
        info_distr = self.exec_analysis()
        for k in info_distr.keys():
            df = pd.DataFrame({'Value' : list(info_distr[k].keys()),
                               'Frequency': list(info_distr[k].values())})
            df.to_csv(self.output_path + k + '.csv', index=False, encoding="utf-8")


    def convert_to_str(self, l):
        l_str = [str(it) for it in l]
        return l_str



class InputFile:
    def __init__(self, input_path, query_codes, query_code_descriptions):
        self.init_file = self.read_json(input_path)
        self.query_codes = query_codes
        self.query_code_descriptions = query_code_descriptions
        self.sampled_file_and_operation = self.get_sampled_file_and_operation()
        self.sampled_file_or_operation = self.get_sampled_file_or_operation()
    

    def read_json(self, path):
        with open(path) as json_file:
            return json.load(json_file)


    def get_sampled_file_and_operation(self):
        sampled_dict = {}
        for k1 in self.init_file.keys():
            for k2 in self.init_file[k1].keys():
                flag = 0
                # Check if all the query codes exist in the record.
                for i, q_c in enumerate(self.query_codes):
                    q_c_descr = self.query_code_descriptions[i]
                    if len(q_c_descr) == 1:
                        if not(q_c in self.init_file[k1][k2][q_c_descr[0]]):
                            flag = 1
                    elif len(q_c_descr) == 2:
                        if not(q_c in self.init_file[k1][k2][q_c_descr[0]][q_c_descr[1]]):
                            flag = 1
                if flag == 0:
                    if k1 not in sampled_dict.keys():
                        sampled_dict[k1] = {}
                        sampled_dict[k1][k2] = self.init_file[k1][k2]
                    else:
                        sampled_dict[k1][k2] = self.init_file[k1][k2]
        return sampled_dict

    
    def get_sampled_file_or_operation(self):
        sampled_dict = {}
        for k1 in self.init_file.keys():
            for k2 in self.init_file[k1].keys():
                flag = 0
                # Check if at least one of the query codes exists in the record.
                for i, q_c in enumerate(self.query_codes):
                    q_c_descr = self.query_code_descriptions[i]
                    if len(q_c_descr) == 1:
                        if q_c in self.init_file[k1][k2][q_c_descr[0]]:
                            flag = 1
                            break
                    elif len(q_c_descr) == 2:
                        if q_c in self.init_file[k1][k2][q_c_descr[0]][q_c_descr[1]]:
                            flag = 1
                            break
                if flag == 1:
                    if k1 not in sampled_dict.keys():
                        sampled_dict[k1] = {}
                        sampled_dict[k1][k2] = self.init_file[k1][k2]
                    else:
                        sampled_dict[k1][k2] = self.init_file[k1][k2]
        return sampled_dict        


