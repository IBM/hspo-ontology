import os 
import random
import argparse
from helper import save_json

def find_json_files(path):
    files = []
    filenames = []
    for file in os.listdir(path):
        if file.endswith(".json"):
            files.append(os.path.join(path, file))
            filenames.append(file.split('.')[0])
    return files, filenames


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_path_graphs_0", default='../../transformation/mimic/data/precalculated_embeddings/use_case_428_427/undirected/0/bow/v1/', type=str, required=False,
                        help = "The path of the precalculated embeddings of the graphs with 0 label (no readmission).")
    parser.add_argument("--input_path_graphs_1", default='../../transformation/mimic/data/precalculated_embeddings/use_case_428_427/undirected/1/bow/v1/', type=str, required=False,
                        help = "The path of the precalculated embeddings of the graphs with 1 label (readmission).")

    args = parser.parse_args()

    _, graphs_p_0 = find_json_files(args.input_path_graphs_0)
    _, graphs_p_1 = find_json_files(args.input_path_graphs_1)

    random.seed(42)
    random.shuffle(graphs_p_0)
    splits_0 = []
    for i in range(0, len(graphs_p_0), len(graphs_p_1)):
        splits_0.append(graphs_p_0[i: i+len(graphs_p_1)])


    if not os.path.exists('use_case_428_427_data_splits'):
        os.makedirs('use_case_428_427_data_splits') 

    splits = []
    for s in splits_0:
        tmp_merge = graphs_p_1 + s
        random.shuffle(tmp_merge)
        splits.append(tmp_merge)

    for i, s in enumerate(splits):
        if not os.path.exists('use_case_428_427_data_splits/split_' + str(i) + '/'):
            os.makedirs('use_case_428_427_data_splits/split_' + str(i) + '/') 

        save_json(s, 'use_case_428_427_data_splits/split_' + str(i) + '/all_data_' + str(i) + '.json')

        # Create the cv folds
        step = len(s)//5
        c = 0
        for j in range(0, len(s)-step, step):
            fold = s[j:j+step]
            rest = s[:j] + s[j+step:]
            cv = {'train_set': rest,
                'test_set': fold}
            save_json(cv, 'use_case_428_427_data_splits/split_' + str(i) + '/cv_split_' + str(c) + '.json')
            c += 1