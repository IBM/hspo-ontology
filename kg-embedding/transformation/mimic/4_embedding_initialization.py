import argparse
import os
from spacy.lang.en import English
import numpy as np
from transformers import AutoTokenizer, AutoModel
import torch
from helper import read_json, save_json, find_json_files, filter_list, filter_list_2
from helper import InputFile


class Embeddings:
    def __init__(self, emb_strategy, aggr_strategy='_', voc_path='_'):
        if voc_path=='_':
            self.len_v = 768
        else:
            self.voc = read_json(voc_path)
            self.len_v = len(self.voc)
        self.nlp = English()
        self.emb_strategy = emb_strategy
        if self.emb_strategy == 'bow':
            self.tokenizer = self.nlp.tokenizer
        elif self.emb_strategy == 'lm':
            self.tokenizer_BioBERT = AutoTokenizer.from_pretrained("dmis-lab/biobert-v1.1")
            self.BioBERT = AutoModel.from_pretrained("dmis-lab/biobert-v1.1")
            self.BioBERT.to(device)
        self.aggr_strategy = aggr_strategy
    
    def process_graph(self, graph_path):
        graph = read_json(graph_path)
        emb_list = []
        for t in graph:
            if t[0][0] == 'unknown':
                rep_s = np.zeros(self.len_v, dtype=int)
            else:
                if self.emb_strategy == 'bow':
                    s = self.tokenize_phrase(t[0][0])
                    rep_s = self.get_bow_rep(s)
                elif self.emb_strategy == 'lm':
                    rep_s = self.get_LM_rep(t[0][0])
            # If religion or race or marital status are unknown then initialize the node with a zero vector
            if t[2][0] == 'unknown':
                rep_o = np.zeros(self.len_v, dtype=int)
            else:
                if self.emb_strategy == 'bow':
                    o = self.tokenize_phrase(t[2][0])
                    rep_o = self.get_bow_rep(o)
                elif self.emb_strategy == 'lm':
                    rep_o = self.get_LM_rep(t[2][0])
            
            emb_list.append(((rep_s.tolist(), t[0][1], t[0][2]), t[1], (rep_o.tolist(), t[2][1], t[2][2])))
        del graph
        return emb_list

    
    def tokenize_phrase(self, s):
        tokens = self.tokenizer(s)
        tokens_list = [str(t).lower() for t in tokens]
        tokens_ready = []
        for t in tokens_list:
            if ' ' not in t:
                tokens_ready.append(t)
        return tokens_ready

    
    def get_bow_rep(self, p):
        bag_vector = np.zeros(len(self.voc), dtype=int)
        for w in p:
            bag_vector[self.voc.index(w)] += 1
        return bag_vector

    
    def get_LM_rep(self, p):
        x = self.tokenizer_BioBERT(p, return_tensors='pt')
        x.to(device)
        x = self.BioBERT(**x)[0]
        # If it is only one word, take its representation
        if x[0].shape[0] == 3:
            return x[0][1]
        else:
            if self.aggr_strategy == 'cls':
                return  x[0][0]
            elif self.aggr_strategy == 'avg':
                return torch.mean(x[0][1:-1], 0)
            elif self.aggr_strategy == 'sum':
                return torch.sum(x[0][1:-1], 0)


