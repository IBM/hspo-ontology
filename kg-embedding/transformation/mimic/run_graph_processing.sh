#!/bin/bash

############################################################
# Help                                                     #
############################################################
Help()
{
   # Display Help
   echo "Description of parameters."
   echo
   echo "Example: run_graph_processing.sh -g 1 -f 1 -v 1 -e 1 -p 1 -d 0 -o 1 -s 'bow' -a '_'"
   echo "Parameters:"
   echo "h     Call the help function."
   echo "g     Run the 'graph_transformation' script. Values: 0 or 1"
   echo "f     Run the 'find_graphs_with_missing_info_v1' script. Values: 0 or 1"
   echo "v     Run the 'vocabulary' script. Values: 0 or 1"
   echo "e     Run the 'embedding_initialization' script. Values: 0 or 1"
   echo "p     Run the 'graph_preprocessing' script. Values: 0 or 1"
   echo "d     Directed (1) or Undected graph (0). Values: 0 or 1"
   echo "o     Graph version. Values: {1, 2, 3, 4, 5, 6, (7)}"
   echo "s     Embedding strategy. Values: 'bow' or 'lm'"
   echo "a     Aggregation strategy. Values: 'cls', 'avg', 'sum', '_'"
}


usage="$(basename "$0") [-h] [-g f v e p d o s a] -- program to run the graph processing pipeline"

if [ "$1" == "-h" ] ; then
    echo "$usage"
    Help
    exit 0
fi
 
# A string with command options
options=$@

while getopts g:f:v:e:p:d:o:s:a: options
do
    case "${options}" in
        g) graph_transformation=${OPTARG};;
        f) finding_missing_info=${OPTARG};; 
        v) vocabulary_creation=${OPTARG};;
        e) emb_extraction=${OPTARG};;
        p) graph_preprocessing=${OPTARG};;
        d) directed=${OPTARG};;
        o) graph_version=${OPTARG};;
        s) emb_strategy=${OPTARG};;
        a) aggr_strategy=${OPTARG};;
    esac
done


source /opt/share/anaconda3-2019.03/x86_64/etc/profile.d/conda.sh

conda activate conda_envs/rdflib

if [ $graph_transformation -eq 1 ]
then
    echo 'Graph transformation is starting ...'
    input_path_graph_transformation='data/with_new_URI/'
    output_path_graph_transformation='data/triplet_format_graphs/'

    python 1_graph_transformation.py --input_path $input_path_graph_transformation --output_path $output_path_graph_transformation --directed $directed  --graph_version $graph_version
    echo 'Graph transformation is completed.'
fi


if [ $finding_missing_info -eq 1 ]
then
    if [ $directed -eq 0 ] && [ $graph_version -eq 1 ]
    then
        input_path_missing_info='data/triplet_format_graphs/'
        python 2_find_graphs_with_missing_info_v1.py --input_path $input_path_missing_info
    fi
fi


conda deactivate
conda activate conda_envs/spacy

if [ $vocabulary_creation -eq 1 ]
then
    echo 'Vocabulary creation is starting ...'
    input_path_grouped_data='../../../hspo-kg-builder/data-lifting/mimic/data/processed_data/4_data_after_adding_notes_info_grouped_icd9.json'
    input_path_graphs='data/triplet_format_graphs/'
    extra_filter=1

    python 3_vocabulary.py --input_path_grouped_data $input_path_grouped_data --input_path_graphs $input_path_graphs --directed $directed --graph_version $graph_version --extra_filter $extra_filter
    echo 'Vocabulary creation is completed.'
fi


if [ $emb_extraction -eq 1 ]
then
    echo 'Embedding initialization is starting ...'
    input_path_grouped_data='../../../hspo-kg-builder/data-lifting/mimic/data/processed_data/4_data_after_adding_notes_info_grouped_icd9.json'
    input_path_graphs='data/triplet_format_graphs/'
    output_path_emb='data/precalculated_embeddings/use_case_428_427/'
    extra_filter=1
    if [ $directed -eq 1 ]
    then
        vocab_path='data/vocabularies/vocab_list_use_case_428_427_spacy_directed_v'${graph_version}'_without_missing_info.json'
    else
        vocab_path='data/vocabularies/vocab_list_use_case_428_427_spacy_undirected_v'${graph_version}'_without_missing_info.json'
    fi

    python 4_embedding_initialization.py --input_path_grouped_data $input_path_grouped_data --input_path_graphs $input_path_graphs --output_path $output_path_emb --directed $directed --graph_version $graph_version --vocab_path $vocab_path --extra_filter $extra_filter --emb_strategy $emb_strategy --aggr_strategy $aggr_strategy 
    echo 'Embedding initialization is completed.'
fi


conda deactivate
conda activate conda_envs/pytorch

if [ $graph_preprocessing -eq 1 ]
then
    echo 'Graph preprocessing is starting ...'
    if [ $directed -eq 1 ]
    then
        unique_rel_triplets_path='data/vocabularies/unique_rel_triplets_directed_v'${graph_version}'.json'
    else
        unique_rel_triplets_path='data/vocabularies/unique_rel_triplets_undirected_v'${graph_version}'.json'
    fi
    output_path_emb='data/precalculated_embeddings/use_case_428_427/'
    output_path_processed_graphs='data/processed_graphs/use_case_428_427/'
    if [ $emb_strategy = 'bow' ]
    then
        if [ $directed -eq 1 ]
        then
            vocab_path='data/vocabularies/vocab_list_use_case_428_427_spacy_directed_v'${graph_version}'_without_missing_info.json'
        else
            vocab_path='data/vocabularies/vocab_list_use_case_428_427_spacy_undirected_v'${graph_version}'_without_missing_info.json'
        fi
    else
        vocab_path='_'
    fi

    python 5_graph_preprocessing.py --input_path_embeddings $output_path_emb --vocab_path $vocab_path --unique_rel_triplets_path $unique_rel_triplets_path --emb_strategy $emb_strategy --aggr_strategy $aggr_strategy --output_path $output_path_processed_graphs --directed $directed --graph_version $graph_version
    echo 'Graph preprocessing is completed.'
fi