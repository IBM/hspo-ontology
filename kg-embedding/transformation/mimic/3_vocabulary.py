import argparse
import os
from helper import read_json, save_json, find_json_files, filter_list, filter_list_2
from helper import InputFile
from spacy.lang.en import English


class Vocabulary:
    def __init__(self, input_path_grouped_data, input_path_graphs, directed, graph_version, extra_filter):
        # Take the files for the specific use case (428-->heart failure, 427-->dysrhythmia)
        self.filenames_to_be_sampled = InputFile(input_path_grouped_data, 
                                                 ['428', '427'], 
                                                 [['diagnoses', 'icd9_code'], ['diagnoses', 'icd9_code']]).key_list_or_operation

        if directed:
            self.graphs_0 = find_json_files(input_path_graphs + 'directed/0/v' + str(graph_version) + '/')
            self.graphs_1 = find_json_files(input_path_graphs + 'directed/1/v' + str(graph_version) + '/')
        else:
            self.graphs_0 = find_json_files(input_path_graphs + 'undirected/0/v' + str(graph_version) + '/')
            self.graphs_1 = find_json_files(input_path_graphs + 'undirected/1/v' + str(graph_version) + '/')
        self.graphs_0_filtered_ = filter_list(self.graphs_0, self.filenames_to_be_sampled)
        self.graphs_1_filtered_ = filter_list(self.graphs_1, self.filenames_to_be_sampled)
        if extra_filter:
            self.black_list_0 = read_json('missing_info_bl_graph_0_v1_undirected.json')
            self.graphs_0_filtered = filter_list_2(self.graphs_0_filtered_, self.black_list_0)
            self.black_list_1 = read_json('missing_info_bl_graph_1_v1_undirected.json')
            self.graphs_1_filtered = filter_list_2(self.graphs_1_filtered_, self.black_list_1)
        else:
            self.graphs_0_filtered = self.graphs_0_filtered_
            self.graphs_1_filtered = self.graphs_1_filtered_
        self.nlp = English()
        #self.nlp = spacy.load("en_core_sci_lg")
        self.tokenizer = self.nlp.tokenizer
        #self.tokenizer = Tokenizer(self.nlp.vocab)
        self.rel_list, self.unique_rel_triplets, self.vocabulary, self.vocabulary_dict = self.get_vocabulary()
    
    def get_vocabulary(self):
        voc_list_1, rel_list, unique_rel_triplets = self.get_initial_voc_list()
        voc_list_2 = self.tokenize_phrases(voc_list_1)
        voc_list_3 = self.flatten_list(voc_list_2)
        voc = self.create_dict(voc_list_3)
        return rel_list, unique_rel_triplets, voc_list_3, voc
    

    def get_initial_voc_list(self):
        voc_list = []
        rel_list = []
        unique_rel_triplets = []
        count = 0
        for p in self.graphs_0_filtered:
            f = read_json(p)
            for t in f:
                if t[0][0] not in voc_list:
                    voc_list.append(t[0][0].lower())
                if t[2][0] not in voc_list:
                    voc_list.append(t[2][0].lower())
                if t[1] not in rel_list:
                    rel_list.append(t[1])
                if (t[0][2], t[1], t[2][2]) not in unique_rel_triplets:
                    unique_rel_triplets.append((t[0][2], t[1], t[2][2]))

            count += 1
            if (count % 1000) == 0:
                print('{} graphs are processed' .format(count))
        
        for p in self.graphs_1_filtered:
            f = read_json(p)
            for t in f:
                if t[0][0] not in voc_list:
                    voc_list.append(t[0][0].lower())
                if t[2][0] not in voc_list:
                    voc_list.append(t[2][0].lower())
                if t[1] not in rel_list:
                    rel_list.append(t[1])
                if (t[0][2], t[1], t[2][2]) not in unique_rel_triplets:
                    unique_rel_triplets.append((t[0][2], t[1], t[2][2]))

            count += 1
            if (count % 1000) == 0:
                print('{} graphs are processed' .format(count))
        
        return sorted(voc_list), rel_list, unique_rel_triplets
    

    def tokenize_phrases(self, l):
        l_tokenized = []
        for p in l:
            tokens = self.tokenizer(p)
            l_tokenized.append([str(t) for t in tokens])
        return l_tokenized
    

    def flatten_list(self, l):
        l_flattened = []
        for p in l:
            for w in p:
                if w not in l_flattened and ' ' not in w:
                    l_flattened.append(w)
        return sorted(l_flattened)

    
    def create_dict(self, l):
        dict_ = {}
        c = 1
        for w in l:
            dict_[w] = c
            c += 1
        return dict_


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_path_grouped_data", default=None, type=str, required=True,
                        help = "The input path of the grouped json data after data preprocessing.")
    parser.add_argument("--input_path_graphs", default='data/triplet_format_graphs/', type=str, required=False,
                        help = "The input path of the transformed graphs.")
    parser.add_argument("--output_path", default='data/vocabularies/', type=str, required=False,
                        help = "The output path where the vocabularies are stored.")
    parser.add_argument("--directed", default=None, type=int, required=True,
                        help = "Int value to define if the graph is going to be directed (1) or no (0).")
    parser.add_argument("--graph_version", default=None, type=int, required=True,
                        help = "An id to define the graph version that is going to be used.")
    parser.add_argument("--extra_filter", default=None, type=int, required=True,
                        help = "Int value to define if the graphs with missing info (medication or disease or procedure list) are going to be removed (1) or no (0).")
    
    args = parser.parse_args()
    
    voc = Vocabulary(args.input_path_grouped_data, args.input_path_graphs, 
                     args.directed, args.graph_version, args.extra_filter)
    
    if not os.path.exists(args.output_path):
        os.makedirs(args.output_path) 
    
    if args.directed:
        if args.extra_filter == 1:
            save_json(voc.vocabulary, args.output_path + 'vocab_list_use_case_428_427_spacy_directed_v' + str(args.graph_version) + '_without_missing_info.json')
            save_json(voc.vocabulary_dict, args.output_path + 'vocab_dict_use_case_428_427_spacy_directed_v' + str(args.graph_version) + '_without_missing_info.json')
        else:
            save_json(voc.vocabulary, args.output_path + 'vocab_list_use_case_428_427_spacy_directed_v' + str(args.graph_version) + '.json')
            save_json(voc.vocabulary_dict, args.output_path + 'vocab_dict_use_case_428_427_spacy_directed_v' + str(args.graph_version) + '.json')
            
        save_json(voc.rel_list, args.output_path + 'relation_labels_directed_v' + str(args.graph_version) + '.json')
        save_json(voc.unique_rel_triplets, args.output_path + 'unique_rel_triplets_directed_v' + str(args.graph_version) + '.json')
    else:
        if args.extra_filter == 1:
            save_json(voc.vocabulary, args.output_path + 'vocab_list_use_case_428_427_spacy_undirected_v' + str(args.graph_version) + '_without_missing_info.json')
            save_json(voc.vocabulary_dict, args.output_path + 'vocab_dict_use_case_428_427_spacy_undirected_v' + str(args.graph_version) + '_without_missing_info.json')
        else:
            save_json(voc.vocabulary, args.output_path + 'vocab_list_use_case_428_427_spacy_undirected_v' + str(args.graph_version) + '.json')
            save_json(voc.vocabulary_dict, args.output_path + 'vocab_dict_use_case_428_427_spacy_undirected_v' + str(args.graph_version) + '.json')
            
        save_json(voc.rel_list, args.output_path + 'relation_labels_undirected_v' + str(args.graph_version) + '.json')
        save_json(voc.unique_rel_triplets, args.output_path + 'unique_rel_triplets_undirected_v' + str(args.graph_version) + '.json')
