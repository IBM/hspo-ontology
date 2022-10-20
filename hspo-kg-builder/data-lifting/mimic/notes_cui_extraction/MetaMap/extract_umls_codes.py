import pandas as pd
import pymetamap
import random
import os
from time import sleep
import argparse
import json

def read_csv(path):
    return pd.read_csv(path)


def read_json(path):
        with open(path) as json_file:
            return json.load(json_file)


def save_json(file, path):
    with open(path, 'w') as outfile:
        json.dump(file, outfile)



def get_keys_from_mm(concept, klist):
    conc_dict = concept._asdict()
    conc_list = [conc_dict.get(kk) for kk in klist]
    return(tuple(conc_list))


class MetaMapConnection:
    def __init__(self, lite, metamap_base_dir='', metamap_bin_dir='', 
                 metamap_pos_server_dir='', metamap_wsd_server_dir='', 
                 metamap_lite_base_dir=''):
        if lite:
            self.metamap_lite_base_dir = metamap_lite_base_dir
            self.mm = self.get_metamap_lite_instance()
        else:
            self.metamap_base_dir = metamap_base_dir
            self.metamap_bin_dir = metamap_bin_dir
            self.metamap_pos_server_dir = metamap_pos_server_dir
            self.metamap_wsd_server_dir = metamap_wsd_server_dir
            self.mm = self.get_metamap_instance()
    

    def get_metamap_lite_instance(self):
        mm = pymetamap.MetaMapLite.get_instance(self.metamap_lite_base_dir)
        return mm

    
    def get_metamap_instance(self):
        # Start servers
        os.system(self.metamap_base_dir + self.metamap_pos_server_dir + ' start') # Part of speech tagger
        os.system(self.metamap_base_dir + self.metamap_wsd_server_dir + ' start') # Word sense disambiguation 

        # Sleep a bit to give time for these servers to start up
        sleep(60)

        mm = pymetamap.MetaMap.get_instance(self.metamap_base_dir + self.metamap_bin_dir)
        return mm


class ExtractorUMLSOld:
    def __init__(self, notes_path, lite, metamap_lite_base_dir, metamap_base_dir, metamap_bin_dir, 
                 metamap_pos_server_dir, metamap_wsd_server_dir, output_data_path, filenames_to_be_done):
        # Read the csv with the notes.
        self.notes = read_csv(notes_path)
        # Drop the rows with unknown admission id (mapping cannot be done).
        self.notes_clear = self.notes.dropna(subset=['hadm_id'])
        # Transform the dataframe to dictionary with note aggregation
        self.notes_dict = self.dataframe_to_dictionary_notes()
        # Join the notes
        self.notes_dict_joined = self.join_notes()
        # Initialize an instance of MetaMap annotator
        self.lite = lite
        if lite:
            self.mm_conn = MetaMapConnection(lite=1, 
                                             metamap_lite_base_dir=metamap_lite_base_dir)
        else:
            self.mm_conn = MetaMapConnection(lite=0, 
                                             metamap_base_dir=metamap_base_dir,
                                             metamap_bin_dir=metamap_bin_dir, 
                                             metamap_pos_server_dir=metamap_pos_server_dir, 
                                             metamap_wsd_server_dir=metamap_wsd_server_dir,
                                             composite_phrase = 1)
        self.output_data_path = output_data_path
        self.files_to_be_done = read_json(filenames_to_be_done)


    def join_notes(self):
        notes_dict_joined = {}
        for k in self.notes_dict.keys():
            joined_text_0 = ' '.join(self.notes_dict[k])
            joined_text_1 = joined_text_0.replace('__', ' ')
            joined_text_2 = joined_text_1.replace('  ', '')
            joined_text_3 = joined_text_2.replace('  ', '')
            joined_text_4 = joined_text_3.replace('  ', '')
            joined_text_5 = joined_text_4.replace('*', '')
            joined_text_6 = joined_text_5.replace('|', '')
            notes_dict_joined[k] = joined_text_6
        return notes_dict_joined


    def dataframe_to_dictionary_notes(self):
        notes_dict = {}
        for _, row in self.notes_clear.iterrows():
            if str(row['subject_id']) + '_' + str(int(float(row['hadm_id'])))  not in notes_dict.keys():
                clean_text = self.remove_empty_strings(row['text'])
                notes_dict[str(row['subject_id']) + '_' + str(int(float(row['hadm_id'])))] = []
                notes_dict[str(row['subject_id']) + '_' + str(int(float(row['hadm_id'])))].extend(clean_text)
            else:
                # If there is a key for this subject_id + admission_id combination then extend the note list.
                clean_text = self.remove_empty_strings(row['text'])
                notes_dict[str(row['subject_id']) + '_' + str(int(float(row['hadm_id'])))].extend(clean_text)
        return notes_dict


    def remove_empty_strings(self, text):
        clean_text = []
        for r in text.split('\n'):
            if r == '':
                continue
            else:
                clean_text.append(r)
        return clean_text


    def get_umls_codes_of_notes(self):
        for k in self.notes_dict_joined.keys():
            if not(k.split('_')[0] + '_' + k.split('_')[1] in self.files_to_be_done['filenames']):
                continue
            if self.lite:
                cons, _ = self.mm_conn.mm.extract_concepts([self.notes_dict_joined[k]])
            else:
                cons, _ = self.mm_conn.mm.extract_concepts([self.notes_dict_joined[k]],
                                                           word_sense_disambiguation = True,
                                                           #restrict_to_sts = ['sosy'], # signs and symptoms
                                                           composite_phrase = 1) # for memory issues
            

            keys_of_interest = ['preferred_name', 'cui', 'semtypes', 'pos_info']
            cols = [get_keys_from_mm(cc, keys_of_interest) for cc in cons]
            results_df = pd.DataFrame(cols, columns = keys_of_interest)

            umls_dict = {'umls_codes': results_df['cui'].tolist(),
                         'textual_description': results_df['preferred_name'].tolist()}
            save_json(umls_dict, self.output_data_path + k.split('_')[0] + '_' + k.split('_')[1] + '.json')


