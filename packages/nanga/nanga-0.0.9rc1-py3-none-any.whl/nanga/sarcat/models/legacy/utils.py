# @copyright  Copyright (c) 2018-2020 Opscidia

from pathlib import Path
import torch


cats_ = {"id": ["astro-ph.CO", "astro-ph.EP", "astro-ph.GA", "astro-ph.HE", "astro-ph.IM", "astro-ph.SR", "cond-mat.dis-nn", "cond-mat.mes-hall", "cond-mat.mtrl-sci", "cond-mat.other", "cond-mat.quant-gas", "cond-mat.soft", "cond-mat.stat-mech", "cond-mat.str-el", "cond-mat.supr-con", "cs.AI", "cs.AR", "cs.CC", "cs.CE", "cs.CG", "cs.CL", "cs.CR", "cs.CV", "cs.CY", "cs.DB", "cs.DC", "cs.DL", "cs.DM", "cs.DS", "cs.ET", "cs.FL", "cs.GL", "cs.GR", "cs.GT", "cs.HC", "cs.IR", "cs.IT", "cs.LG", "cs.LO", "cs.MA", "cs.MM", "cs.MS", "cs.NA", "cs.NE", "cs.NI", "cs.OH", "cs.OS", "cs.PF", "cs.PL", "cs.RO", "cs.SC", "cs.SD", "cs.SE", "cs.SI", "cs.SY", "gr-qc", "hep-ex", "hep-lat", "hep-ph", "hep-th", "math-ph", "math.AC", "math.AG", "math.AP", "math.AT", "math.CA", "math.CO", "math.CT", "math.CV", "math.DG", "math.DS", "math.FA", "math.GM", "math.GN", "math.GR", "math.GT", "math.HO", "math.IT", "math.KT", "math.LO", "math.MG", "math.MP", "math.NA", "math.NT", "math.OA", "math.OC", "math.PR", "math.QA", "math.RA", "math.RT", "math.SG", "math.SP", "math.ST", "nlin.AO", "nlin.CD", "nlin.CG", "nlin.PS", "nlin.SI", "nucl-ex", "nucl-th", "physics.acc-ph", "physics.ao-ph", "physics.app-ph", "physics.atm-clus", "physics.atom-ph", "physics.bio-ph", "physics.chem-ph", "physics.class-ph", "physics.comp-ph", "physics.data-an", "physics.ed-ph", "physics.flu-dyn", "physics.gen-ph", "physics.geo-ph", "physics.hist-ph", "physics.ins-det", "physics.med-ph", "physics.optics", "physics.plasm-ph", "physics.pop-ph", "physics.soc-ph", "physics.space-ph", "q-bio.BM", "q-bio.CB", "q-bio.GN", "q-bio.MN", "q-bio.NC", "q-bio.OT", "q-bio.PE", "q-bio.QM", "q-bio.SC", "q-bio.TO", "q-fin.CP", "q-fin.EC", "q-fin.GN", "q-fin.MF", "q-fin.PM", "q-fin.PR", "q-fin.RM", "q-fin.ST", "q-fin.TR", "quant-ph", "stat.AP", "stat.CO", "stat.ME", "stat.ML", "stat.OT", "stat.TH"], "name": ["Cosmology and Nongalactic Astrophysics", "Earth and Planetary Astrophysics", "Astrophysics of Galaxies", "High Energy Astrophysical Phenomena", "Instrumentation and Methods for Astrophysics", "Solar and Stellar Astrophysics", "Disordered Systems and Neural Networks", "Mesoscale and Nanoscale Physics", "Materials Science", "Other Condensed Matter", "Quantum Gases", "Soft Condensed Matter", "Statistical Mechanics", "Strongly Correlated Electrons", "Superconductivity", "Artificial Intelligence", "Hardware Architecture", "Computational Complexity", "Computational Engineering, Finance, and Science", "Computational Geometry", "Computation and Language", "Cryptography and Security", "Computer Vision and Pattern Recognition", "Computers and Society", "Databases", "Distributed, Parallel, and Cluster Computing", "Digital Libraries", "Discrete Mathematics", "Data Structures and Algorithms", "Emerging Technologies", "Formal Languages and Automata Theory", "General Literature", "Graphics", "Computer Science and Game Theory", "Human-Computer Interaction", "Information Retrieval", "Information Theory", "Learning", "Logic in Computer Science", "Multiagent Systems", "Multimedia", "Mathematical Software", "Numerical Analysis", "Neural and Evolutionary Computing", "Networking and Internet Architecture", "Other Computer Science", "Operating Systems", "Performance", "Programming Languages", "Robotics", "Symbolic Computation", "Sound", "Software Engineering", "Social and Information Networks", "Systems and Control", "General Relativity and Quantum Cosmology", "High Energy Physics - Experiment", "High Energy Physics - Lattice", "High Energy Physics - Phenomenology", "High Energy Physics - Theory", "Mathematical Physics", "Commutative Algebra", "Algebraic Geometry", "Analysis of PDEs", "Algebraic Topology", "Classical Analysis and ODEs", "Combinatorics", "Category Theory", "Complex Variables", "Differential Geometry", "Dynamical Systems", "Functional Analysis", "General Mathematics", "General Topology", "Group Theory", "Geometric Topology", "History and Overview", "Information Theory", "K-Theory and Homology", "Logic", "Metric Geometry", "Mathematical Physics", "Numerical Analysis", "Number Theory", "Operator Algebras", "Optimization and Control", "Probability", "Quantum Algebra", "Rings and Algebras", "Representation Theory", "Symplectic Geometry", "Spectral Theory", "Statistics Theory", "Adaptation and Self-Organizing Systems", "Chaotic Dynamics", "Cellular Automata and Lattice Gases", "Pattern Formation and Solitons", "Exactly Solvable and Integrable Systems", "Nuclear Experiment", "Nuclear Theory", "Accelerator Physics", "Atmospheric and Oceanic Physics", "Applied Physics", "Atomic and Molecular Clusters", "Atomic Physics", "Biological Physics", "Chemical Physics", "Classical Physics", "Computational Physics", "Data Analysis, Statistics and Probability", "Physics Education", "Fluid Dynamics", "General Physics", "Geophysics", "History and Philosophy of Physics", "Instrumentation and Detectors", "Medical Physics", "Optics", "Plasma Physics", "Popular Physics", "Physics and Society", "Space Physics", "Biomolecules", "Cell Behavior", "Genomics", "Molecular Networks", "Neurons and Cognition", "Other", "Populations and Evolution", "Quantitative Methods", "Subcellular Processes", "Tissues and Organs", "Computational Finance", "Economics", "General Finance", "Mathematical Finance", "Portfolio Management", "Pricing of Securities", "Risk Management", "Statistical Finance", "Trading and Microstructure", "Quantum Physics", "Applications", "Computation", "Methodology", "Machine Learning", "Other Statistics", "Theory"]}



