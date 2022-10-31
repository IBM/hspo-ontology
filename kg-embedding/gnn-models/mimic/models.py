import torch
import torch.nn.functional as F
from torch_geometric.nn import SAGEConv, RGCNConv, GATv2Conv, Linear


class Net1_1(torch.nn.Module):
    def __init__(self, hidden_channels):
        super().__init__()
        self.conv1 = SAGEConv((-1, -1), hidden_channels[0])
        self.conv2 = SAGEConv((-1, -1), hidden_channels[1])
        self.linear1 = Linear(hidden_channels[1], 1)
    

    def forward(self, x, edge_index):
        x = F.relu(self.conv1(x=x, edge_index=edge_index))
        x = F.relu(self.conv2(x=x, edge_index=edge_index))
        x = self.linear1(x)

        return x


class Net1_2(torch.nn.Module):
    def __init__(self, hidden_channels):
        super().__init__()
        self.conv1 = SAGEConv((-1, -1), hidden_channels[0])
        self.conv2 = SAGEConv((-1, -1), hidden_channels[1])
        self.conv3 = SAGEConv((-1, -1), 1)
    

    def forward(self, x, edge_index):
        x = F.relu(self.conv1(x=x, edge_index=edge_index))
        x = F.relu(self.conv2(x=x, edge_index=edge_index))
        x = self.conv3(x, edge_index=edge_index)

        return x


class Net2_1(torch.nn.Module):
    def __init__(self, hidden_channels):
        super().__init__()
        self.conv1 = GATv2Conv((-1, -1), hidden_channels[0], heads=1, add_self_loops=False)
        self.linear1 = Linear(-1, hidden_channels[0])
        self.conv2 = GATv2Conv((-1, -1), hidden_channels[1], heads=1, add_self_loops=False)
        self.linear2 = Linear(-1, hidden_channels[1])
        self.linear3 = Linear(hidden_channels[1], 1)
    

    def forward(self, x, edge_index):
        x = F.relu(self.conv1(x=x, edge_index=edge_index) + self.linear1(x))
        x = F.relu(self.conv2(x=x, edge_index=edge_index) + self.linear2(x))
        x = self.linear3(x)

        return x


class Net2_2(torch.nn.Module):
    def __init__(self, hidden_channels):
        super().__init__()
        self.conv1 = GATv2Conv((-1, -1), hidden_channels[0], heads=1, add_self_loops=False)
        self.linear1 = Linear(-1, hidden_channels[0])
        self.conv2 = GATv2Conv((-1, -1), hidden_channels[1], heads=1, add_self_loops=False)
        self.linear2 = Linear(-1, hidden_channels[1])
        self.conv3 = GATv2Conv((-1, -1), 1, heads=1, add_self_loops=False)
        self.linear3 = Linear(-1, 1)
    

    def forward(self, x, edge_index):
        x = F.relu(self.conv1(x=x, edge_index=edge_index) + self.linear1(x))
        x = F.relu(self.conv2(x=x, edge_index=edge_index) + self.linear2(x))
        x = self.conv3(x=x, edge_index=edge_index) + self.linear3(x)

        return x

