# Person-Centric Knowledge Graph Extraction using MIMIC-III dataset: An ICU-readmission prediction study 

## Knowledge Graph Transformation

## Setup
### Requirements
- Python 3.5+
- rdflib (tested with version 6.1.1)
- 


### Execution - Description
The generated Knowledge Graphs (kg-generation step) are in RDF format. So they have to be transformed in pytorch-geometric friendly format to be used for Graph Neural Network (GNN) training. In this implementation the extracted graphs, that contain URIs with textual description, are used (strategy 2 in kg-generation step). The following steps are required for the transformation:
- Run the ```1_graph_transformation.py --input_path --output_path --directed --graph_version``` script to transform the graphs from RDF format to triplet format. In total, there are 13 different graph versions, 6 undirected and 7 directed. Look to the corresponding .pdf file for more information. Arguments:
    - input_path: The input path with the ontology-mapped graphs.
    - output_path: The path for storing the transformed graphs.
    - directed: Int value to define if the graph is going to be directed (1) or no. (0)
    - graph_version: The ID to define the graph version that is going to be used. Values: 0, 1, ...
- Run the ```2_find_graphs_with_missing_info_v1.py --input_path``` script find graphs with missing information. Some of the records in MIMIC-III dataset are not complete. The first version of the undirected graphs is needed. The information of interest that might be missing is related to diseases, medication, and procedures. Arguments:
    - input_path: The input path with the graphs. (e.g. <i>data/triplet_format_graphs/</i>)

### Notes