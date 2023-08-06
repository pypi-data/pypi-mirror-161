# @copyright  Copyright (c) 2018-2020 Opscidia

import sys
import torch
from torch import nn
from torch import optim
from torch.nn import functional as F



def load_model(path: str):
    checkpoint = torch.load(path, map_location = lambda storage, log: storage)
    print(checkpoint['params'])
    model = ClassifModel(checkpoint['params'])
    model.load_state_dict(checkpoint['state_dict'])
    return model, checkpoint['scores']


class BiRNN(nn.Module):
    ''' A block of bidirectional Gated Recurrent Units.
    INPUT
        in_dim: int
            The dimension of the input space
        out_dim: int
            *Half* of the dimension of the output space. The actual
            output dimension will be 2 * out_dim, as the GRUs are 
            bidirectional
        normalise: bool = True
            Whether to apply layer normalisation after the GRU layers
        nlayers: int = 1
            The number of GRU layers
        dropout: float = 0.
            The amount of dropout to apply after the GRU layers
    '''
    def __init__(self, input_size: int, hidden_size: int, normalize: bool = True,
        nlayers: int = 1, dropout: float = 0.):
        super().__init__()
        self.rnn = nn.GRU(input_size, hidden_size, bidirectional = True, num_layers = nlayers)
        self.norm = nn.LayerNorm(2 * hidden_size) if normalize else None
        self.drop = nn.Dropout(dropout) if dropout > 0 else None

    def forward(self, x, h = None):
        x, h = self.rnn(x, h)
        if self.norm is not None:
            x = self.norm(x)
        if self.drop is not None:
            x = self.drop(x)
        return x, h
    
    

    
    
class SelfAttentionBlock(nn.Module):
    ''' A block of self-attention. The attention used here is the scaled
    dot product attention, which allows inputs to be either two- or three-
    dimensional. Note that this layer has no trainable parameters.
    INPUT
        dim: int
            The dimension of the input- and output space
        normalise: bool = True
            Whether apply layer normalisation to the output
        dropout: float = 0.
            The amount of dropout to apply after the self-attention
    '''
    def __init__(self, dim: int, normalise: bool = True, dropout: float = 0.):
        super().__init__()
        self.sqrt_dim = nn.Parameter(torch.sqrt(torch.FloatTensor([dim])), 
            requires_grad = False)
        self.norm = nn.LayerNorm(dim) if normalise else None
        self.drop = nn.Dropout(dropout) if dropout > 0 else None

    def forward(self, inputs):
        if len(inputs.shape) == 2:
            # Special 2d case with shape (batch_size, dim)
            # Treat dim as the sequence length to make sense of the
            # matrix multiplications, and set dim = 1
            # (batch_size, seq_len) -> (batch_size, seq_len, dim)
            reshaped_inputs = inputs.unsqueeze(2)
        else:
            # (seq_len, batch_size, dim) -> (batch_size, seq_len, dim)
            reshaped_inputs = inputs.permute(1, 0, 2)

        # (batch_size, seq_len, dim) -> (batch_size, seq_len, seq_len)
        scores = torch.bmm(reshaped_inputs, reshaped_inputs.permute(0, 2, 1))
        scores /= self.sqrt_dim
        weights = F.softmax(scores, dim = -1)

        # (batch_size, seq_len, seq_len) x (batch_size, seq_len, dim)
        # -> (batch_size, seq_len, dim)
        mix = torch.bmm(weights, reshaped_inputs)

        if len(inputs.shape) == 2:
            # (batch_size, seq_len, dim) -> (batch_size, seq_len)
            out = mix.squeeze()
        else:
            # (batch_size, seq_len, dim) -> (seq_len, batch_size, dim)
            out = mix.permute(1, 0, 2)

        if self.norm is not None:
            out = self.norm(out)
        if self.drop is not None:
            out = self.drop(out)
        return out, weights
    
    
    
class Base(nn.Module):
    ''' A base model, with a frozen word embedding layer.
    INPUT
        data_dir: str = '.data'
            The name of the data directory
        pbar_width: str = None
            The width of the progress bar when training. If you are using
            a Jupyter notebook then you should set this to ~1000
        vocab: torchtext.vocab.Vocab
            The vocabulary of the training dataset, containing the word 
            vectors and the conversion dictionary from tokens to indices
    '''
    def __init__(self, TEXT, pbar_width, categories, pretrained=True):
        super().__init__()
        
        self.pbar_width = pbar_width
        self.ntargets = categories
        self.stoi = TEXT.vocab.stoi
        
        vocab_size = len(TEXT.vocab)
        embed_dim = TEXT.vocab.vectors.shape[1]
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        # Embedding layer
            
        if pretrained:
            emb_matrix = TEXT.vocab.vectors
            self.embedding.weight = nn.Parameter(emb_matrix, requires_grad = False)
          
            
            
    def is_cuda(self):
        ''' Check if the model is stored on the GPU. '''
        return next(self.parameters()).is_cuda
    
    def evaluate(self, *args, **kwargs):
        ''' Evaluate the performance of the model. See inference.evaluate
            for more details. '''
        from inference import evaluate
        return evaluate(self, *args, **kwargs)

    def predict(self, *args, **kwargs):
        ''' Perform predictions. See inference.predict for more details. '''
        from inference import predict
        return predict(self, *args, **kwargs)

    def fit(self, *args, **kwargs):
        ''' Train the model. See training.train_model for more details. '''
        from training import train_model
        return train_model(self, *args, **kwargs)
            

#         
    
