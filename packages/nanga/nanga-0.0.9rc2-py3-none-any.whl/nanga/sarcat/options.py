# @copyright  Copyright (c) 2018-2020 Opscidia

def train_opts(parser):
    group = parser.add_argument_group('Training')
    group.add_argument('--train', default='./sample_data/sample_train.tsv',
        help='path to a train data')
    group.add_argument('--category_dir', default='../data/',
        help='path to a train data')
    group.add_argument('--master_category_path', default='../data/mcat_dict.json',
        help='path to master categorty dict')
    group.add_argument('--batch_size', type=int, default=32, 
        help='batch size')
    group.add_argument('--lr', type=float, default=0.01, 
        help='learning rate')
    group.add_argument('--epochs', type=int, default=50, 
        help='epochs')
    group.add_argument('--mcat_ratio', type=float, default=0.1, 
        help='mcat ratio')
    group.add_argument('--gpu_id', type=int, default=0,
        help='gpu id')
    group.add_argument('--gpu', action='store_true',
        help='whether gpu is used')
    group.add_argument('--random_seed', type=int, default=42,
        help='path to a train data')
    group.add_argument('--pbar_width', type=int, default=None,
        help='The width of the progress bar.')
    group.add_argument('--use_wandb', type=bool, default=True,
        help='Whether to use the Weights & Biases online performance recording.')
    group.add_argument('--wandb_name', type=str, default='scita_classif',
        help='The name of the training run, used for wandb purposes')
    
    group.add_argument('--ema', type=float, default=0.99,
        help='The fact used in computing the exponential moving averages of the loss and sample-average F1 scores. Roughly corresponds to taking the average of the previous 1 / (1 - ema) many batches')
    
    return group


def model_opts(parser):
    group = parser.add_argument_group('Mosdel')
    
    group.add_argument('--hidden_size', type=int, default=256,
        help='hidden size')
    
    group.add_argument('--normalize', type=bool, default=True,
        help='normalize')
    group.add_argument('--nlayers', type=int, default=2,
        help='number of layer')
    group.add_argument('--dropout', type=float, default=0.5,
        help='dropout')
    group.add_argument('--boom_dim', type=int, default=512,
        help='dropout')
    group.add_argument('--min-freq', type=int, default=0,
        help='''map words of source side appearing less than 
                threshold times to unknown''')
    group.add_argument('--pretrained-embedding-name', type=str, default=None,
        help='pretrained embeddings')
    group.add_argument('--pretrained-embedding-path', type=str, default=None,
        help='pretrained embeddings')
