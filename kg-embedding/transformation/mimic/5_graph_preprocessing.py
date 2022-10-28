import os
import argparse
import torch
import numpy as np
from torch_geometric.data import HeteroData
from helper import read_json, find_json_files 


class GraphProc:
    def __init__(self, graph_path, voc_path, unique_rel_triplets_path,
                 emb_strategy, label, output_path):
        self.g = read_json(graph_path)
        self.g_name = graph_path.split('/')[-1].split('.')[0]
        self.label = label
        self.emb_strategy = emb_strategy
        self.output_path = output_path
        self.unique_rel_triplets = read_json(unique_rel_triplets_path)
        if voc_path=='_':
            self.len_v = 768
        else:
            self.voc = read_json(voc_path)
            self.len_v = len(self.voc)
        #self.g_proc, self.valid = self.process()
        self.g_proc = self.process()

    def process(self):
        g_conv = self.convert()
        return g_conv
        # Check if the graph is valid
        #if g_conv.validate():
        #    return g_conv, 1
        #else:
        #    print('The transformed graph is not valid.')
        #    return g_conv, 0
    
    def convert(self):
        dict_str = {}
        dict_triplet_count = {}
        for t_emb in self.g:
            # Remember the triplet format: (embeddings, specific type, generic type)
            # for example in directed graph version 4: (embeddings, marital_status, demographic_info)
            k1_specific = t_emb[0][1]
            k1_generic = t_emb[0][2]
            k2_specific = t_emb[2][1]
            k2_generic = t_emb[2][2]
            if k1_generic not in dict_str.keys():
                dict_str[k1_generic] = [t_emb[0][0]]
            else:
                # Avoid adding the same node twice.
                if k1_specific not in ['patient', 'demographics', 'diseases', 'interventions', 'social_context',
                                       'procedure_provisioning_ICD9', 'procedure_provisioning_CPT', 
                                       'medication_provisioning', 'age', 'marital_status', 'religion', 
                                       'race', 'gender', 'age_group', 'employment', 'housing', 'household']:
                    dict_str[k1_generic].append(t_emb[0][0])
            if k2_generic not in dict_str.keys():
                dict_str[k2_generic] = [t_emb[2][0]]
            else:
                if k2_specific not in ['patient', 'demographics', 'diseases', 'interventions', 'social_context',
                                       'procedure_provisioning_ICD9', 'procedure_provisioning_CPT', 
                                       'medication_provisioning', 'age', 'marital_status', 'religion', 
                                       'race', 'gender', 'age_group', 'employment', 'housing', 'household']:
                    dict_str[k2_generic].append(t_emb[2][0])
            
            if t_emb[0][2] + '_' + t_emb[1] + '_' + t_emb[2][2] not in dict_triplet_count.keys():
                dict_triplet_count[t_emb[0][2] + '_' + t_emb[1] + '_' + t_emb[2][2]] = {'count': 1,
                                                                                        'triplet': (t_emb[0][2], t_emb[1], t_emb[2][2])}
            else:
                dict_triplet_count[t_emb[0][2] + '_' + t_emb[1] + '_' + t_emb[2][2]]['count'] += 1
            
        for k in dict_triplet_count.keys():
            s = dict_triplet_count[k]['triplet'][0]
            o = dict_triplet_count[k]['triplet'][2]
            s_count = len(dict_str[s])
            o_count = len(dict_str[o])
            rel_pairs = []
            # If the node has an unknown value (then it is initiliazed with zeros vector) then the adj. matrix for the relation will be empty
            if all(v == 0 for v in dict_str[o]):                
                dict_triplet_count[k]['COO_graph_connectivity'] = torch.LongTensor([[], []])
            else:
                for i1 in range(s_count):
                    for i2 in range(o_count):
                        rel_pairs.append([i1, i2])
                # https://pytorch-geometric.readthedocs.io/en/latest/notes/introduction.html
                #dict_triplet_count[k]['COO_graph_connectivity'] = torch.tensor(rel_pairs, dtype=torch.long).t().contiguous()
                dict_triplet_count[k]['COO_graph_connectivity'] = torch.LongTensor(rel_pairs).t().contiguous()


        # https://pytorch-geometric.readthedocs.io/en/latest/modules/data.html#torch_geometric.data.HeteroData
        data = HeteroData()
        for k in dict_str.keys():
            data[k].x = torch.FloatTensor(dict_str[k])
        
        rel_graph = []
        for k in dict_triplet_count.keys():
            t = dict_triplet_count[k]['triplet']
            data[t[0], t[1], t[2]].edge_index = torch.LongTensor(dict_triplet_count[k]['COO_graph_connectivity'])
            rel_graph.append([t[0], t[1], t[2]])
        
        # Check if some relations are missing from the graph
        # If this is the case add zero nodes and an empty adj. matrix
        for rel in self.unique_rel_triplets:
            if rel not in rel_graph:
                if rel[0] not in dict_str.keys():
                    data[rel[0]].x = torch.FloatTensor([np.zeros(self.len_v, dtype=int).tolist()])
                if rel[2] not in dict_str.keys():
                    data[rel[2]].x = torch.FloatTensor([np.zeros(self.len_v, dtype=int).tolist()])
                data[rel[0], rel[1], rel[2]].edge_index = torch.LongTensor([[0], [0]])
                #print(self.g_name)
                #print(rel)
        
        #data['patient'].y = torch.from_numpy(self.label).type(torch.long)
        data['patient'].y = torch.from_numpy(self.label).type(torch.float)

        return data
    
                
    def save_graph(self):
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)   
        torch.save(self.g_proc, self.output_path + self.g_name + '.pt')
        #if self.valid:      
        #    torch.save(self.g_proc, self.output_path + self.g_name + '.pt')
        #else:
        #    print('Invalid graph')
        

