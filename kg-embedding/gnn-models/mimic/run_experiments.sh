#!/bin/bash

############################################################
# Help                                                     #
############################################################
Help()
{
   # Display Help
   echo "Description of parameters."
   echo
   echo "Example: run_experiments.sh -d 0 -s 'lm' -a 'cls' -o 1 -l 1 -b 32 -m '1_2' -u 1 -n 5 -r 0.001 -w 0.0005 -e 100 -x 1"
   echo "Parameters:"
   echo "h     Call the help function."
   echo "d     Directed (1) or Undected graph (0). Values: 0 or 1"
   echo "s     Embedding strategy. Values: 'bow' or 'lm'"
   echo "a     Aggregation strategy. Values: 'cls', 'avg', 'sum', '_'"
   echo "o     Graph version. Values: {1, 2, 3, 4, 5, 6, (7)}"
   echo "l     Adding a self loop (1) in the graph or no (0). Values: 0 or 1"
   echo "b     The batch size, e.g. 32, 64, etc."
   echo "m     The model id. Values: 1_1, 1_2, 2_1, 2_2"
   echo "u     Using bases (1) or no (0). Values: 0 or 1"
   echo "n     The number of bases, if some are used. e.g. 5"
   echo "r     The learning rate for training. e.g. 0.001"
   echo "w     The weight decay parameter. e.g. 0.0005"
   echo "e     The number of training epochs. e.g. 100"
   echo "x     The experiment id"
}


usage="$(basename "$0") [-h] [-in d s a o l b m u n r w e x] -- program to run the experiment pipeline"

if [ "$1" == "-h" ] ; then
    echo "$usage"
    Help
    exit 0
fi

 
# A string with command options
options=$@

while getopts d:s:a:o:l:b:m:u:n:r:w:e:x: options
do
    case "${options}" in
        d) directed=${OPTARG};;
        s) emb_strategy=${OPTARG};;
        a) aggr_strategy=${OPTARG};;
        o) graph_version=${OPTARG};;
        l) add_self_loop=${OPTARG};; 
        b) batch_size=${OPTARG};;
        m) model_id=${OPTARG};;
        u) use_bases=${OPTARG};;
        n) num_bases=${OPTARG};;
        r) learning_rate=${OPTARG};;
        w) weight_decay=${OPTARG};;
        e) epochs=${OPTARG};;
        x) exp_id=${OPTARG};;
    esac
done


source /opt/share/anaconda3-2019.03/x86_64/etc/profile.d/conda.sh
conda conda_envs/pytorch

if [ $directed -eq 1 ]
then
    direction='directed'
else
    direction='undirected'
fi

if [ $emb_strategy = 'bow' ]
then
    input_path_graphs='../../transformation/mimic/data/processed_graphs/use_case_428_427/'${direction}'/'${emb_strategy}'/v'${graph_version}'/'
else
    input_path_graphs='../../transformation/mimic/data/processed_graphs/use_case_428_427/'${direction}'/'${emb_strategy}'/'${aggr_strategy}'/v'${graph_version}'/'
fi

for splits in {0..9}
do
    for cv_splits in {0..4}
    do
        input_path_data_files='use_case_428_427_data_splits/split_'${splits}'/cv_split_'${cv_splits}'.json'
        output_path='saved_models/use_case_428_427/exp_'${exp_id}'/'${direction}'/'${emb_strategy}'/v'${graph_version}'/'${model_id}'/split_'${splits}'/cv_split_'${cv_splits}'/'
        jbsub -mem 16g -q x86_24h -cores 1+1 python main.py --input_path_data_files $input_path_data_files --input_path_graphs $input_path_graphs --directed $directed --add_self_loop $add_self_loop --batch_size $batch_size --model_id $model_id --use_bases $use_bases --num_bases $num_bases --learning_rate $learning_rate --weight_decay $weight_decay --epochs $epochs --output_path $output_path
    done
done
