# Person-Centric Knowledge Graph Extraction using MIMIC-III dataset: An ICU-readmission prediction study 

## Graph Neural Networks (GNNs)

## Setup
### Requirements
- Python 3.7+ 
- tqdm (tested with version 4.64.0) 
- scikit-learn (tested with version 1.1.2)
- pytorch (tested with version 1.12.1)
- pytorch_geometric (tested with version 2.1.0)                          


### Execution - Description
- Run the ```0_data_split.py --input_path_graphs_0 --input_path_graphs_1``` script to create the different balanced dataset splits for the experimentation. Arguments:
    - input_path_graphs_0: The path of the precalculated embeddings of the graphs with 0 label (no readmission). Any path with precalculated embeddings (KG transformation step) can be used.
    - input_path_graphs_1: The path of the precalculated embeddings of the graphs with 1 label (readmission). Any path with precalculated embeddings (KG transformation step) can be used.
- Run the ```main.py --input_path_data_files --input_path_graphs --directed --add_self_loop -batch_size --model_id --use_bases --num_bases --learning_rate --weight_decay --epochs --output_path``` to execute the training and evaluation of the models. Arguments:
    - input_path_data_files: The input path of the data files (e.g. <i>use_case_428_427_data_splits/split_0/cv_split_0.json</i>).
    - input_path_graphs: The input path of the processed graphs (transformation step).
    - directed: Int value to define if the graph is going to be directed (1) or no (0).
    - add_self_loop: Int value to define if self loops are going to be added in the graph (1) or no (0).
    - batch_size: The size of the batch.
    - model_id: The model id. Choices: 1_1, 1_2, 2_1, 2_2
    - use_bases: Define if basis-decomposition regularization \[1\] is applied (1) or no (0).
    - num_bases: The number of bases for the basis-decomposition technique.
    - learning_rate: The learning rate for the optimizer.
    - weight_decay: The weight decay for the optimizer.
    - epochs: The number of training epochs.
    - output_path: The output path for saving the model.

A bash script (```run_experiments.sh [-h] [-in d s a o l b m u n r w e x]```) to execute the experimental setup is also available. The paths (input, output, conda source, conda environments) should be updated accordingly. 

## References
```
[1] Schlichtkrull, Michael, et al. "Modeling relational data with graph convolutional networks." European semantic web conference. Springer, Cham, 2018.
```
