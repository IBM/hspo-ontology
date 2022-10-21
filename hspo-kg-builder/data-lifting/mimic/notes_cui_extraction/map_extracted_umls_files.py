import argparse
import os
from utils_ import find_json_files, read_json, save_json



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--umls_codes_path", default=None, type=str, required=True,
                        help = "The path where the extracted UMLS codes are stored.")
    parser.add_argument("--output_path", default=None, type=str, required=True,
                        help = "The path where the task-valid extracted UMLS files are going to be stored.")
    
    args = parser.parse_args()

    extracted_files = find_json_files(args.umls_codes_path)
    mapping = read_json('../data/processed_data/key_mapping_from_total_to_task_valid.json')

    if not os.path.exists(args.output_path):
        os.makedirs(args.output_path)

    for ex_f in extracted_files:
        ex_f_dict = read_json(args.umls_codes_path + ex_f + '.json')
        try:
            save_json(ex_f_dict, args.output_path + mapping[ex_f] + '.json')
        except:
            pass