mcats_ = {"astro-ph.GA": "physics", "astro-ph.CO": "physics", "astro-ph.EP": "physics", "astro-ph.HE": "physics", "astro-ph.IM": "physics", "astro-ph.SR": "physics", "cond-mat.dis-nn": "physics", "cond-mat.mtrl-sci": "physics", "cond-mat.mes-hall": "physics", "cond-mat.other": "physics", "cond-mat.quant-gas": "physics", "cond-mat.soft": "physics", "cond-mat.stat-mech": "physics", "cond-mat.str-el": "physics", "cond-mat.supr-con": "physics", "gr-qc": "physics", "hep-ex": "physics", "hep-lat": "physics", "hep-ph": "physics", "hep-th": "physics", "math-ph": "physics", "nlin.AO": "physics", "nlin.CG": "physics", "nlin.CD": "physics", "nlin.SI": "physics", "nlin.PS": "physics", "nucl-ex": "physics", "nucl-th": "physics", "physics.acc-ph": "physics", "physics.app-ph": "physics", "physics.ao-ph": "physics", "physics.atom-ph": "physics", "physics.atm-clus": "physics", "physics.bio-ph": "physics", "physics.chem-ph": "physics", "physics.class-ph": "physics", "physics.comp-ph": "physics", "physics.data-an": "physics", "physics.flu-dyn": "physics", "physics.gen-ph": "physics", "physics.geo-ph": "physics", "physics.hist-ph": "physics", "physics.ins-det": "physics", "physics.med-ph": "physics", "physics.optics": "physics", "physics.ed-ph": "physics", "physics.soc-ph": "physics", "physics.plasm-ph": "physics", "physics.pop-ph": "physics", "physics.space-ph": "physics", "quant-ph": "physics", "math.AG": "math", "math.AT": "math", "math.AP": "math", "math.CT": "math", "math.CA": "math", "math.CO": "math", "math.AC": "math", "math.CV": "math", "math.DG": "math", "math.DS": "math", "math.FA": "math", "math.GM": "math", "math.GN": "math", "math.GT": "math", "math.GR": "math", "math.HO": "math", "math.IT": "math", "math.KT": "math", "math.LO": "math", "math.MP": "math", "math.MG": "math", "math.NT": "math", "math.NA": "math", "math.OA": "math", "math.OC": "math", "math.PR": "math", "math.QA": "math", "math.RT": "math", "math.RA": "math", "math.SP": "math", "math.ST": "math", "math.SG": "math", "cs.AI": "cs", "cs.CL": "cs", "cs.CC": "cs", "cs.CE": "cs", "cs.CG": "cs", "cs.GT": "cs", "cs.CV": "cs", "cs.CY": "cs", "cs.CR": "cs", "cs.DS": "cs", "cs.DB": "cs", "cs.DL": "cs", "cs.DM": "cs", "cs.DC": "cs", "cs.ET": "cs", "cs.FL": "cs", "cs.GL": "cs", "cs.GR": "cs", "cs.AR": "cs", "cs.HC": "cs", "cs.IR": "cs", "cs.IT": "cs", "cs.LG": "cs", "cs.LO": "cs", "cs.MS": "cs", "cs.MA": "cs", "cs.MM": "cs", "cs.NI": "cs", "cs.NE": "cs", "cs.NA": "cs", "cs.OS": "cs", "cs.OH": "cs", "cs.PF": "cs", "cs.PL": "cs", "cs.RO": "cs", "cs.SI": "cs", "cs.SE": "cs", "cs.SD": "cs", "cs.SC": "cs", "cs.SY": "cs", "q-bio.BM": "q-bio", "q-bio.GN": "q-bio", "q-bio.MN": "q-bio", "q-bio.SC": "q-bio", "q-bio.CB": "q-bio", "q-bio.NC": "q-bio", "q-bio.TO": "q-bio", "q-bio.PE": "q-bio", "q-bio.QM": "q-bio", "q-bio.OT": "q-bio", "q-fin.PR": "q-fin", "q-fin.RM": "q-fin", "q-fin.PM": "q-fin", "q-fin.TR": "q-fin", "q-fin.MF": "q-fin", "q-fin.CP": "q-fin", "q-fin.ST": "q-fin", "q-fin.GN": "q-fin", "q-fin.EC": "q-fin", "stat.AP": "stats", "stat.CO": "stats", "stat.ML": "stats", "stat.ME": "stats", "stat.OT": "stats", "stat.TH": "stats"}

