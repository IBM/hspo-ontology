import argparse
from utils_ import InputFile

def count_0_1_labels(file):
    count_0 = 0
    count_1 = 0
    for k1 in file.keys():
        for k2 in file[k1].keys():
            if file[k1][k2]['readmission'] == '1':
                count_1 += 1
            else:
                count_0 += 1
    
    print('Label 0: {}' .format(count_0))
    print('Label 1: {}' .format(count_1))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_path", default='data/processed_data/4_data_after_adding_notes_info_grouped_icd9.json', type=str, required=False,
                        help = "The path of the final json file with the data.")
    parser.add_argument("--query_codes", nargs="+", default=['428', '427'], required=False,
                        help = "The list of codes (ICD9) that are used to create the use case.")
    parser.add_argument("--query_code_descriptions", nargs="+", action='append', required=False,
                        help = "The list of the description (keys) of the codes (ICD9) that are used to create the use case. It is used to properly parse the json file.")

    args = parser.parse_args()

    use_case = InputFile(args.data_path, 
                         args.query_codes, 
                         args.query_code_descriptions)

    count_0_1_labels(use_case.sampled_file_or_operation)  