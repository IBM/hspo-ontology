# This script is used to find graphs with missing information. 
# To do that we need the first version of the undirected graphs.
# Information of interest that might be missing: diseases, medication, procedures. 

import argparse
from helper import save_json, read_json, find_json_files

def find_graphs_with_missing_info(input_path):
    unique_t = [["patient", "has", "demographics"],
                ["patient", "has", "diseases"],
                ["patient", "has", "interventions"],
                ["interventions", "has", "procedure_provisioning_ICD9"],
                ["interventions", "has", "medication_provisioning"],
                ["medication_provisioning", "hasIntervention", "procedure_medication"],
                ["demographics", "hasMaritalStatus", "marital_status"],
                ["demographics", "followsReligion", "religion"],
                ["demographics", "hasRaceorEthnicity", "race"],
                ["demographics", "hasGender", "gender"],
                ["diseases", "hasDisease", "disease"],
                ["procedure_provisioning_ICD9", "hasIntervention", "procedure_ICD9"],
                ["demographics", "has", "age"],
                ["age", "hasStageOfLife", "stage_of_life"],
                ["age", "belongsToAgeGroup", "age_group"]]

    # Graphs with labels zero
    black_list_graphs_0 = []
    t_dict_0 = {}
    for k in unique_t:
        t_dict_0[k[0] + '_' + k[1] + '_' + k[2]] = 0
    
    g0 = find_json_files(input_path + 'undirected/0/v4/')
    for p in g0:
        flag = 0
        g = read_json(p)
        uniq_tmp = []
        for r in g:
            if [r[0][1], r[1], r[2][1]] not in uniq_tmp:
                uniq_tmp.append([r[0][1], r[1], r[2][1]])
        for r in unique_t:
            if r not in uniq_tmp:
                t_dict_0[r[0] + '_' + r[1] + '_' + r[2]] += 1
                flag = 1
        if flag == 1:
            black_list_graphs_0.append(p.split('/')[-1].split('.')[0])
    
    # Graphs with labels zero
    black_list_graphs_1 = []
    t_dict_1 = {}
    for k in unique_t:
        t_dict_1[k[0] + '_' + k[1] + '_' + k[2]] = 0
    
    g1 = find_json_files(input_path + 'undirected/1/v4/')
    for p in g1:
        flag = 0
        g = read_json(p)
        uniq_tmp = []
        for r in g:
            if [r[0][1], r[1], r[2][1]] not in uniq_tmp:
                uniq_tmp.append([r[0][1], r[1], r[2][1]])
        for r in unique_t:
            if r not in uniq_tmp:
                t_dict_1[r[0] + '_' + r[1] + '_' + r[2]] += 1
                flag = 1
        if flag == 1:
            black_list_graphs_1.append(p.split('/')[-1].split('.')[0])
    
    return t_dict_0, t_dict_1, black_list_graphs_0, black_list_graphs_1


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_path", default='data/triplet_format_graphs/', type=str, required=False,
                        help = "The input path with the graphs (version 4 undirected).")

    args = parser.parse_args()

    t_dict_0, t_dict_1, black_list_graphs_0, black_list_graphs_1 = find_graphs_with_missing_info(args.input_path)
    save_json(t_dict_0, 'missing_info_dict_graph_0_v4_undirected.json')
    save_json(t_dict_1, 'missing_info_dict_graph_1_v4_undirected.json')
    save_json(black_list_graphs_0, 'missing_info_bl_graph_0_v4_undirected.json')
    save_json(black_list_graphs_1, 'missing_info_bl_graph_1_v4_undirected.json')