def get_root_path() -> Path:
    ''' Returns project root folder. '''
    current_dir = Path.cwd()
    if str(current_dir)[-3:] == 'src':
        return current_dir.parent
    else:
        return current_dir

def get_path(path_name: str) -> Path:
    ''' Returns data folder. '''
    return get_root_path() / path_name

def get_cats(data_dir: str = '.data') -> list:
    ''' Load the list of arXiv categories. This loads cats.json if present
    and otherwise creates it using the arXiv SQLite database arxiv_data.db.
    
    INPUT
        data_dir: str = '.data'
            The data directory
    '''
    return cats_
#     import json
#     cats_path = 'cats.json'
# #     if not cats_path.is_file():
# #         from .db import ArXivDatabase
# #         db = ArXivDatabase(data_dir = data_dir)
# #         db.get_cats()
#     with open(cats_path, 'r') as f:
#         return json.load(f)

def get_mcat_dict(data_dir: str = '.data') -> list:
    ''' Load the dictionary translating between categories and master
    categories. This loads mcat_dict.json if present and otherwise creates 
    it using the arXiv SQLite database arxiv_data.db.
    
    INPUT
        data_dir: str = '.data'
            The data directory
    '''
    return mcats_
#     import json
#     mcat_dict_path = 'mcat_dict.json'
# #     if not mcat_dict_path.is_file():
# #         from .db import ArXivDatabase
# #         db = ArXivDatabase(data_dir = data_dir)
# #         db.get_mcat_dict()
#     with open(mcat_dict_path, 'r') as f:
#         return json.load(f)