class ExtractorUMLS:
    def __init__(self, notes_path, lite, metamap_lite_base_dir, metamap_base_dir, metamap_bin_dir, 
                 metamap_pos_server_dir, metamap_wsd_server_dir, output_data_path):
        # Read the json with the joined notes.
        self.notes = read_json(notes_path)
        # Initialize an instance of MetaMap annotator
        self.lite = lite
        if lite:
            self.mm_conn = MetaMapConnection(lite=1, 
                                             metamap_lite_base_dir=metamap_lite_base_dir)
        else:
            self.mm_conn = MetaMapConnection(lite=0, 
                                             metamap_base_dir=metamap_base_dir,
                                             metamap_bin_dir=metamap_bin_dir, 
                                             metamap_pos_server_dir=metamap_pos_server_dir, 
                                             metamap_wsd_server_dir=metamap_wsd_server_dir,
                                             composite_phrase = 1)
        self.output_data_path = output_data_path


    def remove_empty_strings(self, text):
        clean_text = []
        for r in text.split('\n'):
            if r == '':
                continue
            else:
                clean_text.append(r)
        return clean_text


    def get_umls_codes_of_notes(self):
        k_list = list(self.notes.keys())
        random.shuffle(k_list)
        for k in k_list:
            if self.lite:
                cons, _ = self.mm_conn.mm.extract_concepts([self.notes[k]])
            else:
                cons, _ = self.mm_conn.mm.extract_concepts([self.notes[k]],
                                                           word_sense_disambiguation = True,
                                                           #restrict_to_sts = ['sosy'], # signs and symptoms
                                                           composite_phrase = 1) # for memory issues
            

            keys_of_interest = ['preferred_name', 'cui', 'semtypes', 'pos_info']
            cols = [get_keys_from_mm(cc, keys_of_interest) for cc in cons]
            results_df = pd.DataFrame(cols, columns = keys_of_interest)

            umls_dict = {'umls_codes': results_df['cui'].tolist(),
                         'textual_description': results_df['preferred_name'].tolist()}
            save_json(umls_dict, self.output_data_path + k.split('_')[0] + '_' + k.split('_')[1] + '.json')
    

    def get_umls_codes_of_notes_divide_and_merge(self):
        step = 20000
        k_list = list(self.notes.keys())
        random.shuffle(k_list)
        for k in k_list:
            n = self.notes[k]
            cui_all, textual_all = [], []
            for i in range(0, len(n), step):
                if self.lite:
                    cons, _ = self.mm_conn.mm.extract_concepts([n[i:i+step]])
                else:
                    cons, _ = self.mm_conn.mm.extract_concepts([n[i:i+step]],
                                                                word_sense_disambiguation = True,
                                                                #restrict_to_sts = ['sosy'], # signs and symptoms
                                                                composite_phrase = 1) # for memory issues
                

                keys_of_interest = ['preferred_name', 'cui', 'semtypes', 'pos_info']
                cols = [get_keys_from_mm(cc, keys_of_interest) for cc in cons]
                results_df = pd.DataFrame(cols, columns = keys_of_interest)

                cui_all.extend(results_df['cui'].tolist())
                textual_all.extend(results_df['preferred_name'].tolist())

            umls_dict = {'umls_codes': cui_all,
                         'textual_description': textual_all}
            save_json(umls_dict, self.output_data_path + k.split('_')[0] + '_' + k.split('_')[1] + '.json')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--bucket_path", default=None, type=str, required=True,
                        help = "The path of the note buckets.")
    parser.add_argument("--bucket_id", default=None, type=str, required=True,
                        help = "The bucket id/number to indicate the one that is going to be processed.")
    parser.add_argument("--metamap_path", default=None, type=str, required=True,
                        help = "The path of metamap base directory.")
    parser.add_argument("--output_path", default=None, type=str, required=True,
                        help = "The path where the extracted umls codes are stored.")
    parser.add_argument("--divide_and_merge", default=0, type=int, required=False,
                        help = "This is a flag to define if the notes are going to be divided into subnotes and then processed by metamap. The final UMLS sublists are merged. Values: 0 or 1")

    args = parser.parse_args()

    if not os.path.exists(args.output_path):
        os.makedirs(args.output_path)

    ex = ExtractorUMLS(notes_path = args.bucket_path + 'notes_bucket_' + args.bucket_id + '.json',
                       lite = 1, 
                       metamap_lite_base_dir = args.metamap_path, 
                       metamap_base_dir = '',
                       metamap_bin_dir = '', 
                       metamap_pos_server_dir = '', 
                       metamap_wsd_server_dir = '',
                       output_data_path = args.output_path)
    
    if args.divide_and_merge:
        ex.get_umls_codes_of_notes_divide_and_merge()
    else:
        ex.get_umls_codes_of_notes()