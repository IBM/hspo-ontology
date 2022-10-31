import os
import numpy as np
import json
import argparse


class Search:
    def __init__(self, folder_path, output_path):
        self.folder_path = folder_path
        self.output_path = output_path
        self.files_to_check = self.get_files()
        self.res_dict = self.build_res_dict()
        self.add_avg_metrics_cv()
        self.res_dict_across_splits = self.add_avg_metrics_splits()
    

    def get_files(self):
        training_info_files = []
        for root, _, files in os.walk(self.folder_path, topdown=False):
            for name in files:
                if name == 'training_info.txt':
                    training_info_files.append(os.path.join(root, name))
        return training_info_files
    

    def build_res_dict(self):
        res_dict = {}
        for f in self.files_to_check:
            with open(f) as f_:
                lines = f_.readlines()
                try:
                    acc = lines[-1][:-1].split('\t')[0][-7:-1]
                    prec = lines[-1][:-1].split('\t')[1][-7:-1]
                    rec = lines[-1][:-1].split('\t')[2][-7:-1]
                    f1 = lines[-1][:-1].split('\t')[3][-6:]
                    f_sub = f.split('/')
                    if f_sub[5] not in res_dict.keys():
                        res_dict[f_sub[5]] = {}
                    if f_sub[6] not in res_dict[f_sub[5]].keys():
                        res_dict[f_sub[5]][f_sub[6]] = {}
                    if f_sub[7] not in res_dict[f_sub[5]][f_sub[6]].keys():
                        res_dict[f_sub[5]][f_sub[6]][f_sub[7]] = {}
                    if f_sub[8] not in res_dict[f_sub[5]][f_sub[6]][f_sub[7]].keys():
                        res_dict[f_sub[5]][f_sub[6]][f_sub[7]][f_sub[8]] = {}
                    if f_sub[9] not in res_dict[f_sub[5]][f_sub[6]][f_sub[7]][f_sub[8]].keys():
                        res_dict[f_sub[5]][f_sub[6]][f_sub[7]][f_sub[8]][f_sub[9]] = {}
                    if f_sub[10] not in res_dict[f_sub[5]][f_sub[6]][f_sub[7]][f_sub[8]][f_sub[9]].keys():
                        res_dict[f_sub[5]][f_sub[6]][f_sub[7]][f_sub[8]][f_sub[9]][f_sub[10]] = {'acc': [],
                                                                                                'prec': [],
                                                                                                'rec': [],
                                                                                                'f1': []}
                    res_dict[f_sub[5]][f_sub[6]][f_sub[7]][f_sub[8]][f_sub[9]][f_sub[10]]['acc'].append(float(acc))
                    res_dict[f_sub[5]][f_sub[6]][f_sub[7]][f_sub[8]][f_sub[9]][f_sub[10]]['prec'].append(float(prec))
                    res_dict[f_sub[5]][f_sub[6]][f_sub[7]][f_sub[8]][f_sub[9]][f_sub[10]]['rec'].append(float(rec))
                    res_dict[f_sub[5]][f_sub[6]][f_sub[7]][f_sub[8]][f_sub[9]][f_sub[10]]['f1'].append(float(f1))
                except:
                    pass

        return res_dict                  
    

    def add_avg_metrics_cv(self):
        for k1 in self.res_dict.keys():
            for k2 in self.res_dict[k1].keys():
                for k3 in self.res_dict[k1][k2].keys():
                    for k4 in self.res_dict[k1][k2][k3].keys():
                        for k5 in self.res_dict[k1][k2][k3][k4].keys():
                            for k6 in self.res_dict[k1][k2][k3][k4][k5].keys():
                                self.res_dict[k1][k2][k3][k4][k5][k6]['avg_acc']= round(np.mean(self.res_dict[k1][k2][k3][k4][k5][k6]['acc']), 4)
                                self.res_dict[k1][k2][k3][k4][k5][k6]['avg_prec']= round(np.mean(self.res_dict[k1][k2][k3][k4][k5][k6]['prec']), 4)
                                self.res_dict[k1][k2][k3][k4][k5][k6]['avg_rec']= round(np.mean(self.res_dict[k1][k2][k3][k4][k5][k6]['rec']), 4)
                                self.res_dict[k1][k2][k3][k4][k5][k6]['avg_f1']= round(np.mean(self.res_dict[k1][k2][k3][k4][k5][k6]['f1']), 4)
    

    def add_avg_metrics_splits(self):
        res_dict_across_splits = {}
        for k1 in self.res_dict.keys():
            if k1 not in res_dict_across_splits.keys():
                res_dict_across_splits[k1] = {}
            for k2 in self.res_dict[k1].keys():
                if k2 not in res_dict_across_splits[k1].keys():
                    res_dict_across_splits[k1][k2] = {}
                for k3 in self.res_dict[k1][k2].keys():
                    if k3 not in res_dict_across_splits[k1][k2].keys():
                        res_dict_across_splits[k1][k2][k3] = {}
                    for k4 in self.res_dict[k1][k2][k3].keys():
                        if k4 not in res_dict_across_splits[k1][k2][k3].keys():
                            res_dict_across_splits[k1][k2][k3][k4] = {}
                        for k5 in self.res_dict[k1][k2][k3][k4].keys():
                            if k5 not in res_dict_across_splits[k1][k2][k3][k4].keys():
                                res_dict_across_splits[k1][k2][k3][k4][k5] = {}
                            tmp_acc, tmp_prec, tmp_rec, tmp_f1 = [], [], [], []
                            for k6 in self.res_dict[k1][k2][k3][k4][k5].keys():
                                tmp_acc.append(self.res_dict[k1][k2][k3][k4][k5][k6]['avg_acc'])
                                tmp_prec.append(self.res_dict[k1][k2][k3][k4][k5][k6]['avg_prec'])
                                tmp_rec.append(self.res_dict[k1][k2][k3][k4][k5][k6]['avg_rec'])
                                tmp_f1.append(self.res_dict[k1][k2][k3][k4][k5][k6]['avg_f1'])
                            
                            res_dict_across_splits[k1][k2][k3][k4][k5]['avg_acc_across_splits'] = round(np.mean(tmp_acc), 4)
                            res_dict_across_splits[k1][k2][k3][k4][k5]['avg_prec_across_splits'] = round(np.mean(tmp_prec), 4)
                            res_dict_across_splits[k1][k2][k3][k4][k5]['avg_rec_across_splits'] = round(np.mean(tmp_rec), 4)
                            res_dict_across_splits[k1][k2][k3][k4][k5]['avg_f1_across_splits'] = round(np.mean(tmp_f1), 4)
        return res_dict_across_splits


    def save_res_dict(self):
        with open(self.output_path + 'overall_results.json', 'w') as outfile:
            json.dump(self.res_dict, outfile)
        with open(self.output_path + 'overall_results_across_splits.json', 'w') as outfile:
            json.dump(self.res_dict_across_splits, outfile)

            


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--saved_models_path", default='../saved_models/use_case_428_427/', type=str, required=False,
                        help = "The path of the saved models.")
    parser.add_argument("--output_path", default='../saved_models/use_case_428_427/', type=str, required=False,
                        help = "The output path for storing the aggregated results.")

    args = parser.parse_args()

    obj = Search(args.saved_models_path,
                 args.output_path)
    obj.save_res_dict()