def get_nrows(fname: str, data_dir: str = '.data') -> int:
    ''' Count the number of rows in a tsv file by streaming it, and thus
    without loading it into memory.
    
    INPUT
        fname: str
            The tsv file whose rows are to be counted, with file extension
        data_dir: str = '.data'
            The data directory
    '''
    import pandas as pd
    path = get_path(data_dir) / fname
    df = pd.read_csv(path, sep = '\t', usecols = [0], chunksize = 10000)
    return sum(len(x) for x in df)

def get_mcats(data_dir: str = '.data') -> list:
    ''' A convenience function that gets the list of master categories,
    by using the list of categories and the master category dictionary.
    
    INPUT
        data_dir: str = '.data'
            The data directory

    OUTPUT
        A list of master categories
    '''
    cats = get_cats(data_dir = data_dir)['id']
    mcat_dict = get_mcat_dict(data_dir = data_dir)
    duplicate_mcats = [mcat_dict[cat] for cat in cats]

    # Get unique master categories while preserving the order
    mcats = list(dict.fromkeys(duplicate_mcats).keys())

    return mcats

def get_mcat_masks(data_dir: str = '.data') -> torch.FloatTensor:
    ''' Create master category masks.
    
    INPUT
        data_dir: str = '.data'
            The data directory

    OUTPUT
        A two-dimensional torch.FloatTensor of shape (num_mcats, num_cats),
        where num_cats and num_cats are the number of master categories and
        categories, respectively. Every slice contains a mask for a given
        master category.
    '''
    cats = get_cats(data_dir = data_dir)['id']
    mcats = get_mcats(data_dir = data_dir)
    mcat_dict = get_mcat_dict(data_dir = data_dir)
    mcat2idx = {mcat: idx for idx, mcat in enumerate(mcats)}
    mcat_idxs = [mcat2idx[mcat] for mcat in mcats]
    dup_cats = torch.FloatTensor([mcat2idx[mcat_dict[cat]] for cat in cats])
    masks = torch.stack([(dup_cats == mcat_idx).float() 
        for mcat_idx in mcat_idxs])
    return masks

def apply_mask(x: torch.FloatTensor, masks: torch.FloatTensor):
    ''' Apply a mask to a tensor. 
    
    INPUT
        x: torch.FloatTensor
            A tensor of shape (*, num_cats)

    OUTPUT
        A tensor of shape (num_mcats, *, num_cats), where each slice along
        the first dimension now has as last dimension the mask for the given
        master category.
    '''
    stacked = torch.stack([x for _ in range(masks.shape[0])], dim = 0)
    return masks.unsqueeze(1) * stacked

def mix_logits(x, y):
    ''' A numerically stable version of
            1 - \sigma^{-1}([1 - \sigma(x)][1 - \sigma(y)])

        INPUT
            x: torch.FloatTensor
                A tensor containing logits
            y: torch.FloatTensor
                A tensor containing logits, of the same shape as x

        OUTPUT
            A torch.FloatTensor of the same shape as x and y, calculated as
                x + y + log(1 + exp(-x) + exp(-y))
    '''
    return x + y + torch.log(1 + torch.exp(-x) + torch.exp(-y))