def extract_emb(input_path_grouped_data, input_path_graphs, output_path, directed,
                graph_version, extra_filter, emb_strategy, aggr_strategy='_', vocab_path='_'):
    emb = Embeddings(emb_strategy, aggr_strategy, vocab_path)
    filenames_to_be_sampled = InputFile(input_path_grouped_data, 
                                        ['428', '427'], 
                                        [['diagnoses', 'icd9_code'], ['diagnoses', 'icd9_code']]).key_list_or_operation

    if directed:
        graphs_0 = find_json_files(input_path_graphs + 'directed/0/v' + str(graph_version) + '/')
        graphs_1 = find_json_files(input_path_graphs + 'directed/1/v' + str(graph_version) + '/')
    else:
        graphs_0 = find_json_files(input_path_graphs + 'undirected/0/v' + str(graph_version) + '/')
        graphs_1 = find_json_files(input_path_graphs + 'undirected/1/v' + str(graph_version) + '/')
    graphs_0_filtered_ = filter_list(graphs_0, filenames_to_be_sampled)
    graphs_1_filtered_ = filter_list(graphs_1, filenames_to_be_sampled)
    if extra_filter:
        black_list_0 = read_json('missing_info_bl_graph_0_v1_undirected.json')
        graphs_0_filtered = filter_list_2(graphs_0_filtered_, black_list_0)
        black_list_1 = read_json('missing_info_bl_graph_1_v1_undirected.json')
        graphs_1_filtered = filter_list_2(graphs_1_filtered_, black_list_1)
    else:
        graphs_0_filtered = graphs_0_filtered_
        graphs_1_filtered = graphs_1_filtered_

    c = 0
    for p in graphs_0_filtered:
        c += 1
        emb_list = emb.process_graph(p)
        if emb_strategy == 'bow':
            if directed:
                full_output_path = output_path + 'directed/0/' + emb_strategy + '/v' + str(graph_version) + '/'
            else:
                full_output_path = output_path + 'undirected/0/' + emb_strategy + '/v' + str(graph_version) + '/'
            if not os.path.exists(full_output_path):
                os.makedirs(full_output_path) 
            save_json(emb_list, full_output_path + p.split('/')[-1])
        elif emb_strategy == 'lm':
            if directed:
                full_output_path = output_path + 'directed/0/' + emb_strategy + '/' + aggr_strategy + '/v' + str(graph_version) + '/'
            else:
                full_output_path = output_path + 'undirected/0/' + emb_strategy + '/' + aggr_strategy + '/v' + str(graph_version) + '/'
            if not os.path.exists(full_output_path):
                os.makedirs(full_output_path) 
            save_json(emb_list, full_output_path + p.split('/')[-1])
        
        if c % 500 == 0:
            print('{} graphs were processed' .format(c))

    for p in graphs_1_filtered:
        c += 1      
        emb_list = emb.process_graph(p)
        if emb_strategy == 'bow':
            if directed:
                full_output_path = output_path + 'directed/1/' + emb_strategy + '/v' + str(graph_version) + '/'
            else:
                full_output_path = output_path + 'undirected/1/' + emb_strategy + '/v' + str(graph_version) + '/'
            if not os.path.exists(full_output_path):
                os.makedirs(full_output_path) 
            save_json(emb_list, full_output_path + p.split('/')[-1])
        elif emb_strategy == 'lm':
            if directed:
                full_output_path = output_path + 'directed/1/' + emb_strategy + '/' + aggr_strategy + '/v' + str(graph_version) + '/'
            else:
                full_output_path = output_path + 'undirected/1/' + emb_strategy + '/' + aggr_strategy + '/v' + str(graph_version) + '/'
            if not os.path.exists(full_output_path):
                os.makedirs(full_output_path) 
            save_json(emb_list, full_output_path + p.split('/')[-1])
        
        if c % 500 == 0:
            print('{} graphs were processed' .format(c))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_path_grouped_data", default=None, type=str, required=True,
                        help = "The input path of the grouped json data after data preprocessing.")
    parser.add_argument("--input_path_graphs", default='data/triplet_format_graphs/', type=str, required=False,
                        help = "The input path of the transformed graphs.")
    parser.add_argument("--output_path", default='data/precalculated_embeddings/use_case_428_427/', type=str, required=False,
                        help = "The output path for storing the embeddings.")
    parser.add_argument("--directed", default=None, type=int, required=True,
                        help = "Int value to define if the graph is going to be directed (1) or no (0).")
    parser.add_argument("--graph_version", default=None, type=int, required=True,
                        help = "An id to define the graph version that is going to be used.")
    parser.add_argument("--vocab_path", default=None, type=str, required=True,
                        help = "The path to vocabulary. It is needed if BOW strategy is applied.")
    parser.add_argument("--extra_filter", default=None, type=int, required=True,
                        help = "Int value to define if the graphs with missing info (medication or disease or procedure list) are going to be removed (1) or no (0).")
    parser.add_argument("--emb_strategy", default=None, type=str, required=True,
                        help = "The strategy for embedding initialization. Choices: bow, lm")
    parser.add_argument("--aggr_strategy", default=None, type=str, required=False,
                        help = "The aggregation strategy for embedding initialization. Only applies for lm strategy. Choices: cls, avg, sum")

    args = parser.parse_args()

    # Define the device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    if args.emb_strategy == 'bow':
        extract_emb(input_path_grouped_data=args.input_path_grouped_data, 
                    input_path_graphs=args.input_path_graphs,
                    output_path=args.output_path, 
                    directed=args.directed,
                    graph_version=args.graph_version, 
                    extra_filter=args.extra_filter,
                    emb_strategy=args.emb_strategy, 
                    vocab_path=args.vocab_path)
    elif args.emb_strategy == 'lm':
        extract_emb(input_path_grouped_data=args.input_path_grouped_data, 
                    input_path_graphs=args.input_path_graphs,
                    output_path=args.output_path, 
                    directed=args.directed,
                    graph_version=args.graph_version, 
                    extra_filter=args.extra_filter,
                    emb_strategy=args.emb_strategy, 
                    aggr_strategy=args.aggr_strategy)
    else:
        print('Invalid embedding strategy is given. Possible strategies: bow, lm')

