# Person-Centric Knowledge Graph Extraction using MIMIC-III dataset: An ICU-readmission prediction study 

## Knowledge Graph Transformation

## Setup
### Requirements
- Python 3.7+
- rdflib (tested with version 6.1.1)
- spacy (tested with version 3.4.1)    
- pytorch (tested with version 1.12.1)                     
- transformers (tested with version 4.21.2)        
- tokenizers (tested with version 0.12.1)        
- numpy (tested with version 1.23.2)
- pytorch_geometric (tested with version 2.1.0)           


### Execution - Description
The generated Knowledge Graphs (kg-generation step) are in RDF format. So they have to be transformed in pytorch-geometric friendly format to be used for Graph Neural Network (GNN) training. In this implementation the extracted graphs, that contain URIs with textual description, are used (strategy 2 in kg-generation step). The following steps are required for the transformation:
- Run the ```1_graph_transformation.py --input_path --output_path --directed --graph_version``` script to transform the graphs from RDF format to triplet format. In total, there are 13 different graph versions, 6 undirected and 7 directed. Look to the corresponding .pdf file for more information. Arguments:
    - input_path: The input path with the ontology-mapped graphs.
    - output_path: The path for storing the transformed graphs.
    - directed: Int value to define if the graph is going to be directed (1) or no. (0)
    - graph_version: The ID to define the graph version that is going to be used. Values: 0, 1, ...
- Run the ```2_find_graphs_with_missing_info_v1.py --input_path``` script find graphs with missing information. Some of the records in MIMIC-III dataset are not complete. The first version of the undirected graphs is needed. The information of interest that might be missing is related to diseases, medication, and procedures. Arguments:
    - input_path: The input path with the graphs. (e.g. <i>data/triplet_format_graphs/</i>)
- Run the ```3_vocabulary.py --input_path_grouped_data --input_path_graphs --output_path --directed --graph_version --extra_filter``` script to create the vocabulary. The use case with patients that have heart failure (ICD9 code: 428) or cardiac_dysrhythmias (ICD9 code: 427) has been predefined. Arguments:
    - input_path_grouped_data: The input path of the grouped json data after data preprocessing (AKA <i>4_data_after_adding_notes_info_grouped_icd9.json</i>).
    - input_path_graphs: The input path of the transformed graphs.
    - output_path: The output path where the vocabularies are stored.
    - directed: Value to define if the graph is going to be directed (1) or no (0).
    - graph_version: The id to define the graph version that is going to be used.
    - extra_filter: Value to define if the graphs with missing info (medication or disease or procedure list) are going to be removed (1) or no (0).
- Run the ```4_embedding_initialization.py --input_path_grouped_data --input_path_graphs --output_path --directed --graph_version --vocab_path --extra_filter --emb_strategy --aggr_strategy``` script to pre-compute and initialize the embeddings of every node in the graph. Arguments:
    - input_path_grouped_data: The input path of the grouped json data after data preprocessing (AKA <i>4_data_after_adding_notes_info_grouped_icd9.json</i>).
    - input_path_graphs: The input path of the transformed graphs.
    - output_path: The output path where the embeddings are stored. 
    - directed: Value to define if the graph is going to be directed (1) or no (0).
    - graph_version: The id to define the graph version that is going to be used.
    - vocab_path: The path to vocabulary. It is needed if BOW strategy is applied.
    - extra_filter: Value to define if the graphs with missing info (medication or disease or procedure list) are going to be removed (1) or no (0).
    - emb_strategy: The strategy for embedding initialization. Choices: bow, lm. The BOW strategy corresponds to Bag-of-Words model \[1\]. The LM strategy corresponds to pre-trained BioBERT \[2\] usage. 
    - aggr_strategy: The aggregation strategy for embedding initialization. Only applies for lm strategy. Choices: cls, avg, sum
- Run the ```5_graph_preprocessing.py --input_path_embeddings --vocab_path --unique_rel_triplets_path --emb_strategy --aggr_strategy --output_path --directed --graph_version``` script to finally transform the graph in .pt format that can be used for GNN training using <a target="_blank" href="https://pytorch-geometric.readthedocs.io/en/latest/">PyTorch Geometric</a> framework. Arguments:
    - input_path_embeddings: The input path of the precalculated embeddings.
    - vocab_path: The path of the vocabulary. It is needed if BOW strategy is applied.
    - unique_rel_triplets_path: The path of the list with the unique relation triplets. This file is created after the third step (vocabulary creation).
    - emb_strategy: The strategy for embedding initialization. Choices: bow, lm
    - aggr_strategy: The aggregation strategy for embedding initialization. Only applies for lm strategy. Choices: cls, avg, sum
    - output_path: The output path where the processed graphs are going to be stored.
    - directed: Value to define if the graph is going to be directed (1) or no (0).
    - graph_version: The id to define the graph version that is going to be used.

A bash script (```run_graph_processing.sh [-h] [-g f v e p d o s a]```) to execute the full pipeline end-to-end is also available. The paths (input, output, conda source, conda environments) should be updated accordingly. 

### Notes
- BioBERT is used as the selected Language Model in the  embedding initialization step because of the medical domain (MIMIC-III) of the application. Different generic or domain-specific Language Models can be easily used for other applications. 

## References
```
[1] Harris, Zellig S. "Distributional structure." Word 10.2-3 (1954): 146-162.
[2] Lee, Jinhyuk, et al. "BioBERT: a pre-trained biomedical language representation model for biomedical text mining." Bioinformatics 36.4 (2020): 1234-1240.
```
