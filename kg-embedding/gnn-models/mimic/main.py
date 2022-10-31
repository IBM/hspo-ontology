import argparse
import torch
from tqdm import tqdm 
import os
import sys  
import logging 
from torch_geometric.loader import DataLoader
from torch_geometric.nn import to_hetero, to_hetero_with_bases
from sklearn.metrics import precision_recall_fscore_support, accuracy_score
from datasets import MyDataset
from models import Net1_1, Net1_2, Net2_1, Net2_2
from helper import read_json, save_results


def train():
    model.train()
    steps, total_training_loss = 0, 0
    predictions, ground_truth = [], []
    for batch in tqdm(train_dataloader):
        batch = batch.to(device)
        steps += 1
        optimizer.zero_grad()
        x_dict_ = batch.x_dict
        edge_index_dict_ = batch.edge_index_dict
        out = model(x_dict_, edge_index_dict_)
        loss = loss_function(out['patient'], torch.unsqueeze(batch['patient']['y'], 1))
        loss.backward()
        optimizer.step()
        total_training_loss += loss
        pred = torch.squeeze((torch.sigmoid(out['patient']) > 0.5).long(), 1)
        predictions.extend(pred.tolist())
        ground_truth.extend(batch['patient']['y'].long().tolist())
    
    logger.info("------ Training Set Results ------")
    logger.info("Epoch: {}, loss: {:.4f}" .format(epoch, total_training_loss / steps))
    
    precision, recall, f1_score, _ = precision_recall_fscore_support(y_true=ground_truth, y_pred=predictions, average = 'binary', zero_division=0)
    train_info = {'loss': total_training_loss / steps,
                  'accuracy': accuracy_score(y_true=ground_truth, y_pred=predictions),
                  'precision': precision,
                  'recall': recall,
                  'f1_score': f1_score}
    return train_info, ground_truth, predictions


def evaluation(eval_loader, test_or_val):
    steps, total_eval_loss = 0, 0
    predictions, ground_truth = [], []
    with torch.no_grad():
        model.eval()
        logger.info("------ Testing ------")
        for batch in tqdm(eval_loader):
            batch = batch.to(device)
            steps += 1
            x_dict_ = batch.x_dict
            edge_index_dict_ = batch.edge_index_dict
            out = model(x_dict_, edge_index_dict_)
            loss = loss_function(out['patient'], torch.unsqueeze(batch['patient']['y'], 1))
            total_eval_loss += loss
            pred = torch.squeeze((torch.sigmoid(out['patient']) > 0.5).long(), 1)
            predictions.extend(pred.tolist())
            ground_truth.extend(batch['patient']['y'].long().tolist())
    
    precision, recall, f1_score, _ = precision_recall_fscore_support(y_true=ground_truth, y_pred=predictions, average = 'binary', zero_division=0)
    eval_info = {'loss': total_eval_loss/steps,
                 'accuracy': accuracy_score(y_true=ground_truth, y_pred=predictions),
                 'precision': precision,
                 'recall': recall,
                 'f1_score': f1_score}
    
    logger.info("-------- {} Results --------" .format(test_or_val))
    logger.info("loss: {:.4f}" .format(eval_info['loss'].item()))
    logger.info("accuracy: {:.4f}" .format(eval_info['accuracy']))
    logger.info("precision: {:.4f}" .format(eval_info['precision']))
    logger.info("recall: {:.4f}" .format(eval_info['recall']))
    logger.info("f1_score: {:.4f}" .format(eval_info['f1_score']))

    return eval_info, ground_truth, predictions