def extract_graphs(files_path, voc_path, unique_rel_triplets_path,
                   emb_strategy, label, output_path):
    graphs_emb = find_json_files(files_path)
    for g_p_emb in graphs_emb:
        g_obj = GraphProc(graph_path=g_p_emb, 
                          voc_path=voc_path, 
                          unique_rel_triplets_path=unique_rel_triplets_path,
                          emb_strategy=emb_strategy, 
                          label=label, 
                          output_path=output_path)
        g_obj.save_graph()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("--input_path_embeddings", default="data/precalculated_embeddings/use_case_428_427/", type=str, required=False,
                        help = "The input path of the precalculated embeddings.")
    parser.add_argument("--vocab_path", default=None, type=str, required=False,
                        help = "The path of the vocabulary. It is needed if BOW strategy is applied.")
    parser.add_argument("--unique_rel_triplets_path", default=None, type=str, required=True,
                        help = "The path of the list with the unique relation triplets.")
    parser.add_argument("--emb_strategy", default=None, type=str, required=True,
                        help = "The strategy for embedding initialization. Choices: bow, lm")
    parser.add_argument("--aggr_strategy", default=None, type=str, required=False,
                        help = "The aggregation strategy for embedding initialization. Only applies for lm strategy. Choices: cls, avg, sum")
    parser.add_argument("--output_path", default="data/processed_graphs/use_case_428_427/", type=str, required=False,
                        help = "The output path for storing the processed graphs.")
    parser.add_argument("--directed", default=None, type=int, required=True,
                        help = "Int value to define if the graph is going to be directed (1) or no (0).")
    parser.add_argument("--graph_version", default=None, type=int, required=True,
                        help = "An id to define the graph version that is going to be used.")

    args = parser.parse_args()
    
    if args.directed:
        if args.emb_strategy == 'bow':
            final_input_path_embeddings_0 = args.input_path_embeddings + 'directed/0/' + args.emb_strategy + '/' + 'v' + str(args.graph_version) + '/'
            final_input_path_embeddings_1 = args.input_path_embeddings + 'directed/1/' + args.emb_strategy + '/' + 'v' + str(args.graph_version) + '/'
            final_output_path = args.output_path + 'directed/' + args.emb_strategy + '/' + 'v' + str(args.graph_version) + '/'
        elif args.emb_strategy == 'lm':
            final_input_path_embeddings_0 = args.input_path_embeddings + 'directed/0/' + args.emb_strategy + '/' + args.aggr_strategy + '/' + 'v' + str(args.graph_version) + '/'
            final_input_path_embeddings_1 = args.input_path_embeddings + 'directed/1/' + args.emb_strategy + '/' + args.aggr_strategy + '/' + 'v' + str(args.graph_version) + '/'
            final_output_path = args.output_path + 'directed/' + args.emb_strategy + '/' + args.aggr_strategy + '/' + 'v' + str(args.graph_version) + '/'
    else:
        if args.emb_strategy == 'bow':
            final_input_path_embeddings_0 = args.input_path_embeddings + 'undirected/0/' + args.emb_strategy + '/' + 'v' + str(args.graph_version) + '/'
            final_input_path_embeddings_1 = args.input_path_embeddings + 'undirected/1/' + args.emb_strategy + '/' + 'v' + str(args.graph_version) + '/'
            final_output_path = args.output_path + 'undirected/' + args.emb_strategy + '/' + 'v' + str(args.graph_version) + '/'
        elif args.emb_strategy == 'lm':
            final_input_path_embeddings_0 = args.input_path_embeddings + 'undirected/0/' + args.emb_strategy + '/' + args.aggr_strategy + '/' + 'v' + str(args.graph_version) + '/'
            final_input_path_embeddings_1 = args.input_path_embeddings + 'undirected/1/' + args.emb_strategy + '/' + args.aggr_strategy + '/' + 'v' + str(args.graph_version) + '/'
            final_output_path = args.output_path + 'undirected/' + args.emb_strategy + '/' + args.aggr_strategy + '/' + 'v' + str(args.graph_version) + '/'

    # Label: 0
    extract_graphs(files_path=final_input_path_embeddings_0, 
                   voc_path=args.vocab_path, 
                   unique_rel_triplets_path=args.unique_rel_triplets_path,
                   emb_strategy=args.emb_strategy, 
                   label=np.array(0), 
                   output_path=final_output_path)      
    # Label: 1
    extract_graphs(files_path=final_input_path_embeddings_1, 
                   voc_path=args.vocab_path, 
                   unique_rel_triplets_path=args.unique_rel_triplets_path,
                   emb_strategy=args.emb_strategy, 
                   label=np.array(1), 
                   output_path=final_output_path)