def cats2mcats(pred: torch.FloatTensor, target: torch.FloatTensor, 
    masks: torch.FloatTensor = None, data_dir: str = '.data'):
    ''' Convert category logits to master category logits.
    
    INPUT
        pred: torch.FloatTensor
            A tensor containing predictions, of size 
            (seq_len, batch_size, num_cats)
        target: torch.FloatTensor
            A tensor containing true values, of size 
            (seq_len, batch_size, num_cats)
        masks: torch.FloatTensor = None
            The master category masks, defaults to computing new masks
            using the get_mcat_masks function
        data_dir: str = '.data'
            The data directory

    OUTPUT
        A pair (mpred, mtarget), both of which are torch.FloatTensor objects
        of size (seq_len, batch_size, num_mcats)
    '''
    if masks is None: masks = get_mcat_masks(data_dir = data_dir)

    shifted_logits = pred + torch.abs(torch.min(pred))
    masked_logits = apply_mask(shifted_logits, masks = masks)
    masked_logits -= torch.abs(torch.min(pred))
    sorted_logits = torch.sort(masked_logits, dim = -1)[0]
    first, second = sorted_logits[:, :, -1], sorted_logits[:, :, -2]
    mpred = mix_logits(first, second).permute(1, 0)

    masked_target = apply_mask(target, masks = masks)
    mtarget = torch.max(masked_target, dim = 2).values.permute(1, 0)
    return mpred, mtarget

def get_class_weights(dl, pbar_width: int = None, data_dir: str = '.data'):
    ''' Compute the category- and master category class weights from a dataset.

    INPUT
        dl: torch.utils.data.DataLoader
            The training dataset
        pbar_width: int = None
            The width of the progress bar. If you are using a Jupyter notebook
            then set this to ~1000
        data_dir: str = '.data'
            The data directory

    OUTPUT
        A dictionary containing
            cat_weights: torch.FloatTensor
                A one-dimensional tensor containing the category class weights
            mcat_weights: torch.FloatTensor
                A one-dimensional tensor containing the master category 
                class weights
    '''
    from tqdm.auto import tqdm
    with tqdm(desc = 'Calculating class weights', ncols = pbar_width,
        total = len(dl) * dl.batch_size) as pbar:
        counts = None
        for _, y in dl:
            if counts is None:
                counts = torch.sum(y, dim = 0) 
            else:
                counts += torch.sum(y, dim = 0)
            pbar.update(dl.batch_size)

        # Adding 1 to avoid zero division
        cat_weights = torch.max(counts) / (counts + 1)

    mcat_masks = get_mcat_masks(data_dir = data_dir)
    mcat_counts = [torch.sum(counts * mask) for mask in mcat_masks]
    mcat_counts = torch.FloatTensor(mcat_counts)

    # Adding 1 to avoid zero division
    mcat_weights = torch.max(mcat_counts) / (mcat_counts + 1)
    return {'cat_weights': cat_weights, 'mcat_weights': mcat_weights}

def boolean(input):
    ''' Convert strings 'true'/'false' into boolean True/False.

    INPUT
        input: str or bool

    OUTPUT
        A bool object which is True if input is 'true' and False 
        if input is 'false' (not case sensitive). If input is already
        of type bool then nothing happens, and if none of the above
        conditions are true then a None object is returned.
    '''
    if isinstance(input, bool): return input
    if isinstance(input, str) and input.lower() == 'true': return True
    if isinstance(input, str) and input.lower() == 'false': return False

def clean(doc: str):
    ''' Clean a document. This removes newline symbols, scare quotes,
        superfluous whitespace and replaces equations with -EQN-. 
        
    INPUT
        doc: str
            A document

    OUTPUT
        The cleaned version of the document
    '''
    import re

    # Remove newline symbols
    doc = re.sub('\n', ' ', doc)

    # Convert LaTeX equations of the form $...$, $$...$$, \[...\]
    # or \(...\) to -EQN-
    dollareqn = '(?<!\$)\${1,2}(?!\$).*?(?<!\$)\${1,2}(?!\$)'
    bracketeqn = '\\[\[\(].*?\\[\]\)]'
    eqn = f'({dollareqn}|{bracketeqn})'
    doc = re.sub(eqn, ' -EQN- ', doc)

    # Remove scare quotes, both as " and \\"
    doc = re.sub('(\\"|")', '', doc)

    # Merge multiple spaces
    doc = re.sub(r' +', ' ', doc)

    return doc.strip()


if __name__ == '__main__':
    pass
