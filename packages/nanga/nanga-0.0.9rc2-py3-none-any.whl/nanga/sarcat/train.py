# @copyright  Copyright (c) 2018-2020 Opscidia

import argparse, sys, os, random, torch
from torch import optim
from torch.nn import functional as F
from tqdm.auto import tqdm
import warnings
from torchtext import data, vocab
from torchtext.data import Field, TabularDataset, BucketIterator
from sklearn.metrics import f1_score
from options import train_opts, model_opts
from data.utils import get_cats, BatchWrapper, get_mcat_dict, get_class_weights, get_mcat_masks, cats2mcats
from losses import NestedBCELoss
from models.rnn_models import ClassifModel





def main(args):
    
    device = torch.device('cuda' if args.gpu  else 'cpu')
    
    # Define the two types of fields in the tsv file
    TXT = Field()
    CAT = Field(sequential = False, use_vocab = False, is_target = True)

    # Set up the columns in the tsv file with their associated fields
    cats = get_cats(args.category_dir)
    mcats_dict = get_mcat_dict(args.category_dir)
    if cats is None:
        sys.exit(f"{args.category} does not eexist.")
    cats = cats['id']
    fields = [('text', TXT)] + [(cat, CAT) for cat in cats]
    
    
    # Load in the dataset and tokenise the texts
    dataset = TabularDataset(
        path = args.train,
        format = 'tsv',
        fields = fields,
        skip_header = True
    )

    # Split into a training- and validation set
    train, val = dataset.split(split_ratio = 0.90)
    
    
        
    if args.pretrained_embedding_name is not None and args.pretrained_embedding_path is not None:
        #pretrained = load_pretrained_embedding_from_file(args.pretrained_embedding, fields[0][1], 300)
        vectors = vocab.Vectors(name=args.pretrained_embedding_name, cache=args.pretrained_embedding_path) # model_name + path = path_to_embeddings_file
        TXT.build_vocab(train, min_freq=args.min_freq, vectors=vectors)
        pretrained = True

        #pretrained = load_fasttext_embeddings(args.pretrained_embedding)
    else:
        vectors = None
        TXT.build_vocab(train, min_freq=args.min_freq)
        pretrained = False
        
        
    print(TXT.vocab.itos.index('-TITLE_START-'), TXT.vocab.itos.index('-TITLE_END-'), TXT.vocab.itos.index('-ABSTRACT_START-'), TXT.vocab.itos.index('-ABSTRACT_END-'))
   

    # Numericalise the texts, batch them into batches of similar text
    # lengths and pad the texts in each batch
    train_iter, val_iter = BucketIterator.splits(
        datasets = (train, val),
        batch_size = args.batch_size,
        sort_key = lambda sample: len(sample.text),
        device=device
    )

    train_dl = BatchWrapper(train_iter, vectors = vectors, cats = cats)
    val_dl = BatchWrapper(val_iter, vectors = vectors, cats = cats)

    del dataset, train, val, train_iter, val_iter
    
    model = ClassifModel(field=TXT, pbar_width=args.pbar_width, categories=len(cats), hidden_size=args.hidden_size, normalize=args.normalize, nlayers=args.nlayers, dropout=0.5, boom_dim=512, boom_dropout=0.5, device=device).to(device)
    
    # Sign into wandb and log metrics from model
    if args.use_wandb:
        import wandb
        config = {
            'name': args.wandb_name,
            'mcat_ratio': args.mcat_ratio, 
            'epochs': args.epochs, 
            'lr': args.lr,
            'batch_size': train_dl.batch_size,
            'ema': args.ema,
            'vectors': train_dl.vectors,
            'dropout': args.dropout,
            'nlayers':args.nlayers,
            'dim': args.hidden_size,
            'boom_dim': args.boom_dim,
            'emb_dim': TXT.vocab.vectors.shape[1],
        }
        wandb.init(project = 'scita', config = config)
        wandb.watch(model)
        
    
    
    if not os.path.isdir('./results'):
        os.mkdir('./results')
    weights = get_class_weights(train_dl, pbar_width = model.pbar_width, 
        cats = cats, mcats_dict = mcats_dict, device=device)

    criterion = NestedBCELoss(**weights, mcat_ratio = 0.1,
        cats = cats, mcats_dict = mcats_dict, device=device)
    optimizer = optim.Adam(model.parameters(), lr = args.lr)
    mcat_masks = get_mcat_masks(cats, mcats_dict, device)

    if model.is_cuda():
        mcat_masks = mcat_masks.to(device)
        criterion = criterion.to(device)

    avg_loss, avg_cat_f1, avg_mcat_f1, best_score = 0, 0, 0, 0
    overwrite_model = False
    
    for epoch in range(args.epochs):
        
        with tqdm(total = len(train_dl) * train_dl.batch_size, 
            ncols = args.pbar_width) as pbar:
            model.train()
            
            for idx, (x_train, y_train) in enumerate(train_dl):
                optimizer.zero_grad()

                if model.is_cuda():
                    x_train = x_train.to(device)
                    y_train = y_train.to(device)

                # Get cat predictions
                y_hat = model(x_train)
                preds = torch.sigmoid(y_hat)

                # Get master cat predictions
                my_hat, my_train = cats2mcats(y_hat, y_train, 
                    masks = mcat_masks, cats = cats, mcats_dict = mcats_dict, device=device)
                mpreds = torch.sigmoid(my_hat)

                # Calculate loss and perform backprop
                loss = criterion(y_hat, y_train)
                loss.backward()
                optimizer.step()
                
                # Compute f1 scores
                with warnings.catch_warnings():
                    warnings.simplefilter('ignore')
                    cat_f1 = f1_score(preds.cpu() > 0.5, y_train.cpu(), 
                        average = 'samples')
                    mcat_f1 = f1_score(mpreds.cpu() > 0.5, my_train.cpu(),
                        average = 'samples')

                # Keep track of the current iteration index
                iteration = epoch * len(train_dl) * train_dl.batch_size
                iteration += idx * train_dl.batch_size

                # Exponentially moving average of loss and f1 scores
                avg_loss = args.ema * avg_loss + (1 - args.ema) * float(loss.item())
                avg_loss /= 1 - args.ema ** (iteration / (1 - args.ema) + 1)
                avg_cat_f1 = args.ema * avg_cat_f1 + (1 - args.ema) * float(cat_f1)
                avg_cat_f1 /= 1 - args.ema ** (iteration / (1 - args.ema) + 1)
                avg_mcat_f1 = args.ema * avg_mcat_f1 + (1 - args.ema) * float(mcat_f1)
                avg_mcat_f1 /= 1 - args.ema ** (iteration / (1 - args.ema) + 1)

                # Log wandb
                if args.use_wandb:
                    wandb.log({
                        'loss': avg_loss, 
                        'cat f1': avg_cat_f1,
                        'mcat f1': avg_mcat_f1
                    })

                # Update the progress bar
                desc = f'Epoch {epoch:2d} - '\
                       f'loss {avg_loss:.4f} - '\
                       f'cat f1 {avg_cat_f1:.4f} - '\
                       f'mcat f1 {avg_mcat_f1:.4f}'
                pbar.set_description(desc)
                pbar.update(train_dl.batch_size)

            # Compute validation scores
            with torch.no_grad():
                model.eval()

                val_loss, val_cat_f1, val_mcat_f1 = 0, 0, 0
                y_vals, y_hats = [], []
                for x_val, y_val in val_dl:

                    if model.is_cuda():
                        x_val = x_val.to(device)
                        y_val = y_val.to(device)

                    # Get cat predictions
                    y_hat = model(x_val)
                    preds = torch.sigmoid(y_hat)

                    # Get mcat predictions
                    my_hat, my_val = cats2mcats(y_hat, y_val, 
                        masks = mcat_masks, cats = cats, mcats_dict = mcats_dict, device=device)
                    mpreds = torch.sigmoid(my_hat)

                    # Collect the true and predicted labels
                    y_vals.append(y_val)
                    y_hats.append(preds > 0.5)

                    # Accumulate loss
                    _loss = criterion(y_hat,y_val, weighted = False)
                    val_loss += float(_loss.item())

                    # Accumulate f1 scores
                    with warnings.catch_warnings():
                        warnings.simplefilter('ignore')
                        val_cat_f1 += f1_score(preds.cpu() > 0.5, y_val.cpu(), 
                            average = 'samples')
                        val_mcat_f1 += f1_score(mpreds.cpu() > 0.5, 
                            my_val.cpu(), average = 'samples')

                # Concatenate the true and predicted labels
                y_val = torch.cat(y_vals, dim = 0)
                y_hat = torch.cat(y_hats, dim = 0)

                # Compute the average loss and f1 scores
                val_loss /= len(val_dl)
                val_cat_f1 /= len(val_dl)
                val_mcat_f1 /= len(val_dl)

                # Log wandb
                if args.use_wandb:
                    wandb.log({
                        'val loss': val_loss, 
                        'val cat f1': val_cat_f1,
                        'val mcat f1': val_mcat_f1
                    })

                # If the current cat f1 score is the best so far, then
                # replace the stored model with the current one
                if val_cat_f1 > best_score:
                    model_fname = f'./results/model_{val_cat_f1 * 100:.2f}.pt' 
                    best_score = val_cat_f1
                    data = {
                        'params': args,
                        'state_dict': model.state_dict(),
                        'scores': model.evaluate(val_dl, output_dict = True, cats = cats)
                    }

                    if overwrite_model:
                        for f in get_path(model.data_dir).glob(f'model*.pt'):
                            f.unlink()

                    with warnings.catch_warnings():
                        warnings.simplefilter('ignore')
    #                         path = get_path(model.data_dir) / model_fname
                        torch.save(data, model_fname)

                    # Save the model's state dict to wandb directory
                    if args.use_wandb:
                        if overwrite_model:
                            for f in Path(wandb.run.dir).glob(f'model*.pt'):
                                f.unlink()
                        torch.save(data, model_fname)
                        wandb.save(model_fname)

                # Update progress bar
                desc = f'Epoch {epoch:2d} - '\
                       f'loss {avg_loss:.4f} - '\
                       f'cat f1 {avg_cat_f1:.4f} - '\
                       f'mcat f1 {avg_mcat_f1:.4f} - '\
                       f'val_loss {val_loss:.4f} - '\
                       f'val cat f1 {val_cat_f1:.4f} - '\
                       f'val mcat f1 {val_mcat_f1:.4f}'
                pbar.set_description(desc)

        





if __name__ == "__main__":
    parser = argparse.ArgumentParser('')
    
    train_opts(parser)
    model_opts(parser)
    args = parser.parse_args()
    
    os.environ['CUDA_VISIBLE_DEVICES'] = str(args.gpu_id)
    main(args)