class BoomBlock(nn.Module):
    ''' A block consisting of two dense layers, one embedding into a high
        dimensional space, and the other projecting back into the dimension
        we started with. A GeLU activation is applied after the first
        embedding, but no activation is applied after the projection.
        INPUT
            dim: int
                The dimension of the input and output
            boom_dim: int
                The dimension of the intermediate space
            boom_normalise: bool = True
                Whether to apply a layer normalisation after embedding into
                the larger space
            boom_dropout: float = 0.
                The amount of dropout to apply after embedding into the
                larger space
            normalise: bool = True
                Whether to apply a layer normalisation after the projection
            dropout: float = 0.
                The amount of dropout to apply after the projection
    '''
    def __init__(self, dim: int, boom_dim: int, boom_normalise: bool = True,
        boom_dropout: float = 0., normalise: bool = True, dropout: float = 0.):
        super().__init__()
        self.boom_up = nn.Linear(dim, boom_dim)
        self.boom_norm = nn.LayerNorm(boom_dim) if boom_normalise else None
        self.boom_drop = nn.Dropout(boom_dropout) if boom_dropout > 0 else None
        self.boom_down = nn.Linear(boom_dim, dim)
        self.norm = nn.LayerNorm(boom_dim) if normalise else None
        self.drop = nn.Dropout(dropout) if dropout > 0 else None

    def forward(self, inputs):
        x = F.gelu(self.boom_up(inputs))
        if self.boom_norm is not None:
            x = self.boom_norm(x)
        if self.boom_drop is not None:
            x = self.boom_drop(x)

        x = inputs + self.boom_down(x)
        if self.norm is not None:
            x = self.norm(x)
        if self.drop is not None:
            x = self.drop(x)
        return x
    
class FCBlock(nn.Module):
    ''' A block of fully connected layers.
    INPUT
        in_dim: int
            The dimension of the input space
        out_dim: int
            The dimension of the output space
        normalise: bool = True
            Whether to apply layer normalisation after the fully connected 
            layers has been applied
        nlayers: int = 1
            The number of fully connected layers
        dropout: float = 0.
            The amount of dropout to apply after the fully connected layers
    '''
    def __init__(self, in_dim: int, out_dim: int, normalise: bool = True,
        nlayers: int = 1, dropout: float = 0.):
        super().__init__()
        self.fcs = nn.ModuleList(
            [nn.Linear(in_dim, out_dim)] + \
            [nn.Linear(out_dim, out_dim) for _ in range(nlayers - 1)]
        )
        self.norm = nn.LayerNorm(out_dim) if normalise else None
        self.drop = nn.Dropout(dropout) if dropout > 0 else None
    
    def forward(self, x):
        for idx, fc in enumerate(self.fcs):
            x = F.gelu(fc(x)) + x if idx > 0 else F.gelu(fc(x))
        if self.norm is not None:
            x = self.norm(x)
        if self.drop is not None:
            x = self.drop(x)
        return x
    
class ClassifModel(Base):
    
    def __init__(self, field=None, pbar_width=0.1, categories=128, hidden_size=256, normalize=True, nlayers=2, dropout=0.5, boom_dim=512, boom_dropout=0.5, device='cuda'):
        super().__init__(field, pbar_width, categories)
        
        
        input_size = field.vocab.vectors.shape[1]
        
#         self.embendsBlock = Base(field, pbar_width, categories, input_size)
        
        
        
        self.rnn = BiRNN(input_size, hidden_size, normalize, nlayers, dropout)
        self.drop = nn.Dropout(p=0.5)
        
        self.seq_attn = SelfAttentionBlock(2 * hidden_size, 
            dropout)
        self.proj = FCBlock(2 * hidden_size, self.ntargets)
        self.cat_attn = SelfAttentionBlock(self.ntargets,
            dropout = dropout)
        self.boom = BoomBlock(self.ntargets, boom_dim,
            boom_dropout, normalise = False)
        self.device = device
        
        
    def forward(self, sample):
        
        x = self.drop(self.embedding(sample))
        
#         title_emb = self.embedding(title)
#         abstract_emd = self.embedding(abstract)
        
#         cats = torch.cat([title_embed, abstract_emd], dim=2)
        
#         x = self.embed(x)
        x, _ = self.rnn(x)
        x, _ = self.seq_attn(x)
        x = torch.sum(x, dim = 0)
        x = self.proj(x)
        x, _ = self.cat_attn(x)
        return self.boom(x)
    
    
class MODELLSTM(nn.Module):

    def __init__(self, vocab_size, TEXT, hidden_size, embed_dim, nlayers, bidirectional, device):
        super(LSTM, self).__init__()
        
        if not pretrained:
            self.embedding = nn.Embedding(vocab_size, embed_dim)
        else:
            self.embedding = nn.Embedding(vocab_size, embed_dim).from_pretrained(TEXT.vocab.vectors)
        
        self.embedding = nn.Embedding(len(text_field.vocab), 300)
        self.dimension = dimension
        self.lstm = nn.LSTM(input_size=300,
                            hidden_size=dimension,
                            num_layers=1,
                            batch_first=True,
                            bidirectional=True)
        self.drop = nn.Dropout(p=0.5)

        self.fc = nn.Linear(2*dimension, 1)

    def forward(self, text, text_len):

        text_emb = self.embedding(text)

        packed_input = pack_padded_sequence(text_emb, text_len, batch_first=True, enforce_sorted=False)
        packed_output, _ = self.lstm(packed_input)
        output, _ = pad_packed_sequence(packed_output, batch_first=True)

        out_forward = output[range(len(output)), text_len - 1, :self.dimension]
        out_reverse = output[:, 0, self.dimension:]
        out_reduced = torch.cat((out_forward, out_reverse), 1)
        text_fea = self.drop(out_reduced)

        text_fea = self.fc(text_fea)
        text_fea = torch.squeeze(text_fea, 1)
        text_out = torch.sigmoid(text_fea)

        return text_out
