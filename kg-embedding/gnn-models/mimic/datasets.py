import torch_geometric.transforms as T
import torch
import os 
from torch_geometric.data import Dataset
from helper import read_json


class MyDataset(Dataset):
    def __init__(self, input_path, filenames, directed, add_self_loops, transform=None):
        super(MyDataset, self).__init__('.', transform, None, None)
        self.root = input_path
        self.filenames = filenames
        self.directed = directed
        self.add_self_loops = add_self_loops
        self.graph_paths = self.find_pt_files()
        self.metadata = self.get(42).metadata()


    def len(self):
        return len(self.graph_paths)


    def get(self, idx):
        g = torch.load(self.graph_paths[idx])

        return self._process(g)


    def find_pt_files(self):
        files_l = []
        for root_, _, files in os.walk(self.root):
            for file in files:
                if file.endswith(".pt") and file.split('.')[0] in self.filenames:
                    files_l.append(os.path.join(root_, file))

        return files_l

    
    def _download(self):
        return


    def _process(self, g):
        if not(self.directed):
            g = T.ToUndirected()(g)
        if self.add_self_loops:
            g = T.AddSelfLoops()(g)
        #g = T.NormalizeFeatures()(g)
        return g
    
    
    def __repr__(self):
        return '{}()'.format(self.__class__.__name__)