if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
                        datefmt='%m/%d/%Y %H:%M:%S',
                        level=logging.INFO)
    
    logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser()

    parser.add_argument("--input_path_data_files", default=None, type=str, required=True,
                        help = "The input path of the data files")
    parser.add_argument("--input_path_graphs", default=None, type=str, required=True,
                        help = "The input path of the processed graphs")
    parser.add_argument("--directed", default=None, type=int, required=True,
                        help = "Int value to define if the graph is going to be directed (1) or no (0).")
    parser.add_argument("--add_self_loop", default=None, type=int, required=True,
                        help = "Int value to define if self loops are going to be added in the graph (1) or no (0).")
    parser.add_argument("--batch_size", default=None, type=int, required=True,
                        help = "The size of the batch")
    parser.add_argument("--model_id", default=None, type=str, required=True,
                        help = "The model id")
    parser.add_argument("--use_bases", default=None, type=int, required=True,
                        help = "Define if basis-decomposition regularization is applied (1) or no (0).")
    parser.add_argument("--num_bases", default=None, type=int, required=False,
                        help = "The number of bases for the basis-decomposition technique. https://arxiv.org/pdf/1703.06103.pdf")
    parser.add_argument("--learning_rate", default=None, type=float, required=True,
                        help = "The learning rate for the optimizer.")
    parser.add_argument("--weight_decay", default=None, type=float, required=True,
                        help = "The weight decay for the optimizer.")
    parser.add_argument("--epochs", default=None, type=int, required=True,
                        help = "The number of training epochs.")
    parser.add_argument("--output_path", default=None, type=str, required=True,
                        help = "The output path for saving the model.")
    

    args = parser.parse_args()

    if not os.path.exists(args.output_path):
        os.makedirs(args.output_path) 

    logger.addHandler(logging.FileHandler(args.output_path + 'log_info.log', 'w'))
    logger.info(sys.argv)
    logger.info(args)

    saved_file = save_results(args.output_path + 'training_info.txt',
                              header='# epoch \t train_loss \t val_loss \t test_lost \t train_acc \t train_f1 \t val_acc \t val_f1 \t test_acc \t test_f1')
    model_file = "best_model.pt"

    # Define the device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    data_files = read_json(args.input_path_data_files)
    # Split the data files in train, val, and test set.
    train_filenames = data_files['train_set'][round(0.15*len(data_files['train_set'])):]
    val_filenames = data_files['train_set'][:round(0.15*len(data_files['train_set']))]
    test_filenames = data_files['test_set']

    # Define the dataset and the dataloaders
    train_dataset = MyDataset(input_path=args.input_path_graphs,
                               filenames=train_filenames, directed=args.directed, add_self_loops=args.add_self_loop)
    val_dataset = MyDataset(input_path=args.input_path_graphs,
                             filenames=val_filenames, directed=args.directed, add_self_loops=args.add_self_loop)
    test_dataset = MyDataset(input_path=args.input_path_graphs,
                              filenames=test_filenames, directed=args.directed, add_self_loops=args.add_self_loop)


    train_dataloader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True)
    val_dataloader = DataLoader(val_dataset, batch_size=args.batch_size, shuffle=False)
    test_dataloader = DataLoader(test_dataset, batch_size=args.batch_size, shuffle=False)
    
    # Define the model
    if args.model_id == '1_1':
        model = Net1_1([256, 32])
    elif args.model_id == '1_2':     
        model = Net1_2([256, 32])
    elif args.model_id == '2_1':     
        model = Net2_1([256, 32])
    elif args.model_id == '2_2':     
        model = Net2_2([256, 32])
    else:
        print('Wrong model id was given.')
    
    if args.use_bases:
        model = to_hetero_with_bases(model, train_dataset.metadata, num_bases=args.num_bases)
    else:
        model = to_hetero(model, train_dataset.metadata, aggr='sum')
    model.to(device)

    optimizer = torch.optim.Adam(model.parameters(), lr=args.learning_rate, weight_decay=args.weight_decay)
    loss_function = torch.nn.BCEWithLogitsLoss()

    best_result = 0
    test_best_acc = None 
    test_best_prec = None
    test_best_rec = None
    test_best_f1 = None
    # Training + Evaluation
    train_info = {'epoch': [],
                  'loss': [],
                  'accuracy': [],
                  'precision': [],
                  'recall': [],
                  'f1_score': []}
    val_info = {'epoch': [],
                'loss': [],
                'accuracy': [],
                'precision': [],
                'recall': [],
                'f1_score': []}
    test_info = {'epoch': [],
                'loss': [],
                'accuracy': [],
                'precision': [],
                'recall': [],
                'f1_score': []}

    for epoch in range(args.epochs):
        logger.info('---------Training---------')
        # Train step
        train_info_epoch, _, _ = train()
        train_info['epoch'].append(epoch + 1)
        train_info['loss'].append(train_info_epoch['loss'].item())
        train_info['accuracy'].append(train_info_epoch['accuracy'])
        train_info['precision'].append(train_info_epoch['precision'])
        train_info['recall'].append(train_info_epoch['recall'])
        train_info['f1_score'].append(train_info_epoch['f1_score'])
        # Validation step
        eval_info, _, _ = evaluation(val_dataloader, 'val')
        val_info['epoch'].append(epoch + 1)
        val_info['loss'].append(eval_info['loss'].item())
        val_info['accuracy'].append(eval_info['accuracy'])
        val_info['precision'].append(eval_info['precision'])
        val_info['recall'].append(eval_info['recall'])
        val_info['f1_score'].append(eval_info['f1_score'])
        # Test step
        eval_info, _, _ = evaluation(test_dataloader, 'test')
        test_info['epoch'].append(epoch + 1)
        test_info['loss'].append(eval_info['loss'].item())
        test_info['accuracy'].append(eval_info['accuracy'])
        test_info['precision'].append(eval_info['precision'])
        test_info['recall'].append(eval_info['recall'])
        test_info['f1_score'].append(eval_info['f1_score'])

        # Save the best model based on the performance in validation set.
        if epoch == 0 or val_info['f1_score'][-1] > best_result:
            best_result = val_info['f1_score'][-1]
            test_best_acc = test_info['accuracy'][-1]
            test_best_prec = test_info['precision'][-1]
            test_best_rec = test_info['recall'][-1]
            test_best_f1 = test_info['f1_score'][-1]
            torch.save(model.state_dict(), args.output_path + model_file)
            logger.info("Best results on val set saved!")
        
        saved_file.save("{} \t {:.4f} \t {:.4f} \t {:.4f} \t {:.4f} \t {:.4f} \t {:.4f} \t {:.4f} \t {:.4f} \t {:.4f}" .format(epoch,
                                                                                                                               train_info['loss'][-1],
                                                                                                                               val_info['loss'][-1],
                                                                                                                               test_info['loss'][-1],
                                                                                                                               train_info['accuracy'][-1],
                                                                                                                               train_info['f1_score'][-1],
                                                                                                                               val_info['accuracy'][-1],
                                                                                                                               val_info['f1_score'][-1],
                                                                                                                               test_info['accuracy'][-1],
                                                                                                                               test_info['f1_score'][-1]))
    
    saved_file.save("best test result: acc: {:.4f} \t prec: {:.4f} \t rec: {:.4f} \t f1: {:.4f}" .format(test_best_acc,
                                                                                                         test_best_prec,
                                                                                                         test_best_rec,
                                                                                                         test_best_f1))

