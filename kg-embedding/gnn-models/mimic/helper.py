import json
import os

def save_json(file, path):
    with open(path, 'w') as outfile:
        json.dump(file, outfile)


def find_json_files(folder_path):
    files = []
    for file in os.listdir(folder_path):
        if file.endswith(".json"):
            files.append(os.path.join(folder_path, file))
    return files


def read_json(path):
    with open(path) as json_file:
        return json.load(json_file)


def filter_list(l, filenames):
    l_filtered = []
    for p in l:
        if p.split('/')[-1].split('.')[0] in filenames:
            l_filtered.append(p)
    return l_filtered


def filter_list_2(l, black_list):
    l_filtered = []
    for p in l:
        if p.split('/')[-1].split('.')[0] not in black_list:
            l_filtered.append(p)
    return l_filtered


class InputFile:
    def __init__(self, input_path, query_codes, query_code_descriptions):
        self.init_file = read_json(input_path)
        self.query_codes = query_codes
        self.query_code_descriptions = query_code_descriptions
        self.sampled_file_and_operation, self.key_list_and_operation = self.get_sampled_file_and_operation()
        self.sampled_file_or_operation, self.key_list_or_operation = self.get_sampled_file_or_operation()


    def get_sampled_file_and_operation(self):
        sampled_dict = {}
        key_list = []
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
                        key_list.append(k1 + '_' + k2)
                    else:
                        sampled_dict[k1][k2] = self.init_file[k1][k2]
                        key_list.append(k1 + '_' + k2)
        return sampled_dict, key_list

    
    def get_sampled_file_or_operation(self):
        sampled_dict = {}
        key_list = []
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
                        key_list.append(k1 + '_' + k2)
                    else:
                        sampled_dict[k1][k2] = self.init_file[k1][k2]
                        key_list.append(k1 + '_' + k2)
        return sampled_dict, key_list


class save_results(object):
    def __init__(self, filename, header=None):
        self.filename = filename
        if os.path.exists(filename):
            os.remove(filename)
        
        if header is not None:
            with open(filename, 'w') as out:
                print(header, file=out)
    
    def save(self, info):
        with open(self.filename, 'a') as out:
            print(info, file=out)