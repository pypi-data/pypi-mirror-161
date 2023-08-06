# @copyright  Copyright (c) 2018-2020 Opscidia


import time, logging
from torch.utils.data import DataLoader
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.ERROR)


def generate_data(titles, abstracts):
    data = []
    for t, a in zip(titles, abstracts):
        data.append((t, a))

    return data




def data_loader(title_abstracts, bsz):
    start = time.process_time()
    nb = len(title_abstracts) // bsz
#     data = generate_data(titles, abstracts)
    logging.debug(f'Generate data has taken: {time.process_time() - start} sec')
    data =  DataLoader(title_abstracts, batch_size=bsz, shuffle=False)
    return data
