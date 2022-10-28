# Person-Centric Knowledge Graph Extraction using MIMIC-III dataset: An ICU-readmission prediction study 

## Graph Neural Networks (GNNs)

## Setup
### Requirements
- Python 3.7+          


### Execution - Description
- Run the ```0_data_split.py --input_path_graphs_0 --input_path_graphs_1``` script to create the different balanced dataset splits for the experimentation. Arguments:
    - input_path_graphs_0: The path of the precalculated embeddings of the graphs with 0 label (no readmission). Any path with precalculated embeddings (KG transformation step) can be used.
    - input_path_graphs_1: The path of the precalculated embeddings of the graphs with 1 label (readmission). Any path with precalculated embeddings (KG transformation step) can be used.

A bash script (```run_graph_processing.sh [-h] [-g f v e p d o s a]```) to execute the full pipeline end-to-end is also available. The paths (input, output, conda source, conda environments) should be updated accordingly. 

### Notes 

## References
```

```
